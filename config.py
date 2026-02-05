"""Configuration management for Weekly Activity Summary application."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Google API Configuration
GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
GOOGLE_CREDENTIALS_PATH = BASE_DIR / GOOGLE_CREDENTIALS_FILE
TOKEN_FILE = BASE_DIR / 'token.json'

# Google API Scopes
GOOGLE_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/drive.readonly',
]

# Anthropic API Configuration
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')

# Scheduler Configuration
SCHEDULE_DAY = os.getenv('SCHEDULE_DAY', 'sunday').lower()
SCHEDULE_HOUR = int(os.getenv('SCHEDULE_HOUR', '18'))
SCHEDULE_MINUTE = int(os.getenv('SCHEDULE_MINUTE', '0'))
TIMEZONE = os.getenv('TIMEZONE', 'America/New_York')

# Report Configuration
REPORT_OUTPUT_DIR = BASE_DIR / os.getenv('REPORT_OUTPUT_DIR', 'reports')
REPORT_FORMAT = os.getenv('REPORT_FORMAT', 'markdown').lower()
LOOKBACK_DAYS = int(os.getenv('LOOKBACK_DAYS', '7'))

# Email Configuration (optional)
SEND_EMAIL = os.getenv('SEND_EMAIL', 'false').lower() == 'true'
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL', '')

# Ensure reports directory exists
REPORT_OUTPUT_DIR.mkdir(exist_ok=True)
