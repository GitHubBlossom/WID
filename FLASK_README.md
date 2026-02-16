# What I Did - Flask Web App

A personal productivity tracker web application built with Flask. Track your daily activities, set weekly goals, and get AI-powered insights to improve your productivity.

## Features

### Core Features
- **Dashboard**: Overview of your weekly productivity with stats and visualizations
- **Activity Logging**: Manually log daily activities or sync from Google services
- **Weekly Goals**: Set, track, and manage weekly goals with progress monitoring
- **AI Insights**: Get intelligent insights about your productivity patterns
- **Smart To-Dos**: AI-generated action items based on your activities and goals
- **Google Integration**: Automatically sync activities from Gmail, Calendar, and Drive

### Data Management
- All data stored locally in JSON files
- No external database required
- Easy to backup and migrate
- Privacy-focused design

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file with your settings:

```env
# Required for AI features
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional Flask settings
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=development
```

### 3. Google API Setup (Optional)

If you want to sync data from Google services:

1. Follow the setup instructions in the main README.md
2. Download `credentials.json` from Google Cloud Console
3. Place it in the project directory
4. Run authentication: `python main.py test-auth`

### 4. Run the Application

```bash
# Start the Flask development server
python app.py
```

The app will be available at `http://localhost:5000`

## Usage Guide

### Dashboard
- View weekly statistics and activity breakdown
- Quick access to recent activities, goals, and insights
- One-click sync with Google services
- Generate AI insights on demand

### Activities
- **Manual Logging**: Click "Log Activity" to add a new activity
  - Enter title, description, category, and duration
  - Add tags for better organization
  - Set date and time

- **Google Sync**: Click "Sync Google Data" to import:
  - Sent and received emails from Gmail
  - Calendar events and meetings
  - Google Docs, Sheets, and Slides activity

### Weekly Goals
- Set goals for each week (Monday-Sunday)
- Track progress with target hours
- Update status as you work
- View completion percentage

### AI Insights
- Click "Generate Insights" to analyze your week
- Get 3-5 key insights about:
  - Productivity patterns
  - Time usage analysis
  - Progress against goals
  - Areas for improvement

### To-Dos
- AI generates actionable to-dos from your insights
- Prioritized by importance (high, medium, low)
- Check off items as you complete them
- Filter by status (pending, in progress, completed)

## Data Structure

### Files
All data is stored in the `data/` directory as JSON files:

- `activities.json` - Activity log entries
- `goals.json` - Weekly goals
- `insights.json` - AI-generated insights
- `todos.json` - To-do items

### Activity Schema
```json
{
  "id": "unique-id",
  "date": "2026-02-16",
  "timestamp": "2026-02-16T10:30:00",
  "title": "Activity title",
  "description": "Detailed description",
  "category": "work|meeting|email|document|learning|personal|other",
  "source": "manual|gmail|calendar|drive",
  "duration_minutes": 30,
  "tags": ["tag1", "tag2"],
  "metadata": {}
}
```

### Goal Schema
```json
{
  "id": "unique-id",
  "week_start": "2026-02-17",
  "title": "Goal title",
  "description": "Goal description",
  "status": "not_started|in_progress|completed|cancelled",
  "created_at": "2026-02-16T12:00:00",
  "updated_at": "2026-02-16T12:00:00",
  "target_hours": 10.0,
  "actual_hours": 5.5
}
```

## API Endpoints

### Web Routes
- `GET /` - Dashboard
- `GET /activities` - Activity list
- `POST /activities/add` - Add new activity
- `GET /goals` - Goals list
- `POST /goals/add` - Add new goal
- `GET /insights` - Insights list
- `GET /todos` - To-do list
- `GET /settings` - Settings page

### AJAX API
- `POST /sync/google` - Sync Google data
- `POST /insights/generate` - Generate AI insights
- `POST /goals/<id>/update_status` - Update goal status
- `POST /todos/<id>/update_status` - Update to-do status
- `GET /api/stats/week/<week_start>` - Get week statistics

## Development

### Project Structure
```
WID/
├── app.py                    # Flask application
├── models.py                 # Data models and storage
├── ai_assistant.py           # AI insights generation
├── google_data_sync.py       # Google API integration
├── templates/                # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── activities.html
│   ├── goals.html
│   ├── insights.html
│   └── todos.html
├── static/
│   ├── css/
│   │   └── style.css        # Styles
│   └── js/
│       └── main.js          # JavaScript
├── data/                     # JSON data files
├── requirements.txt
└── README.md
```

### Adding New Features

1. **New Data Model**: Add to `models.py`
2. **New Route**: Add to `app.py`
3. **New Template**: Create in `templates/`
4. **New Styles**: Add to `static/css/style.css`

### Testing

```bash
# Test the application
python app.py

# Navigate to http://localhost:5000
# Test each feature:
# 1. Log an activity
# 2. Create a goal
# 3. Sync Google data (if configured)
# 4. Generate insights
```

## Configuration Options

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Yes | - | Anthropic API key for AI features |
| `FLASK_SECRET_KEY` | No | Auto-generated | Flask session secret |
| `FLASK_ENV` | No | `production` | Flask environment |

### Data Storage

By default, data is stored in the `data/` directory. To change this:

```python
# In app.py
data_store = DataStore(data_dir="custom/path")
```

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "ANTHROPIC_API_KEY not set"
Add your API key to the `.env` file or set as environment variable:
```bash
export ANTHROPIC_API_KEY=your_key_here
```

### Google sync not working
1. Ensure `credentials.json` is in the project directory
2. Run `python main.py test-auth` to authenticate
3. Check that `token.json` was created

### No data appearing
1. Check that the `data/` directory exists
2. Verify JSON files are being created
3. Check browser console for JavaScript errors

## Production Deployment

### Using Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

### Environment Variables for Production

```env
FLASK_ENV=production
FLASK_SECRET_KEY=generate-a-strong-random-key
ANTHROPIC_API_KEY=your_api_key
```

## Security Considerations

- Set a strong `FLASK_SECRET_KEY` in production
- Keep your `.env` file secure and never commit it
- Restrict file permissions on `data/` directory
- Use HTTPS in production
- Consider adding authentication for multi-user deployments

## Backup and Migration

### Backup Data
```bash
# Backup all data
tar -czf backup-$(date +%Y%m%d).tar.gz data/
```

### Restore Data
```bash
# Extract backup
tar -xzf backup-20260216.tar.gz
```

### Export to CSV
Data can be exported programmatically:

```python
from models import DataStore
import csv

store = DataStore()
activities = store.get_activities()

with open('activities.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=activities[0].to_dict().keys())
    writer.writeheader()
    writer.writerows([a.to_dict() for a in activities])
```

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the main README.md for Google API setup
3. Check application logs for errors

## License

See LICENSE file for details.

## Changelog

### Version 1.0 (2026-02-16)
- Initial Flask web app release
- Dashboard with activity stats
- Manual activity logging
- Weekly goals management
- AI insights and to-dos generation
- Google services integration
- Responsive web design
