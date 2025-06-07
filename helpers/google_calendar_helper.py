import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

def build_service():
    """Authenticate and return Google Calendar API service."""
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), "..", "token.pickle")
    credentials_path = os.path.join(os.path.dirname(__file__), "..", "credentials.json")

    # Load existing token
    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    # If token invalid or missing, go through OAuth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)
