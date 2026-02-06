# Weekly Activity Summary

An intelligent application that automatically generates comprehensive weekly activity reports by analyzing your Gmail, Google Calendar, and Google Drive activity. Powered by AI (Anthropic Claude) to provide insightful summaries of your work.

## Features

- **📧 Email Analysis**: Tracks sent and received emails, identifies top contacts
- **📅 Calendar Insights**: Summarizes meetings, calculates time spent, tracks attendees
- **📄 Document Tracking**: Monitors Google Docs, Sheets, and Slides activity
- **🤖 AI-Powered Summaries**: Uses Claude to generate meaningful insights
- **⏰ Automated Scheduling**: Runs automatically every Sunday at 6 PM (configurable)
- **📊 Multiple Formats**: Export reports as Markdown, HTML, or plain text

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
3. Create your `.env` configuration file by copying the example template:
   ```bash
   cp .env.example .env
   ```
   > **Note:** `.env.example` is a hidden file (starts with `.`). Use `ls -a` to see it.
   > If you still can't find it, create `.env` manually with the content below.

4. Add your Anthropic API key to `.env`:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```
   A minimal `.env` file only needs this one line. See the [Configuration](#5-configuration) section for all available options.

### 5. Configuration

Edit the `.env` file to customize your settings:

```env
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional - customize as needed
SCHEDULE_DAY=sunday          # Day to run reports
SCHEDULE_HOUR=18             # Hour (24-hour format)
SCHEDULE_MINUTE=0            # Minute
TIMEZONE=America/New_York    # Your timezone
LOOKBACK_DAYS=7              # Days to look back
REPORT_FORMAT=markdown       # markdown, html, or txt
```

### 6. First Run - Authentication

Test your Google API authentication:

```bash
python main.py test-auth
```

This will open a browser window for you to authorize the application. Once authorized, a `token.json` file will be created for future use.

## Usage

### Generate a Report Immediately

```bash
python main.py run-now
```

This will:
1. Collect data from Gmail, Calendar, and Drive
2. Generate an AI-powered summary
3. Save the report to the `reports/` directory
4. Display a summary in the console

### Start the Scheduler

```bash
python main.py schedule
```

This will:
1. Start a background scheduler
2. Run the report generation every Sunday at 6 PM (or your configured time)
3. Keep running until you stop it (Ctrl+C)

### Running as a System Service (Linux)

For production use, you can run the scheduler as a systemd service:

1. Edit the provided service file:
   ```bash
   nano weekly-activity-summary.service
   ```

2. Update the paths to match your installation

3. Install the service:
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

### Changing the Schedule

Edit `.env`:
```env
SCHEDULE_DAY=friday          # Run on Friday instead
SCHEDULE_HOUR=17             # At 5 PM
SCHEDULE_MINUTE=30           # At 5:30 PM
```

### Changing the Lookback Period

```env
LOOKBACK_DAYS=14             # Look back 2 weeks instead of 1
```

### Changing Report Format

```env
REPORT_FORMAT=html           # Generate HTML reports
```

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
├── main.py                  # Main entry point
├── config.py                # Configuration management
├── google_auth.py           # Google API authentication
├── gmail_collector.py       # Gmail data collection
├── calendar_collector.py    # Calendar data collection
├── drive_collector.py       # Drive/Docs data collection
├── activity_summarizer.py   # AI summarization
├── report_generator.py      # Report orchestration
├── scheduler.py             # Scheduling logic
├── requirements.txt         # Python dependencies
├── .env.example            # Example configuration
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
