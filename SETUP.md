# Detailed Setup Guide

This guide provides step-by-step instructions for setting up the Weekly Activity Summary application.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Google Cloud Setup](#google-cloud-setup)
3. [Anthropic API Setup](#anthropic-api-setup)
4. [Application Installation](#application-installation)
5. [Configuration](#configuration)
6. [Testing](#testing)
7. [Deployment Options](#deployment-options)

## System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Python**: Version 3.8 or higher
- **Internet Connection**: Required for API access
- **Google Account**: With Gmail, Calendar, and Drive access
- **Anthropic Account**: For Claude API access

## Google Cloud Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: "Weekly Activity Summary"
4. Click "Create"

### Step 2: Enable Required APIs

1. In the Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for and enable each of these APIs:
   - **Gmail API**
     - Search "Gmail API"
     - Click on it
     - Click "Enable"
   - **Google Calendar API**
     - Search "Google Calendar API"
     - Click on it
     - Click "Enable"
   - **Google Drive API**
     - Search "Google Drive API"
     - Click on it
     - Click "Enable"

### Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" user type (unless you have a Google Workspace)
3. Click "Create"
4. Fill in the required fields:
   - **App name**: Weekly Activity Summary
   - **User support email**: Your email
   - **Developer contact email**: Your email
5. Click "Save and Continue"
6. On "Scopes" page, click "Add or Remove Scopes"
7. Add these scopes:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/calendar.readonly`
   - `https://www.googleapis.com/auth/drive.readonly`
8. Click "Update" → "Save and Continue"
9. Add test users (your email address)
10. Click "Save and Continue"

### Step 4: Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen (see Step 3)
4. Choose application type: "Desktop app"
5. Enter name: "Weekly Activity Summary Desktop"
6. Click "Create"
7. Click "Download JSON" on the popup
8. Save the file as `credentials.json` in your project directory

## Anthropic API Setup

### Step 1: Create an Anthropic Account

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Complete account verification if required

### Step 2: Generate API Key

1. In the Anthropic Console, go to "API Keys"
2. Click "Create Key"
3. Enter a name: "Weekly Activity Summary"
4. Click "Create"
5. **Important**: Copy the API key immediately - it won't be shown again
6. Store it securely

## Application Installation

### Step 1: Clone or Download the Repository

```bash
# If using git
git clone <repository-url>
cd WID

# Or download and extract the ZIP file
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

Your terminal prompt should now show `(venv)`.

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- Google API clients
- Anthropic SDK
- APScheduler
- Other required libraries

## Configuration

### Step 1: Create Configuration File

```bash
cp .env.example .env
```

> **Note:** `.env.example` is a hidden file (starts with `.`). Use `ls -a` to verify it exists.
> If you can't find it, create a new `.env` file manually and add the required settings from Step 3 below.

### Step 2: Edit Configuration

Open `.env` in your favorite text editor:

```bash
nano .env
# or
vim .env
# or use any text editor
```

### Step 3: Add Required Settings

**Minimum required configuration:**

```env
# REQUIRED: Your Anthropic API key
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx

# REQUIRED: Path to Google credentials
GOOGLE_CREDENTIALS_FILE=credentials.json
```

**Optional customization:**

```env
# Schedule Settings
SCHEDULE_DAY=sunday          # Day of week (sunday-saturday)
SCHEDULE_HOUR=18             # Hour in 24-hour format (0-23)
SCHEDULE_MINUTE=0            # Minute (0-59)

# Timezone
TIMEZONE=America/New_York    # Your local timezone
# Examples:
# - America/New_York
# - America/Los_Angeles
# - America/Chicago
# - Europe/London
# - Europe/Paris
# - Asia/Tokyo
# - Australia/Sydney

# Report Settings
LOOKBACK_DAYS=7              # How many days to look back
REPORT_OUTPUT_DIR=reports    # Where to save reports
REPORT_FORMAT=markdown       # markdown, html, or txt
```

### Step 4: Place Credentials File

Make sure `credentials.json` (downloaded from Google Cloud) is in the project directory:

```
WID/
├── credentials.json  ← This file
├── .env
├── main.py
└── ...
```

## Testing

### Step 1: Verify Installation

```bash
# Make sure you're in the virtual environment
python --version  # Should be 3.8 or higher
python -c "import anthropic; print('Anthropic SDK installed')"
```

### Step 2: Test Google Authentication

```bash
python main.py test-auth
```

This will:
1. Open a browser window
2. Ask you to select your Google account
3. Show permissions the app needs
4. Ask you to authorize

**Important**: Click "Allow" to grant permissions.

After successful authorization:
- A `token.json` file will be created
- You should see: "✅ All authentication tests passed!"

### Step 3: Test Report Generation

```bash
python main.py run-now
```

This will:
1. Collect your data from the past 7 days
2. Generate an AI summary
3. Save a report to the `reports/` directory
4. Display statistics in the console

Expected output:
```
============================================================
WEEKLY ACTIVITY REPORT GENERATED
============================================================

📧 Email Activity:
   Sent: X
   Received: Y

📅 Calendar Activity:
   Events: X
   Meetings: Y
   Meeting Hours: Z

📄 Document Activity:
   Total: X
   Docs: Y
   Sheets: Z
   Slides: W

💾 Report saved to: reports/weekly_report_2024-01-15_18-00-00.md
============================================================
```

## Deployment Options

### Option 1: Run Manually

Run the scheduler when needed:

```bash
python main.py schedule
```

Press Ctrl+C to stop.

### Option 2: Linux/macOS - systemd Service

1. Edit the service file:
   ```bash
   nano weekly-activity-summary.service
   ```

2. Update these paths:
   - `/path/to/WID` → Your actual project path
   - `youruser` → Your username

3. Install:
   ```bash
   sudo cp weekly-activity-summary.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable weekly-activity-summary
   sudo systemctl start weekly-activity-summary
   ```

4. Check status:
   ```bash
   sudo systemctl status weekly-activity-summary
   ```

### Option 3: macOS - launchd

Create `~/Library/LaunchAgents/com.user.weekly-activity-summary.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.weekly-activity-summary</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/WID/venv/bin/python</string>
        <string>/path/to/WID/main.py</string>
        <string>schedule</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/WID</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Then:
```bash
launchctl load ~/Library/LaunchAgents/com.user.weekly-activity-summary.plist
```

### Option 4: Windows - Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Name: "Weekly Activity Summary"
4. Trigger: "When the computer starts"
5. Action: "Start a program"
6. Program: `C:\path\to\WID\venv\Scripts\python.exe`
7. Arguments: `C:\path\to\WID\main.py schedule`
8. Start in: `C:\path\to\WID`

### Option 5: Docker (Advanced)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py", "schedule"]
```

Build and run:
```bash
docker build -t weekly-activity-summary .
docker run -d \
  -v $(pwd)/credentials.json:/app/credentials.json \
  -v $(pwd)/token.json:/app/token.json \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/reports:/app/reports \
  --name weekly-activity-summary \
  weekly-activity-summary
```

## Troubleshooting

### Common Issues

**Issue**: "credentials.json not found"
- **Solution**: Download credentials from Google Cloud Console and place in project directory

**Issue**: "ANTHROPIC_API_KEY not set"
- **Solution**: Add your API key to `.env` file

**Issue**: "Token has been expired or revoked"
- **Solution**: Delete `token.json` and run `python main.py test-auth` again

**Issue**: "No activity found"
- **Solution**: Check that you have Gmail/Calendar/Drive activity in the lookback period

**Issue**: Browser doesn't open for authentication
- **Solution**: Copy the URL from the terminal and paste it in your browser

## Next Steps

1. Verify the scheduler is running correctly
2. Wait for the first scheduled report (or run manually with `run-now`)
3. Check the `reports/` directory for generated reports
4. Customize the configuration as needed

## Getting Help

If you encounter issues not covered here:
1. Check the logs for error messages
2. Run with verbose mode: `python main.py -v run-now`
3. Open an issue on GitHub with:
   - Error message
   - Steps to reproduce
   - Your Python version
   - Operating system

## Security Best Practices

1. **Never commit** `credentials.json`, `token.json`, or `.env` to version control
2. **Restrict file permissions**:
   ```bash
   chmod 600 credentials.json token.json .env
   ```
3. **Regularly rotate** your API keys
4. **Review** the OAuth scopes - they're read-only for your security
5. **Monitor** the `reports/` directory for unexpected content
