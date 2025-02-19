import os
import pickle
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv
from flask import url_for

load_dotenv()

SCOPES = ['https://mail.google.com/']

def create_authorization_url():
    # Load client ID and client secret from environment variables
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

    if not client_id or not client_secret:
        raise Exception("Google API credentials not found in environment variables.")

    # Construct the client configuration
    client_config = {
        "web": {  # Changed from "installed" to "web"
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": get_redirect_uri()
        }
    }

    flow = Flow.from_client_config(client_config, SCOPES)
    flow.redirect_uri = get_redirect_uri()
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    return authorization_url, state

def get_tokens_from_code(code):
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    client_config = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": get_redirect_uri()
        }
    }

    flow = Flow.from_client_config(client_config, SCOPES)
    flow.redirect_uri = get_redirect_uri()
    
    flow.fetch_token(code=code)
    credentials = flow.credentials
    
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

def get_redirect_uri():
    environment = os.getenv('ENVIRONMENT', 'development')
    if environment == 'development':
        return 'http://localhost:8000/auth/callback'
    else:
        return 'https://ee-backend-w86t.onrender.com/auth/callback'
