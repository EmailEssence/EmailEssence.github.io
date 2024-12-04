from imapclient import IMAPClient
import email
from email.header import decode_header
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

SCOPES = ['https://mail.google.com/']

def get_credentials():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

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


def summarize_emails(emails):
    summaries = []
    client = OpenAI()
    # OpenAI.api_key = os.getenv('OPENAI_API_KEY')
    
    for email in emails:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # Use a valid model
            messages=[
                {"role": "system", "content": "You are an email summarizer. You will be given an email and you will summarize it into a single sentence."},
                {"role": "user", 
                 "content": email.body}
            ]
        )
        # Extract the summary text from the message object
        message = completion.choices[0].message
        summary_text = ''

        if isinstance(message.content, list):
            # Handle the case where content is a list
            for content_piece in message.content:
                if content_piece['type'] == 'text':
                    summary_text += content_piece['text']['value']
        else:
            # Handle the case where content is a string
            summary_text = message.content

        summaries.append({
            'email_id': email.id,
            'summary': summary_text.strip()
        })

    return summaries