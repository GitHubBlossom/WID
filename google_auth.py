"""Google API authentication module."""
import os.path
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import config
import logging

logger = logging.getLogger(__name__)


def get_credentials():
    """Get or refresh Google API credentials.

    Returns:
        Credentials: Valid Google API credentials
    """
    creds = None

    # Load existing token if available
    if config.TOKEN_FILE.exists():
        try:
            with open(config.TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        except Exception as e:
            logger.warning(f"Could not load existing token: {e}")

    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            if not config.GOOGLE_CREDENTIALS_PATH.exists():
                raise FileNotFoundError(
                    f"Google credentials file not found at {config.GOOGLE_CREDENTIALS_PATH}. "
                    "Please download it from Google Cloud Console."
                )

            logger.info("Initiating OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(config.GOOGLE_CREDENTIALS_PATH),
                config.GOOGLE_SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save credentials for future use
        with open(config.TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
        logger.info("Credentials saved successfully")

    return creds


def get_gmail_service():
    """Create and return Gmail API service."""
    creds = get_credentials()
    return build('gmail', 'v1', credentials=creds)


def get_calendar_service():
    """Create and return Google Calendar API service."""
    creds = get_credentials()
    return build('calendar', 'v3', credentials=creds)


def get_drive_service():
    """Create and return Google Drive API service."""
    creds = get_credentials()
    return build('drive', 'v3', credentials=creds)


def get_docs_service():
    """Create and return Google Docs API service."""
    creds = get_credentials()
    return build('docs', 'v1', credentials=creds)


def get_sheets_service():
    """Create and return Google Sheets API service."""
    creds = get_credentials()
    return build('sheets', 'v4', credentials=creds)


def get_slides_service():
    """Create and return Google Slides API service."""
    creds = get_credentials()
    return build('slides', 'v1', credentials=creds)
