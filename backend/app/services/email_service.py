import logging
import os
import email
from typing import List, Optional
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

from starlette.concurrency import run_in_threadpool

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create module-specific logger
logger = logging.getLogger(__name__)


async def get_auth_token():
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
    
def clean_body(body: str) -> str:
    """
    Clean up email body content.
    
    Args:
        body: Raw email body text
        
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

def decode_email_field(field_value: Optional[str], default: str = '') -> str:
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

def extract_email_body(email_message: email.message.Message) -> str:
    """
    Extract email body with fallback content type handling.
    
    Args:
        email_message: Email message object
        
    Returns:
        str: Extracted and decoded email body
    """
    body = ""
    if email_message.is_multipart():
        # plaintext body
        for part in email_message.walk():
            if (part.get_content_type() == 'text/plain' and 
                'attachment' not in str(part.get('Content-Disposition'))):
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    body = part.get_payload(decode=True).decode(charset, errors='replace')
                    break
                except Exception as e:
                    print(f"Error decoding text/plain part: {e}")
                    continue
        # If no text/plain, try text/html
        if not body:
            for part in email_message.walk():
                if (part.get_content_type() == 'text/html' and 
                    'attachment' not in str(part.get('Content-Disposition'))):
                    try:
                        charset = part.get_content_charset() or 'utf-8'
                        body = part.get_payload(decode=True).decode(charset, errors='replace')
                        break
                    except Exception as e:
                        print(f"Error decoding text/html part: {e}")
                        continue
    else:
        try:
            charset = email_message.get_content_charset() or 'utf-8'
            body = email_message.get_payload(decode=True).decode(charset, errors='replace')
        except Exception as e:
            print(f"Error decoding non-multipart message: {e}")
            body = ""
            
    return clean_body(body)


def parse_email_message(
    uid: int,
    email_message: email.message.Message,
    body: str,
    received_date: datetime,
    user_id: str = 'default'
) -> dict:
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
    subject = decode_email_field(email_message.get('Subject'))
    from_ = decode_email_field(email_message.get('From'))
    
    # Parse recipients
    to_field = decode_email_field(email_message.get('To'))
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

def fetch_from_imap(
    token: str,
    email_account: str,
    user_id: str = 'default',
    limit: Optional[int] = None,
    since_date: Optional[datetime] = None,
    folder: str = 'INBOX',
    criteria: str = 'ALL'
) -> List[dict]:
    """
    Fetch emails from an IMAP server with support for pagination and date filtering.
    
    Args:
        token: OAuth2 token for authentication
        email_account: Email account to fetch from
        user_id: User ID for the email owner
        limit: Maximum number of emails to fetch
        since_date: Only fetch emails received after this date
        folder: IMAP folder to fetch from
        criteria: IMAP search criteria
        
    Returns:
        List[dict]: List of fetched emails in schema-compliant format
        
    Raises:
        Exception: If authentication or fetching fails
    """
    # TODO: Add support for multiple folders/labels beyond just INBOX
    # TODO: Implement connection pooling to reduce connection overhead
    # TODO: Move print to logging for consistent log management
    
    imap_host = 'imap.gmail.com'
    with IMAPClient(imap_host, use_uid=True, ssl=True) as server:
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
                body = extract_email_body(email_message)
                
                # Parse into schema-compliant format
                email_data = parse_email_message(
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

async def save_email_to_db(email_data, uid):
    """
    Store email in Database asynchronously if it does not already exist.
    
    Args:
        email_data: Processed email data dictionary
        uid: Email unique identifier
        
    Returns:
        None
    """
    # TODO: Move print to logging for consistent log management
    try:
        print(f"🔍 Checking if email {uid} already exists in MongoDB...")
        existing_email = await db.emails.find_one({"email_id": str(uid)})

        if existing_email:
            print(f"⚠️ Email {uid} already exists, skipping insert.")
        else:
            print(f"📌 Inserting email {uid} into MongoDB...")
            result = await db.emails.insert_one(email_data)
            print(f"✅ Email {uid} inserted successfully with ID: {result.inserted_id}")

    except Exception as e:
        print(f"❌ Error inserting email {uid} into MongoDB: {e}")

async def get_emails_from_db():
    """
    Retrieve emails from database.
    
    Returns:
        List[dict]: List of emails from database
    """
    # TODO: Move print to logging for consistent log management
    stored_emails = await db.emails.find().to_list(100)
    if stored_emails:
        print(f"✅ Returning {len(stored_emails)} stored emails from MongoDB")
        return stored_emails


async def fetch_emails(
    skip: int = 0,
    limit: int = 20,
    unread_only: bool = False,
    category: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "received_at",
    sort_order: str = "desc",
    refresh: bool = False
):
    """
    Main email fetching function that combines IMAP and database operations.
    
    Args:
        skip: Number of emails to skip (pagination)
        limit: Maximum number of emails to return
        unread_only: Filter to only unread emails
        category: Filter by email category
        search: Search term for filtering emails
        sort_by: Field to sort by
        sort_order: Sort direction ("asc" or "desc")
        refresh: Whether to refresh emails from IMAP first
        
    Returns:
        tuple: (emails list, total count, debug info)
        
    Raises:
        HTTPException: If operation fails
    """
    # TODO: Implement incremental sync using last sync timestamp instead of fetching last 50
    # TODO: Add background task option for async refresh without blocking the request
    
    try:
        debug_info = {
            "db_query": {},
            "timing": {},
            "source": "database"
        }
        
        # Start timing
        start_time = datetime.now()
        
        # If refresh is requested, fetch new emails from IMAP first
        if refresh:
            debug_info["source"] = "imap+database"
            debug_info["timing"]["imap_fetch_start"] = datetime.now().isoformat()
            
            try:
                # Get OAuth token
                token = await get_auth_token()
                
                # Use environment variable or config for email account
                # TODO: Utilize user management for email account once implemented
                email_account = os.environ.get("EMAIL_ACCOUNT")
                if not email_account:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="EMAIL_ACCOUNT environment variable not set"
                    )
                
                # Fetch last 50 emails from IMAP (adjust as needed)
                imap_emails = await run_in_threadpool(
                    lambda: fetch_from_imap(
                        token=token,
                        email_account=email_account,
                        limit=50,  # Fetch last 50 emails
                        folder="INBOX"
                    )
                )
                
                # Save fetched emails to database
                for email_data in imap_emails:
                    await save_email_to_db(email_data, email_data["email_id"])
                
                debug_info["imap_fetch_count"] = len(imap_emails)
                debug_info["timing"]["imap_fetch_duration"] = (datetime.now() - start_time).total_seconds()
                
            except Exception as e:
                logger.error(f"IMAP fetch failed: {str(e)}")
                debug_info["imap_error"] = str(e)
        
        # Reset timer for database operations
        start_time = datetime.now()
        
        # Build query filter
        query = {}
        
        if unread_only:
            query["is_read"] = False
            
        if category:
            query["category"] = category
            
        if search:
            # Search in subject and body fields
            search_regex = {"$regex": search, "$options": "i"}
            query["$or"] = [
                {"subject": search_regex},
                {"body": search_regex},
                {"sender": search_regex}
            ]
        
        debug_info["db_query"] = query
        
        # Determine sort direction
        sort_direction = -1 if sort_order == "desc" else 1
        
        # Get total count first
        total = await db.emails.count_documents(query)
        debug_info["timing"]["count_query"] = (datetime.now() - start_time).total_seconds()
        
        # Reset timer for main query
        start_time = datetime.now()
        
        # Fetch emails with pagination and sorting in one chained operation
        emails = await db.emails.find(query).sort([(sort_by, sort_direction)]).skip(skip).limit(limit).to_list(length=limit)
        debug_info["timing"]["main_query"] = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Retrieved {len(emails)} emails out of {total} total")
        
        return emails, total, debug_info

    except Exception as e:
        logger.exception("Email fetch operation failed")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

async def fetch_email(email_id: str):
    """
    Fetch a single email by ID.
    
    Args:
        email_id: Unique email identifier
        
    Returns:
        dict: Email data or None if not found
        
    Raises:
        HTTPException: If database operation fails
    """
    # TODO: Add fallback to IMAP if email not found in database
    # TODO: Implement conflict resolution for emails modified in both places
    
    try:
        email = await db.emails.find_one({"email_id": email_id})
        return email
    except Exception as e:
        logger.exception(f"Failed to fetch email {email_id}")
        raise HTTPException(status_code=500, detail=str(e))

async def insert_email(email_data):
    """
    Insert a new email into the database.
    
    Args:
        email_data: Email data object (Pydantic model)
        
    Returns:
        dict: Inserted email with database ID
        
    Raises:
        HTTPException: If insert operation fails
    """
    try:
        result = await db.emails.insert_one(email_data.dict())
        # Return the inserted email with _id
        return await db.emails.find_one({"_id": result.inserted_id})
    except Exception as e:
        logger.exception("Failed to insert email")
        raise HTTPException(status_code=500, detail=str(e))

async def mark_email_as_read(email_id: str):
    """
    Mark an email as read.
    
    Args:
        email_id: Unique email identifier
        
    Returns:
        dict: Updated email or None if not found
        
    Raises:
        HTTPException: If update operation fails
    """
    try:
        result = await db.emails.update_one(
            {"email_id": email_id},
            {"$set": {"is_read": True}}
        )
        
        if result.matched_count == 0:
            return None
            
        return await db.emails.find_one({"email_id": email_id})
    except Exception as e:
        logger.exception(f"Failed to mark email {email_id} as read")
        raise HTTPException(status_code=500, detail=str(e))

async def delete_email(email_id: str):
    """
    Delete an email.
    
    Args:
        email_id: Unique email identifier
        
    Returns:
        bool: True if deleted, False if not found
        
    Raises:
        HTTPException: If delete operation fails
    """
    try:
        result = await db.emails.delete_one({"email_id": email_id})
        return result.deleted_count > 0
    except Exception as e:
        logger.exception(f"Failed to delete email {email_id}")
        raise HTTPException(status_code=500, detail=str(e))