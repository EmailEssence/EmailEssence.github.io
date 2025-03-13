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
    """Get a valid OAuth token for email access"""
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
    """Clean up email body content"""
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
        token (str): OAuth2 token for authentication
        email_account (str): Email account to fetch from
        limit (Optional[int]): Maximum number of emails to fetch
        since_date (Optional[datetime]): Only fetch emails received after this date
        folder (str): IMAP folder to fetch from (default: 'INBOX')
        criteria (str): IMAP search criteria (default: 'ALL')
        
    Returns:
        List[dict]: List of fetched emails in schema-compliant format
        
    Raises:
        Exception: If authentication or fetching fails
    """
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
    """Store email in Database asynchronously if it does not already exist"""
    try:
        print(f"🔍 Checking if email {uid} already exists in MongoDB...")
        existing_email = await db.emails.find_one({"email_id": str(uid)})  # ✅ Needs await

        if existing_email:
            print(f"⚠️ Email {uid} already exists, skipping insert.")
        else:
            print(f"📌 Inserting email {uid} into MongoDB...")
            result = await db.emails.insert_one(email_data)  # ✅ Needs await
            print(f"✅ Email {uid} inserted successfully with ID: {result.inserted_id}")

    except Exception as e:
        print(f"❌ Error inserting email {uid} into MongoDB: {e}")

async def get_emails_from_db():
        stored_emails = await db.emails.find().to_list(100)
        if stored_emails:
            print(f"✅ Returning {len(stored_emails)} stored emails from MongoDB")
            return stored_emails


async def fetch_emails():
    try:
        # Fetch 1 email from imap
        # compare with 1st email in db
        # if not equal, fetch next n emails
        # stored_emails=get_emails_from_db()
        # if(stored_emails):
        #     latest_email = await db.emails.find_one(sort=[("_id", -1)])

            
        stored_emails = await db.emails.find().to_list(100)
        if stored_emails:
            return stored_emails    
                        
        # Get token using the auth service
        token = await get_auth_token()  # This now uses the auth_service properly
        email_account = os.getenv('EMAIL_ACCOUNT')
        if not email_account:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Email account not configured"
            )

        # Run fetch_from_imap() in a threadpool (since it's sync)
        emails = await run_in_threadpool(
            fetch_from_imap, 
            token, 
            email_account
        )

        # Insert emails asynchronously into MongoDB
        for email_data in emails:
            await save_email_to_db(email_data, email_data["email_id"])

        return emails

    except Exception as e:
        service_logger.exception("Email fetch operation failed")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))