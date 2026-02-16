# Productivity Analyzer

An intelligent web application that automatically generates productivity summaries by analyzing your Gmail, Google Calendar, and Google Drive activity. Powered by AI (Anthropic Claude) to provide insightful summaries of your work.

## Features

- **🌐 Web Interface**: Easy-to-use web dashboard for configuration and viewing summaries
- **⚙️ Simple Setup**: Configure OAuth credentials and settings via web page
- **▶️ On-Demand Analysis**: Click "Run" button to generate summaries for any period (yesterday or custom)
- **📊 Weekly History**: View past summaries grouped by calendar week
- **⏰ Automated Scheduling**: Optionally runs on your chosen day/time (e.g., Sunday evenings)
- **📧 Email Summaries**: Automatically sends nice-looking email summaries
- **🤖 AI-Powered**: Uses Claude to categorize work and identify potential to-dos
- **📧 Email Analysis**: Tracks sent and received emails, identifies top contacts
- **📅 Calendar Insights**: Summarizes meetings, calculates time spent, tracks attendees
- **📄 Document Tracking**: Monitors Google Docs, Sheets, and Slides activity

## Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- A Google account
- An Anthropic API key

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd WID

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Google API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Gmail API
   - Google Calendar API
   - Google Drive API
4. Create OAuth 2.0 credentials:
   - Go to "Credentials" → "Create Credentials" → "OAuth client ID"
   - Choose "Desktop app" as the application type
   - Download the credentials file
5. Save the credentials file as `credentials.json` in the project directory

### 4. Anthropic API Setup

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create an API key
3. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```
4. Add your Anthropic API key to `.env`:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

### 5. Configuration

Create a `.env` file in the project directory:

```env
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional - these can be configured via the web interface
FLASK_SECRET_KEY=change-this-to-something-random
```

### 6. Start the Application

```bash
python app.py
```

The web application will start on `http://localhost:5555`

## Usage

### First-Time Setup

1. **Start the app**: `python app.py`
2. **Access the web interface**: Open `http://localhost:5555` in your browser
3. **Setup OAuth**: You'll be redirected to the setup page
   - Place your `credentials.json` file in the project directory
   - The app will guide you through Google OAuth authentication
4. **Configure Settings**:
   - Choose your timezone
   - Set when you want weekly summaries to run (e.g., Sunday at 6 PM)
   - Set how many days to analyze (default: 1 = yesterday)
   - Enable/disable automatic email summaries

### Generating Summaries

**Manual (On-Demand):**
- Click the **"Run Analysis Now"** button on the dashboard
- Or use **"Run Custom Period"** to analyze a different number of days

**Automatic (Scheduled):**
- Configure your preferred schedule in Settings
- The app runs in the background and generates summaries automatically
- If enabled, sends email summaries automatically

### Viewing History

- All generated summaries appear on the dashboard
- Summaries are grouped by calendar week
- Click "View" to see the full summary report

### CLI Usage (Alternative)

For command-line usage without the web interface, you can use:

```bash
# Generate a report immediately
python main.py run-now

# Start the scheduler (blocking)
python main.py schedule

# Test Google authentication
python main.py test-auth
```

## Report Output

Reports are saved to the `reports/` directory with timestamps:

- `reports/weekly_report_2024-01-15_18-00-00.md` (Markdown)
- `reports/weekly_report_2024-01-15_18-00-00.html` (HTML)
- `reports/weekly_report_2024-01-15_18-00-00.txt` (Plain text)

### Example Report Structure

```markdown
# Weekly Activity Report

**Generated:** January 15, 2024 at 06:00 PM
**Period:** Past 7 days

---

## Executive Summary

[AI-generated insights about your week]

---

## Activity Statistics

### Email
- Sent: **45**
- Received: **203**

### Calendar
- Total Events: **23**
- Meetings: **18**
- Meeting Hours: **12.5**

### Documents
- Total: **15**
- Created: **3**
- Modified: **12**
```

## Customization

All customization is done through the web interface:

1. Go to **Settings** in the navigation menu
2. Adjust:
   - **Timezone**: Your local timezone
   - **Schedule Day**: Which day to run automatic summaries
   - **Schedule Time**: Hour and minute for automatic runs
   - **Lookback Days**: How many days to analyze (1 = yesterday, 7 = past week)
   - **Auto Email**: Enable/disable automatic email summaries
3. Click **Save Settings**

Settings are saved to `data/settings.json` and persist across restarts.

## Troubleshooting

### "Google credentials file not found"

Make sure you have downloaded `credentials.json` from Google Cloud Console and placed it in the project directory.

### "ANTHROPIC_API_KEY not set"

Add your Anthropic API key to the `.env` file:
```env
ANTHROPIC_API_KEY=sk-ant-...
```

### "Permission denied" errors

Make sure you have authorized the application with all required scopes. Delete `token.json` and run `python main.py test-auth` again.

### No emails/events/documents found

Check that:
1. You have activity in the lookback period
2. The timezone is set correctly in `.env`
3. Your Google account has the relevant data

## Project Structure

```
WID/
├── app.py                   # Flask web application
├── email_sender.py          # Email sending via Gmail API
├── report_generator.py      # Report orchestration
├── activity_summarizer.py   # AI summarization
├── gmail_collector.py       # Gmail data collection
├── calendar_collector.py    # Calendar data collection
├── drive_collector.py       # Drive/Docs data collection
├── google_auth.py           # Google API authentication
├── config.py                # Configuration management
├── scheduler.py             # Scheduling logic (CLI)
├── main.py                  # CLI entry point
├── templates/               # Web UI templates
│   ├── base.html           # Base template
│   ├── dashboard.html      # Dashboard page
│   ├── setup.html          # Setup/settings page
│   └── summary.html        # Summary view page
├── data/                    # Generated data
│   ├── settings.json       # User settings
│   └── summaries/          # Generated summaries
├── reports/                 # Generated reports
├── requirements.txt         # Python dependencies
├── .env                    # Configuration (API keys)
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Security & Privacy

- **Local Storage**: All credentials are stored locally in `credentials.json` and `token.json`
- **Read-Only Access**: The application only requests read-only access to your data
- **No Data Storage**: No data is sent to external servers (except Anthropic for summarization)
- **AI Processing**: Only summary data is sent to Anthropic's API, not full email/document content

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

[Add your license here]

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Acknowledgments

- Built with Google APIs for Gmail, Calendar, and Drive
- Powered by Anthropic's Claude AI for intelligent summarization
- Scheduled with APScheduler
