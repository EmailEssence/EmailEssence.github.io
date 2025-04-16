"""
Email service for handling email-related operations.
"""

import logging
import os
import email
from typing import List, Optional, Dict, Any, Tuple
import httpx
import re
from email.header import decode_header
from imapclient import IMAPClient
from datetime import datetime
from google.auth.transport.requests import Request
from app.services import auth_service
from fastapi import HTTPException, status
from bson.objectid import ObjectId
from starlette.concurrency import run_in_threadpool

from app.models import EmailSchema, ReaderViewResponse, UserSchema
from app.services.database.email_repository import EmailRepository
from app.services.database.factories import get_email_repository, get_user_service, get_auth_service
from app.services.database.connection import instance
from app.services.user_service import UserService

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

class EmailService:
    """
    Service for handling all email-related operations.
    
    This class provides a unified interface for email fetching, parsing,
    processing, and storage operations.
    """
    
    def __init__(self, email_repository: EmailRepository = None):
        """
        Initialize the email service.
        
        Args:
            email_repository: Email repository instance
        """
        self.email_repository = email_repository or get_email_repository()
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
        """Clean up email body content."""
        body = re.sub(r'\[image:[^\]]*\]', '', body)
        body = re.sub(r'(\r\n|\r|\n)+', '\n', body)
        body = body.strip()
        return body

    def _decode_email_field(self, field_value: Optional[str], default: str = '') -> str:
        """Safely decode email header fields with proper encoding handling."""
        if not field_value:
            return default
        
        decoded, encoding = decode_header(field_value)[0]
        if isinstance(decoded, bytes):
            decoded = decoded.decode(encoding or 'utf-8', errors='ignore')
        return decoded

    def _extract_email_body(self, email_message: email.message.Message) -> str:
        """Extract email body with fallback content type handling."""
        body = ""
        content_type_preference = ['text/plain', 'text/html']
        
        def decode_part(part):
            try:
                charset = part.get_content_charset() or 'utf-8'
                return part.get_payload(decode=True).decode(charset, errors='replace')
            except Exception as e:
                logger.error(f"Error decoding {part.get_content_type()} part: {e}")
                return ""
        
        if email_message.is_multipart():
            for preferred_type in content_type_preference:
                for part in email_message.walk():
                    if (part.get_content_type() == preferred_type and 
                        'attachment' not in str(part.get('Content-Disposition'))):
                        content = decode_part(part)
                        if content:
                            body = content
                            is_html = preferred_type == 'text/html'
                            return self._clean_body(body, is_html)
        else:
            body = decode_part(email_message)
            
        return self._clean_body(body)

    def _parse_email_message(self, uid: int, email_message: email.message.Message, 
                           body: str, received_date: datetime, google_id: str = 'default') -> dict:
        """Parse email message into schema-compliant format."""
        subject = self._decode_email_field(email_message.get('Subject'))
        from_ = self._decode_email_field(email_message.get('From'))
        
        to_field = self._decode_email_field(email_message.get('To'))
        recipients = [addr.strip() for addr in to_field.split(',')] if to_field else []

        return {
            'google_id': google_id,
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
                             google_id: str = 'default', 
                             limit: Optional[int] = None,
                             since_date: Optional[datetime] = None, 
                             folder: str = 'INBOX', 
                             criteria: str = 'ALL') -> List[dict]:
        """Fetch emails from IMAP server"""
        return await run_in_threadpool(
            lambda: self._fetch_from_imap_sync(
                token, email_account, google_id, limit, since_date, folder, criteria
            )
        )
    
    def _fetch_from_imap_sync(self, token: str, email_account: str,
                            google_id: str = 'default', limit: Optional[int] = None,
                            since_date: Optional[datetime] = None, 
                            folder: str = 'INBOX', criteria: str = 'ALL') -> List[dict]:
        """Synchronous implementation of IMAP fetching"""
        with IMAPClient(self.imap_host, use_uid=True, ssl=True) as server:
            try:
                server.oauth2_login(email_account, token)
            except Exception as e:
                logger.error(f"IMAP Authentication Error: {e}")
                if hasattr(e, 'args') and e.args:
                    logger.error(f"Additional error info: {e.args}")
                raise

            server.select_folder(folder)

            search_criteria = [criteria]
            if since_date:
                date_str = since_date.strftime('%d-%b-%Y')
                search_criteria.extend(['SINCE', date_str])        

            messages = server.search(search_criteria)

            if limit:
                messages = messages[-limit:]

            emails = []
            
            for uid in messages:
                try:
                    fetch_data = server.fetch(uid, ['RFC822', 'INTERNALDATE'])
                    raw_message = fetch_data[uid][b'RFC822']
                    received_date = fetch_data[uid][b'INTERNALDATE']
                    
                    email_message = email.message_from_bytes(raw_message)
                    body = self._extract_email_body(email_message)
                    
                    email_data = self._parse_email_message(
                        uid=uid,
                        email_message=email_message,
                        body=body,
                        received_date=received_date,
                        google_id=google_id
                    )
                    
                    emails.append(email_data)
                    
                except Exception as e:
                    logger.error(f"Error processing email {uid}: {e}")
                    continue

            return emails

    # -------------------------------------------------------------------------
    # Database Operations
    # -------------------------------------------------------------------------
    
    async def save_email_to_db(self, email_data: dict) -> None:
        """Store email in database if not exists"""
        try:
            # Ensure email_id is string and use it directly
            email_id = str(email_data["email_id"])
            existing_email = await self.email_repository.find_by_id(email_id, email_data["google_id"])
            if not existing_email:
                # If email_data is already an EmailSchema instance, use it directly
                if isinstance(email_data, EmailSchema):
                    await self.email_repository.insert_one(email_data)
                else:
                    # Otherwise create a new EmailSchema instance
                    email = EmailSchema(**email_data)
                    await self.email_repository.insert_one(email)
                logger.info(f"Email {email_id} inserted successfully")
        except Exception as e:
            logger.error(f"Error saving email {email_data['email_id']}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_emails_from_db(self, google_id: str, query: Dict = None, 
                                skip: int = 0, limit: int = 100,
                                sort_by: str = "received_at", 
                                sort_order: str = "desc") -> List[EmailSchema]:
        """Get emails from database with filtering options."""
        try:
            sort_direction = -1 if sort_order == "desc" else 1
            filter_query = query or {}
            filter_query["google_id"] = google_id
            
            results = await self.email_repository.find_many(
                filter_query,
                limit=limit,
                sort=[(sort_by, sort_direction)],
                skip=skip
            )
            return [result if isinstance(result, EmailSchema) else EmailSchema(**result) for result in results]
        except Exception as e:
            logger.exception(f"Failed to retrieve emails from database for user {google_id}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_email(self, email_id: str, google_id: str) -> Optional[EmailSchema]:
        """
        Get an email by IMAP UID.
        
        Args:
            email_id: IMAP UID of the email
            google_id: Google ID of the user
            
        Returns:
            Optional[EmailSchema]: Email if found, None otherwise
        """
        try:
            email_data = await self.email_repository.find_by_id(str(email_id), google_id)
            if not email_data:
                return None
            # If email_data is already an EmailSchema instance, return it directly
            if isinstance(email_data, EmailSchema):
                return email_data
            # Otherwise create a new EmailSchema instance
            return EmailSchema(**email_data)
        except Exception as e:
            logger.error(f"Failed to get email: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get email"
            )

    async def mark_email_as_read(self, email_id: str, google_id: str) -> Optional[EmailSchema]:
        """Mark an email as read."""
        try:
            email_id = str(email_id)
            email_data = await self.email_repository.find_by_id(email_id, google_id)
            if not email_data or email_data["google_id"] != google_id:
                logger.warning(f"Email {email_id} not found for user {google_id}")
                return None
                
            email_data["is_read"] = True
            await self.email_repository.update_by_id(email_id, google_id, email_data)
            # If email_data is already an EmailSchema instance, return it directly
            if isinstance(email_data, EmailSchema):
                return email_data
            # Otherwise create a new EmailSchema instance
            return EmailSchema(**email_data)
        except Exception as e:
            logger.exception(f"Failed to mark email {email_id} as read for user {google_id}")
            raise HTTPException(status_code=500, detail=str(e))
        
    async def delete_email(self, email_id: str, google_id: str) -> bool:
        """
        Delete an email.
        
        Args:
            email_id: IMAP UID of the email
            google_id: Google ID of the user
            
        Returns:
            bool: True if deletion successful
        """
        try:
            return await self.email_repository.delete_by_id(str(email_id), google_id)
        except Exception as e:
            logger.error(f"Failed to delete email: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete email"
            )
    
    # -------------------------------------------------------------------------
    # Content Processing Methods
    # -------------------------------------------------------------------------
    
    async def get_email_reader_view(self, email_id: str, google_id: str) -> Optional[ReaderViewResponse]:
        """Process an email to generate a reader-view friendly version."""
        try:
            email = await self.get_email(email_id, google_id)
            if not email:
                return None
                
            body = email.body
            is_html = bool(re.search(r'<(?:html|body|div|p|h[1-6])[^>]*>', body, re.IGNORECASE))
            original_length = len(body)
            
            if is_html:
                cleaned_body = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL)
                cleaned_body = re.sub(r'<style[^>]*>.*?</style>', '', cleaned_body, flags=re.DOTALL)
                
                for tag in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'br']:
                    pattern = f'</{tag}>'
                    cleaned_body = re.sub(pattern, f'</{tag}>\n\n', cleaned_body, flags=re.IGNORECASE)
                
                cleaned_body = re.sub(r'<a[^>]*href=[\'"]([^\'"]*)[\'"][^>]*>(.*?)</a>', 
                                    r'\2 [\1]', cleaned_body, flags=re.DOTALL)
                cleaned_body = re.sub(r'<[^>]+>', ' ', cleaned_body)
                
                import html
                cleaned_body = html.unescape(cleaned_body)
                content_type = "html"
            else:
                cleaned_body = body
                cleaned_body = re.sub(r'(\r\n|\r|\n){2,}', '\n\n', cleaned_body)
                content_type = "plain"
                
            reader_content = re.sub(r' {2,}', ' ', cleaned_body)
            reader_content = re.sub(r'\n{3,}', '\n\n', reader_content)
            reader_content = reader_content.strip()
            
            return ReaderViewResponse.from_email(
                email=email,
                reader_content=reader_content,
                content_type=content_type,
                is_processed=True,
                original_length=original_length,
                processed_length=len(reader_content)
            )
            
        except Exception as e:
            logger.exception(f"Failed to generate reader view for email {email_id} for user {google_id}")
            raise HTTPException(status_code=500, detail=str(e))
        
    # -------------------------------------------------------------------------
    # Public API Methods
    # -------------------------------------------------------------------------
    
    async def fetch_emails(self, google_id: str, skip: int = 0, limit: int = 20,
                          unread_only: bool = False, category: Optional[str] = None,
                          search: Optional[str] = None, sort_by: str = "received_at",
                          sort_order: str = "desc", refresh: bool = False) -> Tuple[List[EmailSchema], int, Dict[str, Any]]:
        """Main email fetching function that combines IMAP and database operations."""
        try:
            debug_info = {"db_query": {}, "timing": {}, "source": "database", "google_id": google_id}
            
            if refresh:
                await self._refresh_emails_from_imap(google_id, debug_info)
            
            query = self._build_email_query(google_id, unread_only, category, search)
            debug_info["db_query"] = query
            
            sort_direction = -1 if sort_order == "desc" else 1
            
            start_time = datetime.now()
            total = await self.email_repository.count_documents(query)
            debug_info["timing"]["count_query"] = (datetime.now() - start_time).total_seconds()
            
            start_time = datetime.now()
            emails = await self.email_repository.find_many(
                query,
                limit=limit,
                skip=skip,
                sort=[(sort_by, sort_direction)]
            )
            debug_info["timing"]["main_query"] = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Retrieved {len(emails)} emails out of {total} total for user {google_id}")
            return emails, total, debug_info
            
        except Exception as e:
            logger.exception(f"Email fetch operation failed for user {google_id}")
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _refresh_emails_from_imap(self, google_id: str, debug_info: Dict[str, Any]) -> None:
        """Internal method to refresh emails from IMAP"""
        debug_info["source"] = "imap+database"
        debug_info["timing"]["imap_fetch_start"] = datetime.now().isoformat()
        
        start_time = datetime.now()
        try:
            # Get user service instance using factory
            user_service = get_user_service()
            auth_service = get_auth_service()
            
            # Get user by google_id
            user = await user_service.get_user(google_id)
            if not user:
                logger.error(f"User {google_id} not found in database during IMAP refresh")
                debug_info["imap_error"] = f"User {google_id} not found"
                return
                
            user_email = user.email
            if not user_email:
                logger.error(f"Email address not found for user {google_id}")
                debug_info["imap_error"] = "User email not found"
                return
            
            logger.info(f"Fetching emails for {user_email}")
            
            # Get token using google_id
            token_data = await auth_service.get_token_data(google_id)
            if not token_data:
                logger.error(f"No token found for user {google_id}")
                debug_info["imap_error"] = "No token found for user"
                return
            
            logger.info(f"Fetching emails from IMAP for {user_email}")
            imap_emails = await self.fetch_from_imap(
                token=token_data.token,
                email_account=user_email,
                google_id=google_id,
                limit=50
            )
            
            logger.info(f"Retrieved {len(imap_emails)} emails from IMAP for {user_email}")
            
            for email_data in imap_emails:
                email_data["google_id"] = google_id
                await self.save_email_to_db(email_data)
            
            debug_info["imap_fetch_count"] = len(imap_emails)
            logger.info(f"Saved {len(imap_emails)} emails to database for {user_email}")
            
        except Exception as e:
            logger.exception(f"IMAP fetch failed for user {google_id}: {str(e)}")
            debug_info["imap_error"] = str(e)
            
        finally:
            debug_info["timing"]["imap_fetch_duration"] = (datetime.now() - start_time).total_seconds()
    
    def _build_email_query(self, google_id: str, unread_only: bool, category: Optional[str], 
                          search: Optional[str]) -> Dict[str, Any]:
        """Build query filter for emails"""
        query = {"google_id": google_id}
        
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