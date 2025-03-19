import logging
import os
import email
from typing import List, Optional, Dict, Any
from typing import List, Optional
import httpx
import re
from email.header import decode_header
from imapclient import IMAPClient
from database import db
from datetime import datetime
from google.auth.transport.requests import Request
from app.services import auth_service
from fastapi import HTTPException, status, Query
from bson.objectid import ObjectId

from starlette.concurrency import run_in_threadpool

from app.models import EmailSchema, ReaderViewResponse

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create module-specific logger
logger = logging.getLogger(__name__)

class EmailService:
    """
    Service for handling all email-related operations.
    
    This class provides a unified interface for email fetching, parsing,
    processing, and storage operations.
    """
    
    def __init__(self):
        """Initialize the email service with required configuration"""
        self.imap_host = 'imap.gmail.com'
        self.default_email_account = os.environ.get("EMAIL_ACCOUNT")
        
    # -------------------------------------------------------------------------
    # Authentication Methods
    # -------------------------------------------------------------------------
    
    async def get_auth_token(self) -> str:
        """
        Get a valid OAuth token for email access.
        
        Returns:
            str: Valid OAuth token
            
        Raises:
            HTTPException: If token retrieval fails
        """
        try:
            credentials = await run_in_threadpool(auth_service.get_credentials)
            if not credentials.valid:
                if credentials.expired and credentials.refresh_token:
                    await run_in_threadpool(lambda: credentials.refresh(Request()))
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token expired and cannot be refreshed. User needs to re-authenticate."
                    )
            return credentials.token
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token retrieval failed: {str(e)}"
            )
    
    # -------------------------------------------------------------------------
    # Email Parsing Methods
    # -------------------------------------------------------------------------
    
    def _clean_body(self, body: str, is_html: bool = False) -> str:
        """
        Clean up email body content.
        
        Args:
            body: Raw email body text
            is_html: Whether the content is from HTML
            
        Returns:
            str: Cleaned email body
        """
        # Remove image tags
        body = re.sub(r'\[image:[^\]]*\]', '', body)
        
        # Replace multiple newlines with single newline
        body = re.sub(r'(\r\n|\r|\n)+', '\n', body)
        
        # Remove trailing/leading whitespace
        body = body.strip()
        
        return body

    def _decode_email_field(self, field_value: Optional[str], default: str = '') -> str:
        """
        Safely decode email header fields with proper encoding handling.
        
        Args:
            field_value: Raw header field value
            default: Default value if field is None
            
        Returns:
            str: Decoded field value
        """
        if not field_value:
            return default
        
        decoded, encoding = decode_header(field_value)[0]
        if isinstance(decoded, bytes):
            decoded = decoded.decode(encoding or 'utf-8', errors='ignore')
        return decoded

    def _extract_email_body(self, email_message: email.message.Message) -> str:
        """
        Extract email body with fallback content type handling.
        
        Args:
            email_message: Email message object
            
        Returns:
            str: Extracted and decoded email body
        """
        body = ""
        content_type_preference = ['text/plain', 'text/html']
        
        def decode_part(part):
            """Helper to decode a message part with proper error handling"""
            try:
                charset = part.get_content_charset() or 'utf-8'
                return part.get_payload(decode=True).decode(charset, errors='replace')
            except Exception as e:
                logger.error(f"Error decoding {part.get_content_type()} part: {e}")
                return ""
        
        if email_message.is_multipart():
            # Try each content type in order of preference
            for preferred_type in content_type_preference:
                for part in email_message.walk():
                    if (part.get_content_type() == preferred_type and 
                        'attachment' not in str(part.get('Content-Disposition'))):
                        content = decode_part(part)
                        if content:
                            body = content
                            # Flag if we're using HTML content
                            is_html = preferred_type == 'text/html'
                            return self._clean_body(body, is_html)
        else:
            body = decode_part(email_message)
            
        return self._clean_body(body)

    def _parse_email_message(self, uid: int, email_message: email.message.Message, 
                           body: str, received_date: datetime, user_id: str = 'default') -> dict:
        """
        Parse email message into schema-compliant format.
        
        Args:
            uid: Email UID
            email_message: Email message object
            body: Extracted email body
            received_date: Server-provided received date
            user_id: User ID for the email owner
            
        Returns:
            dict: Parsed email data matching EmailSchema
        """
        # Decode header fields
        subject = self._decode_email_field(email_message.get('Subject'))
        from_ = self._decode_email_field(email_message.get('From'))
        
        # Parse recipients
        to_field = self._decode_email_field(email_message.get('To'))
        recipients = [addr.strip() for addr in to_field.split(',')] if to_field else []

        return {
            'user_id': user_id,
            'email_id': str(uid),
            'sender': from_,
            'recipients': recipients,
            'subject': subject,
            'body': body,
            'received_at': received_date,
            'category': 'uncategorized',
            'is_read': False
        }

    # -------------------------------------------------------------------------
    # IMAP Connection Methods
    # -------------------------------------------------------------------------
    
    async def fetch_from_imap(self, token: str, email_account: str,
                             user_id: str = 'default', limit: Optional[int] = None,
                             since_date: Optional[datetime] = None, 
                             folder: str = 'INBOX', criteria: str = 'ALL') -> List[dict]:
        """Fetch emails from IMAP server"""
        return await run_in_threadpool(
            lambda: self._fetch_from_imap_sync(
                token, email_account, user_id, limit, since_date, folder, criteria
            )
        )
    
    def _fetch_from_imap_sync(self, token: str, email_account: str,
                            user_id: str = 'default', limit: Optional[int] = None,
                            since_date: Optional[datetime] = None, 
                            folder: str = 'INBOX', criteria: str = 'ALL') -> List[dict]:
        """Synchronous implementation of IMAP fetching"""
        # TODO: Add support for multiple folders/labels beyond just INBOX
        # TODO: Implement connection pooling to reduce connection overhead
        # TODO: Move print to logging for consistent log management
        
        with IMAPClient(self.imap_host, use_uid=True, ssl=True) as server:
            try:
                server.oauth2_login(email_account, token)
            except Exception as e:
                print(f"IMAP Authentication Error: {e}")
                if hasattr(e, 'args') and e.args:
                    print(f"Additional error info: {e.args}")
                raise

            server.select_folder(folder)

            # Build search criteria
            search_criteria = [criteria]
            if since_date:
                # Convert to IMAP date format and add to criteria
                date_str = since_date.strftime('%d-%b-%Y')
                search_criteria.extend(['SINCE', date_str])        

            messages = server.search(search_criteria)

            # Apply limit if specified
            if limit:
                messages = messages[-limit:] # up to limit

            emails = []
            
            for uid in messages:
                try:
                    # Fetch both RFC822 and INTERNALDATE
                    fetch_data = server.fetch(uid, ['RFC822', 'INTERNALDATE'])
                    raw_message = fetch_data[uid][b'RFC822']
                    received_date = fetch_data[uid][b'INTERNALDATE']
                    
                    email_message = email.message_from_bytes(raw_message)
                    
                    # Extract and clean body
                    body = self._extract_email_body(email_message)
                    
                    # Parse into schema-compliant format
                    email_data = self._parse_email_message(
                        uid=uid,
                        email_message=email_message,
                        body=body,
                        received_date=received_date,
                        user_id=user_id
                    )
                    
                    emails.append(email_data)
                    
                except Exception as e:
                    print(f"Error processing email {uid}: {e}")
                    continue

            return emails

    # -------------------------------------------------------------------------
    # Database Operations
    # -------------------------------------------------------------------------
    
    async def save_email_to_db(self, email_data: dict, uid: str) -> None:
        """Store email in database if not exists"""
        # TODO: Move print to logging for consistent log management
        try:
            print(f"🔍 Checking if email {uid} already exists in MongoDB...")
            existing_email = await db.emails.find_one({"email_id": str(uid), "user_id": email_data["user_id"]})

            if existing_email:
                print(f"⚠️ Email {uid} already exists, skipping insert.")
            else:
                print(f"📌 Inserting email {uid} into MongoDB...")
                result = await db.emails.insert_one(email_data)
                print(f"✅ Email {uid} inserted successfully with ID: {result.inserted_id}")

        except Exception as e:
            print(f"❌ Error inserting email {uid} into MongoDB: {e}")

    async def get_emails_from_db(self, user_id: str, query: Dict = None, 
                                skip: int = 0, limit: int = 100,
                                sort_by: str = "received_at", 
                                sort_order: str = "desc") -> List[dict]:
        """
        Get emails from database with filtering options.
        
        Args:
            user_id: ID of the user to get emails for
            query: Filter query to apply
            skip: Number of records to skip
            limit: Maximum number of records to return
            sort_by: Field to sort by
            sort_order: Sort direction ("asc" or "desc")
            
        Returns:
            List[dict]: List of emails from database
        """
        try:
            # Determine sort direction
            sort_direction = -1 if sort_order == "desc" else 1
            
            # Use provided query or empty dict and ensure user_id is included
            filter_query = query or {}
            filter_query["user_id"] = user_id
            
            # Fetch emails with pagination and sorting
            stored_emails = await db.emails.find(filter_query) \
                .sort([(sort_by, sort_direction)]) \
                .skip(skip) \
                .limit(limit) \
                .to_list(length=limit)
            
            if stored_emails:
                logger.info(f"Retrieved {len(stored_emails)} emails from database for user {user_id}")
            return stored_emails
        except Exception as e:
            logger.exception(f"Failed to retrieve emails from database for user {user_id}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_email(self, email_id: str, user_id: str) -> Optional[dict]:
        """
        Fetch a single email by ID.
        
        Args:
            email_id: Unique email identifier
            user_id: ID of the email owner
            
        Returns:
            dict: Email data or None if not found
            
        Raises:
            HTTPException: If database operation fails
        """
        # TODO: Add fallback to IMAP if email not found in database
        # TODO: Implement conflict resolution for emails modified in both places
        
        try:
            email = await db.emails.find_one({"email_id": email_id, "user_id": user_id})
            
            if not email:
                logger.warning(f"Email {email_id} not found for user {user_id}")
                return None
                
            return email
        except Exception as e:
            logger.exception(f"Failed to fetch email {email_id} for user {user_id}")
            raise HTTPException(status_code=500, detail=str(e))
            
    async def mark_email_as_read(self, email_id: str, user_id: str) -> Optional[dict]:
        """
        Mark an email as read.
        
        Args:
            email_id: Unique email identifier
            user_id: ID of the email owner
            
        Returns:
            dict: Updated email or None if not found
            
        Raises:
            HTTPException: If update operation fails
        """
        try:
            result = await db.emails.update_one(
                {"email_id": email_id, "user_id": user_id},
                {"$set": {"is_read": True}}
            )
            
            if result.matched_count == 0:
                logger.warning(f"Email {email_id} not found for user {user_id} during mark as read")
                return None
                
            return await db.emails.find_one({"email_id": email_id, "user_id": user_id})
        except Exception as e:
            logger.exception(f"Failed to mark email {email_id} as read for user {user_id}")
            raise HTTPException(status_code=500, detail=str(e))
        
    async def delete_email(self, email_id: str, user_id: str) -> bool:
        """
        Delete an email.
        
        Args:
            email_id: Unique email identifier
            user_id: ID of the email owner
            
        Returns:
            bool: True if deleted, False if not found
            
        Raises:
            HTTPException: If delete operation fails
        """
        try:
            result = await db.emails.delete_one({"email_id": email_id, "user_id": user_id})
            
            if result.deleted_count == 0:
                logger.warning(f"Email {email_id} not found for user {user_id} during delete")
                
            return result.deleted_count > 0
        except Exception as e:
            logger.exception(f"Failed to delete email {email_id} for user {user_id}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # -------------------------------------------------------------------------
    # Content Processing Methods
    # -------------------------------------------------------------------------
    
    async def get_email_reader_view(self, email_id: str, user_id: str) -> Optional[ReaderViewResponse]:
        """
        Process an email to generate a reader-view friendly version.
        
        Args:
            email_id: Unique email ID
            user_id: ID of the email owner
            
        Returns:
            ReaderViewResponse: Reader-view content with metadata
        """
        try:
            # Retrieve the email
            email_dict = await db.emails.find_one({"email_id": email_id, "user_id": user_id})
            
            if not email_dict:
                logger.warning(f"Email {email_id} not found for user {user_id} during reader view generation")
                return None
                
            # Convert dictionary to EmailSchema
            from app.models import EmailSchema, ReaderViewResponse
            email = EmailSchema(**email_dict)
                
            # Get the email body
            body = email.body
            
            # Check if content is likely HTML with more precise detection
            is_html = bool(re.search(r'<(?:html|body|div|p|h[1-6])[^>]*>', body, re.IGNORECASE))
            
            # Record original length
            original_length = len(body)
            
            # Process based on content type
            if is_html:
                # HTML processing
                logger.debug(f"Processing HTML content for email {email_id}")
                
                # Remove script and style elements first
                cleaned_body = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL)
                cleaned_body = re.sub(r'<style[^>]*>.*?</style>', '', cleaned_body, flags=re.DOTALL)
                
                # Replace common block elements with newlines
                for tag in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'br']:
                    pattern = f'</{tag}>'
                    cleaned_body = re.sub(pattern, f'</{tag}>\n\n', cleaned_body, flags=re.IGNORECASE)
                
                # Replace links with their text content plus the URL
                cleaned_body = re.sub(r'<a[^>]*href=[\'"]([^\'"]*)[\'"][^>]*>(.*?)</a>', 
                                    r'\2 [\1]', cleaned_body, flags=re.DOTALL)
                
                # Remove all remaining HTML tags
                cleaned_body = re.sub(r'<[^>]+>', ' ', cleaned_body)
                
                # Decode HTML entities
                import html
                cleaned_body = html.unescape(cleaned_body)
                
                content_type = "html"
            else:
                # Plain text processing
                logger.debug(f"Processing plain text content for email {email_id}")
                cleaned_body = body
                
                # Preserve paragraph structure in plain text
                cleaned_body = re.sub(r'(\r\n|\r|\n){2,}', '\n\n', cleaned_body)
                
                content_type = "plain"
                
            # Clean up whitespace for both types
            reader_content = re.sub(r' {2,}', ' ', cleaned_body)
            reader_content = re.sub(r'\n{3,}', '\n\n', reader_content)
            reader_content = reader_content.strip()
            
            # Use the factory method to create the response
            return ReaderViewResponse.from_email(
                email=email,
                reader_content=reader_content,
                content_type=content_type,
                is_processed=True,
                original_length=original_length,
                processed_length=len(reader_content)
            )
            
        except Exception as e:
            logger.exception(f"Failed to generate reader view for email {email_id} for user {user_id}")
            raise HTTPException(status_code=500, detail=str(e))
        
    # -------------------------------------------------------------------------
    # Public API Methods
    # -------------------------------------------------------------------------
    
    async def fetch_emails(self, user_id: str, skip: int = 0, limit: int = 20,
                          unread_only: bool = False, category: Optional[str] = None,
                          search: Optional[str] = None, sort_by: str = "received_at",
                          sort_order: str = "desc", refresh: bool = False) -> tuple:
        """
        Main email fetching function that combines IMAP and database operations.
        
        Args:
            user_id: ID of the current user
            skip: Number of emails to skip
            limit: Maximum number of emails to return
            unread_only: Filter for unread emails only
            category: Filter by email category
            search: Search in subject and body
            sort_by: Field to sort by
            sort_order: Sort direction ("asc" or "desc")
            refresh: Whether to refresh emails from IMAP first (default: False)
            
        Returns:
            tuple: (emails list, total count, debug info)
        """
        try:
            debug_info = {"db_query": {}, "timing": {}, "source": "database", "user_id": user_id}
            
            # If refresh requested, fetch from IMAP first
            if refresh:
                await self._refresh_emails_from_imap(user_id, debug_info)
            
            # Build database query
            query = self._build_email_query(user_id, unread_only, category, search)
            debug_info["db_query"] = query
            
            # Determine sort direction
            sort_direction = -1 if sort_order == "desc" else 1
            
            # Get total count
            start_time = datetime.now()
            total = await db.emails.count_documents(query)
            debug_info["timing"]["count_query"] = (datetime.now() - start_time).total_seconds()
            
            # Get emails with pagination
            start_time = datetime.now()
            emails = await db.emails.find(query).sort([(sort_by, sort_direction)]).skip(skip).limit(limit).to_list(length=limit)
            debug_info["timing"]["main_query"] = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Retrieved {len(emails)} emails out of {total} total for user {user_id}")
            return emails, total, debug_info
            
        except Exception as e:
            logger.exception(f"Email fetch operation failed for user {user_id}")
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _refresh_emails_from_imap(self, user_id: str, debug_info: Dict[str, Any]) -> None:
        """
        Internal method to refresh emails from IMAP
        
        Args:
            user_id: ID of the current user
            debug_info: Dictionary to store debug information
        """
        debug_info["source"] = "imap+database"
        debug_info["timing"]["imap_fetch_start"] = datetime.now().isoformat()
        
        start_time = datetime.now()
        try:
            # Get user email account from user ID
            logger.debug(f"Refreshing emails from IMAP for user ID: {user_id}")
            
            # Try different strategies to find the user
            user = None
            
            # First try: treating user_id as an ObjectId (MongoDB's _id)
            try:
                if ObjectId.is_valid(user_id):
                    user = await db.users.find_one({"_id": ObjectId(user_id)})
                    if user:
                        logger.debug(f"Found user by ObjectId: {user.get('email')}")
            except Exception as e:
                logger.debug(f"Error finding user by ObjectId: {str(e)}")
            
            # Second try: use google_id
            if not user:
                user = await db.users.find_one({"google_id": user_id})
                if user:
                    logger.debug(f"Found user by google_id: {user.get('email')}")
            
            # If still not found, try email lookup as a last resort
            if not user and '@' in user_id:
                user = await db.users.find_one({"email": user_id})
                if user:
                    logger.debug(f"Found user by email: {user.get('email')}")
            
            if not user:
                logger.error(f"User {user_id} not found in database during IMAP refresh")
                debug_info["imap_error"] = f"User {user_id} not found"
                return
                
            # Extract user email
            user_email = user.get("email")
            if not user_email:
                logger.error(f"Email address not found for user {user_id}")
                debug_info["imap_error"] = "User email not found"
                return
            
            logger.info(f"Fetching emails for {user_email}")
            
            # Get OAuth token for the specific user
            token_record = await db.tokens.find_one({"user_email": user_email})
            if not token_record:
                # Attempt to get token from user's oauth field
                oauth_data = user.get("oauth")
                if oauth_data and oauth_data.get("token"):
                    token = oauth_data.get("token")
                    logger.info(f"Using token from user's oauth data for {user_email}")
                else:
                    logger.error(f"No token found for user {user_id} with email {user_email}")
                    debug_info["imap_error"] = "No token found for user"
                    return
            else:
                token = token_record.get("token")
                if not token:
                    logger.error(f"Invalid token for user {user_id}")
                    debug_info["imap_error"] = "Invalid token"
                    return
            
            # Normalize user_id to string for storage
            normalized_user_id = str(user.get("_id", user_id))
            
            # Fetch emails
            logger.info(f"Fetching emails from IMAP for {user_email}")
            imap_emails = await self.fetch_from_imap(
                token=token,
                email_account=user_email,
                user_id=normalized_user_id,  # Use the normalized user ID
                limit=50  # Fetch last 50 emails
            )
            
            logger.info(f"Retrieved {len(imap_emails)} emails from IMAP for {user_email}")
            
            # Save fetched emails
            for email_data in imap_emails:
                # Ensure the email is associated with this user
                email_data["user_id"] = normalized_user_id
                await self.save_email_to_db(email_data, email_data["email_id"])
            
            debug_info["imap_fetch_count"] = len(imap_emails)
            logger.info(f"Saved {len(imap_emails)} emails to database for {user_email}")
            
        except Exception as e:
            logger.exception(f"IMAP fetch failed for user {user_id}: {str(e)}")
            debug_info["imap_error"] = str(e)
            
        finally:
            debug_info["timing"]["imap_fetch_duration"] = (datetime.now() - start_time).total_seconds()
    
    def _build_email_query(self, user_id: str, unread_only: bool, category: Optional[str], 
                          search: Optional[str]) -> Dict[str, Any]:
        """
        Build query filter for emails
        
        Args:
            user_id: ID of the current user
            unread_only: Filter for unread emails only
            category: Filter by email category
            search: Search in subject and body
            
        Returns:
            Dict[str, Any]: Query filter
        """
        # Always include user_id in the query
        query = {"user_id": user_id}
        
        if unread_only:
            query["is_read"] = False
            
        if category:
            query["category"] = category
            
        if search:
            search_regex = {"$regex": search, "$options": "i"}
            query["$or"] = [
                {"subject": search_regex},
                {"body": search_regex},
                {"sender": search_regex}
            ]
            
        return query