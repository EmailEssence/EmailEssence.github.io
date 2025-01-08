
import os
import email
from email.header import decode_header
from imapclient import IMAPClient



# TODO decouple the auth from the email service
from backend.app.services.auth_service import get_credentials

def fetch_emails():
    creds = get_credentials()
    EMAIL_ACCOUNT = os.getenv('EMAIL_ACCOUNT')
    access_token = creds.token

    imap_host = 'imap.gmail.com'

    with IMAPClient(imap_host, use_uid=True, ssl=True) as server:
        try:
            # Use the oauth2_login method provided by IMAPClient
            server.oauth2_login(EMAIL_ACCOUNT, access_token)
        except Exception as e:
            print(f"IMAP Authentication Error: {e}")
            # If the exception has more details
            if hasattr(e, 'args') and e.args:
                print(f"Additional error info: {e.args}")
            raise

        # Select the INBOX folder
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

            emails.append({
                'id': uid,
                'from': from_,
                'subject': subject,
                'body': body
            })

    return emails

# def extract_email_body(email):