"""
Email service for handling email-related operations.
"""

import logging
import os
import email
from typing import List, Optional, Dict, Any, Tuple, Union
import re
from email.header import decode_header
from imapclient import IMAPClient
from datetime import datetime
from google.auth.transport.requests import Request
from fastapi import HTTPException, status
from starlette.concurrency import run_in_threadpool

# Import from app modules
from app.models import EmailSchema, ReaderViewResponse
from app.services.database import EmailRepository, get_email_repository
from app.services.database.factories import get_user_service, get_auth_service
from app.services import auth_service

# Configure logging
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
    # Helper Methods
    # -------------------------------------------------------------------------
    
    def _ensure_email_schema(self, email_data: Union[dict, EmailSchema]) -> EmailSchema:
        """Ensure the input is an EmailSchema instance."""
        if isinstance(email_data, EmailSchema):
            return email_data
        return EmailSchema(**email_data)
    
    def _handle_email_error(self, error: Exception, operation: str, email_id: str = None, google_id: str = None) -> None:
        """Standardize error handling for email operations."""
        error_msg = f"Failed to {operation}"
        if email_id:
            error_msg += f" email {email_id}"
        if google_id:
            error_msg += f" for user {google_id}"
        logger.exception(f"{error_msg}: {str(error)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
    
    def _get_imap_connection(self, token: str, email_account: str) -> IMAPClient:
        """Create and authenticate IMAP connection."""
        server = IMAPClient(self.imap_host, use_uid=True, ssl=True)
        try:
            server.oauth2_login(email_account, token)
            return server
        except Exception as e:
            logger.error(f"IMAP Authentication Error: {e}")
            if hasattr(e, 'args') and e.args:
                logger.error(f"Additional error info: {e.args}")
            raise
    
    def _log_operation(self, level: str, message: str, **kwargs) -> None:
        """Standardize logging across the service."""
        log_method = getattr(logger, level.lower())
        log_method(message, **kwargs)
    
    def _build_search_query(self, search: str) -> Dict[str, Any]:
        """Build search query component."""
        if not search:
            return {}
        search_regex = {"$regex": search, "$options": "i"}
        return {
            "$or": [
                {"subject": search_regex},
                {"body": search_regex},
                {"sender": search_regex}
            ]
        }
    
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
    
    # Deprecated: This method is no longer used
    # TODO: Remove this method after we're happy with the new sanitization methods
    def _clean_body(self, body: str, is_html: bool = False) -> str:
        """Clean up email body content."""
        body = re.sub(r'\[image:[^\]]*\]', '', body)
        body = re.sub(r'(\r\n|\r|\n)+', '\n', body)
        body = body.strip()
        return body

    # -------------------------------------------------------------------------
    # Email Security & Privacy Methods
    # -------------------------------------------------------------------------
    
    def _remove_scripts(self, html_content: str) -> str:
        """Remove script tags and their contents for security."""
        # Remove script tags and their contents
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
        
        # Remove on* event handlers (onclick, onload, etc.)
        html_content = re.sub(r'(<[^>]*) on\w+="[^"]*"([^>]*>)', r'\1\2', html_content)
        html_content = re.sub(r'(<[^>]*) on\w+=\'[^\']*\'([^>]*>)', r'\1\2', html_content)
        
        # Remove javascript: URLs
        html_content = re.sub(r'(<[^>]*\s+(?:href|src|action)=[\'\"])javascript:.*?([\'\"][^>]*>)', 
                              r'\1#\2', html_content, flags=re.IGNORECASE|re.DOTALL)
        
        # TODO: Research and add more event handlers to the list based on current trends
        return html_content
    
    def _remove_tracking_pixels(self, html_content: str) -> str:
        """Remove tracking pixels while preserving normal images."""
        # Remove 1x1 pixel images (common tracking pixels)
        html_content = re.sub(r'<img[^>]*(?:width=["\']?1["\']?[^>]*height=["\']?1["\']?|'
                            r'height=["\']?1["\']?[^>]*width=["\']?1["\']?)[^>]*>', 
                            '', html_content, flags=re.IGNORECASE)
        
        # Remove images from common tracking domains
        # TODO: Research and add more tracking domains to the list
        tracking_domains = [
            r'track\.', r'pixel\.', r'analytics\.', r'beacon\.', 
            r'tracker\.', r'metrics\.', r'telemetry\.', r'logger\.'
        ]
        for domain in tracking_domains:
            html_content = re.sub(
                fr'<img[^>]*src=["\']https?://[^"\']*{domain}[^"\']*["\'][^>]*>', 
                '', html_content, flags=re.IGNORECASE
            )
        
        return html_content
    
    def _minimal_email_sanitization(self, html_content: str) -> str:
        """
        Minimally sanitize email content while preserving formatting.
        Removes scripts and tracking elements but maintains styles and layout.
        """
        if not html_content:
            return html_content
            
        # First remove scripts for security
        html_content = self._remove_scripts(html_content)
        
        # Then remove tracking pixels
        html_content = self._remove_tracking_pixels(html_content)
        
        return html_content
    
    def _full_email_sanitization(self, html_content: str) -> str:
        """
        More aggressive cleaning for reader view.
        Removes tracking pixels, scripts, styles and other formatting to focus on content.
        """
        if not html_content:
            return html_content
            
        # Start with minimal sanitization
        html_content = self._minimal_email_sanitization(html_content)
        
        # Additionally remove style tags for reader view
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)
        
        # Remove inline styles
        html_content = re.sub(r'(<[^>]*) style=["\'][^"\']*["\']([^>]*>)', r'\1\2', html_content)
        
        return html_content

    def _decode_email_field(self, field_value: Optional[str], default: str = '') -> str:
        """Safely decode email header fields with proper encoding handling."""
        if not field_value:
            return default
        
        decoded, encoding = decode_header(field_value)[0]
        if isinstance(decoded, bytes):
            decoded = decoded.decode(encoding or 'utf-8', errors='ignore')
        return decoded

    def _extract_email_body(self, email_message: email.message.Message) -> Tuple[str, bool]:
        """
        Extract body content from email message and determine if it's HTML.
        
        Args:
            email_message: The email message to extract body from
            
        Returns:
            Tuple containing (body_content, is_html_flag)
        """
        # Default values
        body = ""
        is_html = False
        html_part = None
        text_part = None
        
        # Check if the message is multipart
        if email_message.is_multipart():
            # First pass: identify all content parts
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                
                # Skip attachments
                if "attachment" in content_disposition:
                    continue
                    
                # Find HTML content
                if content_type == "text/html":
                    html_part = part
                    
                # Find plain text content
                if content_type == "text/plain":
                    text_part = part
            
            # Prefer HTML content when available
            if html_part:
                try:
                    body = html_part.get_payload(decode=True).decode(errors="replace")
                    is_html = True
                except Exception as e:
                    self._log_operation('error', f"Error decoding HTML part: {e}")
                    # Fall back to text part if available
                    if text_part:
                        body = text_part.get_payload(decode=True).decode(errors="replace")
            elif text_part:
                # Use plain text if no HTML is found
                body = text_part.get_payload(decode=True).decode(errors="replace")
        else:
            # Not multipart - get content type and decode accordingly
            content_type = email_message.get_content_type()
            try:
                body = email_message.get_payload(decode=True).decode(errors="replace")
                is_html = content_type == "text/html"
            except Exception as e:
                self._log_operation('error', f"Error decoding non-multipart message: {e}")
                body = email_message.get_payload(decode=False)
                # Try to detect HTML if content-type wasn't reliable
                is_html = bool(re.search(r'<(?:html|body|div|p|h[1-6])[^>]*>', body, re.IGNORECASE))
        
        # Validate HTML detection with regex if needed
        if is_html and not bool(re.search(r'<(?:html|body|div|p|h[1-6])[^>]*>', body, re.IGNORECASE)):
            self._log_operation('warning', "Content marked as HTML but no HTML tags found, validating...")
            is_html = False  # Reset if no HTML tags found
        
        # Apply minimal sanitization for HTML content
        if is_html:
            body = self._minimal_email_sanitization(body)
        
        return body, is_html

    def _parse_email_message(self, uid: int, email_message: email.message.Message, 
                           google_id: str = 'default') -> dict:
        """Parse email message into schema-compliant format."""
        # Extract body content and determine if it's HTML
        body, is_html = self._extract_email_body(email_message)
        
        # Minimally sanitize HTML content if present
        if is_html:
            body = self._minimal_email_sanitization(body)
        
        # Process headers
        subject = self._decode_email_field(email_message.get('Subject'))
        from_ = self._decode_email_field(email_message.get('From'))
        
        to_field = self._decode_email_field(email_message.get('To'))
        recipients = [addr.strip() for addr in to_field.split(',')] if to_field else []
        
        # Get received date
        received_date = email_message.get('Date')
        if received_date:
            try:
                # Try to parse the date from the header
                import email.utils
                received_date = email.utils.parsedate_to_datetime(received_date)
            except Exception:
                # Fall back to current time if parsing fails
                received_date = datetime.now()
        else:
            received_date = datetime.now()

        return {
            'google_id': google_id,
            'email_id': str(uid),
            'sender': from_,
            'recipients': recipients,
            'subject': subject,
            'body': body,
            'is_html': is_html, # TODO: Remove this field or add to the schema? Leaning towards keeping it to communicate the type of body content
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
        with self._get_imap_connection(token, email_account) as server:
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
                        google_id=google_id
                    )
                    
                    emails.append(email_data)
                    
                except Exception as e:
                    self._log_operation('error', f"Error processing email {uid}: {e}")
                    continue

            return emails

    # -------------------------------------------------------------------------
    # Database Operations
    # -------------------------------------------------------------------------
    
    async def save_email_to_db(self, email_data: dict) -> None:
        """Store email in database if not exists"""
        try:
            email_id = str(email_data["email_id"])
            existing_email = await self.email_repository.find_by_email_and_google_id(email_id, email_data["google_id"])
            if not existing_email:
                email_schema = self._ensure_email_schema(email_data)
                await self.email_repository.insert_one(email_schema)
                self._log_operation('info', f"Email {email_id} inserted successfully")
        except Exception as e:
            self._handle_email_error(e, "save", email_data.get("email_id"), email_data.get("google_id"))

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
            return [self._ensure_email_schema(result) for result in results]
        except Exception as e:
            self._handle_email_error(e, "retrieve", None, google_id)

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
            email_data = await self.email_repository.find_by_email_and_google_id(str(email_id), google_id)
            if not email_data:
                return None
            return self._ensure_email_schema(email_data)
        except Exception as e:
            self._handle_email_error(e, "get", email_id, google_id)

    async def mark_email_as_read(self, email_id: str, google_id: str) -> Optional[EmailSchema]:
        """Mark an email as read."""
        try:
            email_id = str(email_id)
            email_data = await self.email_repository.find_by_email_and_google_id(email_id, google_id)
            if not email_data or email_data["google_id"] != google_id:
                self._log_operation('warning', f"Email {email_id} not found for user {google_id}")
                return None
                
            email_data["is_read"] = True
            # TODO: SMTP update? 
            await self.email_repository.update_by_email_and_google_id(email_id, google_id, email_data)
            return self._ensure_email_schema(email_data)
        except Exception as e:
            self._handle_email_error(e, "mark as read", email_id, google_id)
        
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
            self._handle_email_error(e, "delete", email_id, google_id)
    
    # -------------------------------------------------------------------------
    # Content Processing Methods
    # -------------------------------------------------------------------------
    
    def _convert_html_to_readable_text(self, html_content: str) -> str:
        """Convert HTML to readable plain text, optimized for reader view."""
        # First apply full sanitization
        html_content = self._full_email_sanitization(html_content)
        
        # Add newlines after block elements to improve readability
        block_elements = ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'tr', 'section', 'article']
        for tag in block_elements:
            pattern = f'</{tag}>'
            html_content = re.sub(pattern, f'</{tag}>\n\n', html_content, flags=re.IGNORECASE)
        
        # Handle list items with bullets
        html_content = re.sub(r'<li[^>]*>', '• ', html_content, flags=re.IGNORECASE)
        
        # Handle headings with emphasis
        for i in range(1, 7):
            html_content = re.sub(f'<h{i}[^>]*>(.*?)</h{i}>', 
                                 lambda m: f"\n\n{m.group(1).upper()}\n\n", 
                                 html_content, flags=re.IGNORECASE|re.DOTALL)
        
        # Remove all remaining HTML tags
        html_content = re.sub(r'<[^>]+>', ' ', html_content)
        
        # Unescape HTML entities
        import html
        html_content = html.unescape(html_content)
        
        # Clean up whitespace
        html_content = re.sub(r' {2,}', ' ', html_content)
        html_content = re.sub(r'\n{3,}', '\n\n', html_content)
        
        # Strip out email headers that we display separately
        html_content = re.sub(r'(?i)(-+\s*Forwarded message\s*-+\s*)?'
                             r'From:.*?(?=To:|Subject:|Date:|$).*?\n', '', html_content)
        html_content = re.sub(r'(?i)Date:\s*.*?\n', '', html_content)
        html_content = re.sub(r'(?i)To:\s*.*?\n', '', html_content)
        html_content = re.sub(r'(?i)Subject:\s*.*?\n', '', html_content)
        html_content = re.sub(r'(?i)Cc:\s*.*?\n', '', html_content)
        
        # Remove any remaining forwarded message markers
        html_content = re.sub(r'(?i)(-+\s*Forwarded message\s*-+\s*)', '', html_content)
        
        # Clean up excessive whitespace after header removal
        html_content = re.sub(r'\n{3,}', '\n\n', html_content)
        
        # Format sections divided by separator lines
        html_content = re.sub(r'([_\-=]{3,})\s*', '\n\n----------\n\n', html_content)
        
        # Add spacing around links and URLs
        html_content = re.sub(r'(https?://\S+)', r'\n\1\n', html_content)
        
        # Add spacing around list items for better readability
        html_content = re.sub(r'(•\s+.*?)(\n•\s+)', r'\1\n\2', html_content)
        
        # Normalize paragraph spacing (ensure double newlines between paragraphs)
        # Readerview is destroying this.
        html_content = re.sub(r'([^\n])\n([^\n])', r'\1\n\n\2', html_content)
        
        # Clean up any excessive newlines again
        html_content = re.sub(r'\n{3,}', '\n\n', html_content)
        
        return html_content.strip()
        
    def _clean_plaintext_for_reading(self, text: str) -> str:
        """Clean plain text content for better readability."""
        # Normalize newlines
        text = re.sub(r'(\r\n|\r|\n){2,}', '\n\n', text)
        
        # Clean up whitespace
        text = re.sub(r' {2,}', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    async def get_email_reader_view(self, email_id: str, google_id: str) -> Optional[ReaderViewResponse]:
        """Process an email to generate a reader-view friendly version."""
        try:
            email = await self.get_email(email_id, google_id)
            if not email:
                return None
                
            body = email.body
            original_length = len(body)
            
            # Determine if content is HTML based on content
            is_html = getattr(email, 'is_html', False)
            if not is_html:
                # Fallback detection if is_html attribute doesn't exist
                is_html = bool(re.search(r'<(?:html|body|div|p|h[1-6])[^>]*>', body, re.IGNORECASE))
            
            if is_html:
                reader_content = self._convert_html_to_readable_text(body)
                content_type = "html"
            else:
                reader_content = self._clean_plaintext_for_reading(body)
                content_type = "plain"
            
            return ReaderViewResponse.from_email(
                email=email,
                reader_content=reader_content,
                content_type=content_type,
                is_processed=True,
                original_length=original_length,
                processed_length=len(reader_content)
            )
            
        except Exception as e:
            self._handle_email_error(e, "generate reader view for", email_id, google_id)
        
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
            
            self._log_operation('info', f"Retrieved {len(emails)} emails out of {total} total for user {google_id}")
            return emails, total, debug_info
            
        except Exception as e:
            self._handle_email_error(e, "fetch", None, google_id)
    
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
                self._log_operation('error', f"User {google_id} not found in database during IMAP refresh")
                debug_info["imap_error"] = f"User {google_id} not found"
                return
                
            user_email = user.email
            if not user_email:
                self._log_operation('error', f"Email address not found for user {google_id}")
                debug_info["imap_error"] = "User email not found"
                return
            
            self._log_operation('info', f"Fetching emails for {user_email}")
            
            # Get token using google_id
            token_data = await auth_service.get_token_data(google_id)
            if not token_data:
                self._log_operation('error', f"No token found for user {google_id}")
                debug_info["imap_error"] = "No token found for user"
                return
            
            self._log_operation('info', f"Fetching emails from IMAP for {user_email}")
            imap_emails = await self.fetch_from_imap(
                token=token_data.token,
                email_account=user_email,
                google_id=google_id,
                limit=50
            )
            
            self._log_operation('info', f"Retrieved {len(imap_emails)} emails from IMAP for {user_email}")
            
            for email_data in imap_emails:
                email_data["google_id"] = google_id
                await self.save_email_to_db(email_data)
            
            debug_info["imap_fetch_count"] = len(imap_emails)
            self._log_operation('info', f"Saved {len(imap_emails)} emails to database for {user_email}")
            
        except Exception as e:
            self._log_operation('exception', f"IMAP fetch failed for user {google_id}: {str(e)}")
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
            query.update(self._build_search_query(search))
            
        return query