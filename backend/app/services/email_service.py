import os
import email
import httpx
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

            # Decode email fields
            subject, encoding = decode_header(email_message['Subject'])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or 'utf-8', errors='ignore')
            from_, encoding = decode_header(email_message.get('From'))[0]
            if isinstance(from_, bytes):
                from_ = from_.decode(encoding or 'utf-8', errors='ignore')

            # Get email body
            body = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get('Content-Disposition'))
                    if content_type == 'text/plain' and 'attachment' not in content_disposition:
                        body_bytes = part.get_payload(decode=True)
                        body = body_bytes.decode(part.get_content_charset() or 'utf-8', errors='replace')
                        break
            else:
                body_bytes = email_message.get_payload(decode=True)
                body = body_bytes.decode(email_message.get_content_charset() or 'utf-8', errors='replace')

            email_data = {
                'email_id': str(uid),
                'sender': from_,
                'subject': subject,
                'body': body,
                'received_at': datetime.utcnow()
            }

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