import os
import email
import httpx
import re
from email.header import decode_header
from imapclient import IMAPClient
from database import db
from datetime import datetime
from app.services.auth_service import get_credentials
from fastapi import HTTPException, status

from starlette.concurrency import run_in_threadpool

async def get_auth_token():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/auth/internal/token")
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to get authentication token"
                )
            return response.json()["access_token"]
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

def parse_email_message(uid: int, email_message, raw_body: str) -> dict:
    """Parse email message into schema-compliant format"""
    # Decode email fields
    subject, encoding = decode_header(email_message['Subject'])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding or 'utf-8', errors='ignore')
    
    from_, encoding = decode_header(email_message.get('From'))[0]
    if isinstance(from_, bytes):
        from_ = from_.decode(encoding or 'utf-8', errors='ignore')
    
    # Parse recipients
    to_field = email_message.get('To', '')
    if to_field:
        to_decoded, encoding = decode_header(to_field)[0]
        if isinstance(to_decoded, bytes):
            to_decoded = to_decoded.decode(encoding or 'utf-8', errors='ignore')
        recipients = [addr.strip() for addr in to_decoded.split(',')]
    else:
        recipients = []

    # Clean and process the body
    clean_body_text = clean_body(raw_body)

    return {
        'user_id': 'default',  # You should get this from authentication
        'email_id': str(uid),
        'sender': from_,
        'recipients': recipients,
        'subject': subject or '',
        'body': clean_body_text,
        'received_at': datetime.now(),
        'category': 'uncategorized',
        'is_read': False
    }

def fetch_from_imap(token: str, email_account: str):
    imap_host = 'imap.gmail.com'
    
    with IMAPClient(imap_host, use_uid=True, ssl=True) as server:
        try:
            server.oauth2_login(email_account, token)
        except Exception as e:
            print(f"IMAP Authentication Error: {e}")
            if hasattr(e, 'args') and e.args:
                print(f"Additional error info: {e.args}")
            raise

        server.select_folder('INBOX')
        messages = server.search('ALL')

        emails = []
        for uid in messages:
            raw_message = server.fetch(uid, ['RFC822'])[uid][b'RFC822']
            email_message = email.message_from_bytes(raw_message)

            # Get email body
            body = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == 'text/plain' and 'attachment' not in str(part.get('Content-Disposition')):
                        body = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='replace')
                        break
            else:
                body = email_message.get_payload(decode=True).decode(email_message.get_content_charset() or 'utf-8', errors='replace')

            # Parse into schema-compliant format
            email_data = parse_email_message(uid, email_message, body)

            # Store email in MongoDB if it doesn't exist
            existing_email = db.emails.find_one({"email_id": str(uid)})
            if not existing_email:
                db.emails.insert_one(email_data)

            emails.append(email_data)

        return emails

async def fetch_emails():
    try:
        # Check if emails exist in MongoDB first
        stored_emails = await db.emails.find().to_list(100)
        if stored_emails:
            return stored_emails

        # If MongoDB is empty, fetch from IMAP and store them
        token = await get_auth_token()
        email_account = os.getenv('EMAIL_ACCOUNT')
        if not email_account:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Email account not configured"
            )
        
        emails = await run_in_threadpool(lambda: fetch_from_imap(token, email_account))
        return emails
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch emails: {str(e)}"
        )