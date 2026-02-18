"""
WhatIDid.ai - Your Week Summarized
Analyzes Gmail, Calendar, and Drive activity to generate productivity summaries
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from datetime import datetime, timedelta
import os
import json
from pathlib import Path
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

# Import our modules
from report_generator import ReportGenerator
from email_sender import EmailSender
import config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize scheduler
scheduler = BackgroundScheduler()

# Data directory for storing summaries
DATA_DIR = Path('data/summaries')
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Config file for user settings
SETTINGS_FILE = Path('data/settings.json')


def load_settings():
    """Load user settings from file."""
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {
        'timezone': 'America/New_York',
        'schedule_day': 'sunday',
        'schedule_hour': 18,
        'schedule_minute': 0,
        'lookback_days': 1,
        'auto_email_enabled': False
    }


def save_settings(settings):
    """Save user settings to file."""
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)


def generate_summary(lookback_days=1):
    """Generate a productivity summary for the specified period."""
    try:
        logger.info(f"Generating summary for past {lookback_days} day(s)...")

        # Generate report
        generator = ReportGenerator()
        report_path = generator.generate_report()

        # Save summary metadata
        summary_date = datetime.now().isoformat()
        summary_file = DATA_DIR / f"summary_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"

        with open(summary_file, 'w') as f:
            json.dump({
                'date': summary_date,
                'lookback_days': lookback_days,
                'report_path': str(report_path)
            }, f, indent=2)

        logger.info(f"Summary generated: {report_path}")

        # Send email if enabled
        settings = load_settings()
        if settings.get('auto_email_enabled'):
            try:
                email_sender = EmailSender()
                email_sender.send_summary_email(report_path, summary_date)
                logger.info("Summary email sent successfully")
            except Exception as e:
                logger.error(f"Failed to send email: {e}")

        return True, str(report_path)

    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return False, str(e)


def schedule_weekly_summary():
    """Schedule the weekly summary generation based on user settings."""
    settings = load_settings()

    # Clear existing jobs
    scheduler.remove_all_jobs()

    # Map day names to cron day numbers
    day_mapping = {
        'sunday': 0, 'monday': 1, 'tuesday': 2, 'wednesday': 3,
        'thursday': 4, 'friday': 5, 'saturday': 6
    }

    day_of_week = day_mapping.get(settings['schedule_day'], 0)

    # Create trigger
    trigger = CronTrigger(
        day_of_week=day_of_week,
        hour=settings['schedule_hour'],
        minute=settings['schedule_minute'],
        timezone=pytz.timezone(settings['timezone'])
    )

    # Add job
    scheduler.add_job(
        lambda: generate_summary(settings.get('lookback_days', 1)),
        trigger,
        id='weekly_summary',
        name='Weekly Productivity Summary',
        replace_existing=True
    )

    logger.info(
        f"Scheduled weekly summary for {settings['schedule_day'].capitalize()} "
        f"at {settings['schedule_hour']:02d}:{settings['schedule_minute']:02d} "
        f"{settings['timezone']}"
    )


# Routes

@app.route('/')
def root():
    """Redirect root to the app dashboard."""
    return redirect(url_for('index'))


# App dashboard pages
@app.route('/app')
@app.route('/dashboard')
def index():
    """Dashboard page."""
    # Check if OAuth is configured
    if not Path('token.json').exists() or not Path('credentials.json').exists():
        return redirect(url_for('setup'))

    # Load settings
    settings = load_settings()

    # Get all summaries grouped by week
    summaries_by_week = get_summaries_by_week()

    # Get next scheduled run time
    next_run = None
    job = scheduler.get_job('weekly_summary')
    if job:
        next_run = job.next_run_time

    return render_template(
        'dashboard.html',
        settings=settings,
        summaries_by_week=summaries_by_week,
        next_run=next_run
    )


@app.route('/setup', methods=['GET', 'POST'])
def setup():
    """Setup page for OAuth and settings configuration."""
    if request.method == 'POST':
        # Save settings
        settings = {
            'timezone': request.form.get('timezone', 'America/New_York'),
            'schedule_day': request.form.get('schedule_day', 'sunday'),
            'schedule_hour': int(request.form.get('schedule_hour', 18)),
            'schedule_minute': int(request.form.get('schedule_minute', 0)),
            'lookback_days': int(request.form.get('lookback_days', 1)),
            'auto_email_enabled': request.form.get('auto_email_enabled') == 'on'
        }
        save_settings(settings)

        # Reschedule
        schedule_weekly_summary()

        flash('Settings saved successfully!', 'success')
        return redirect(url_for('index'))

    # Load current settings
    settings = load_settings()

    # Check OAuth status
    oauth_configured = Path('credentials.json').exists()
    oauth_authenticated = Path('token.json').exists()

    # Get timezone list
    timezones = pytz.common_timezones

    return render_template(
        'setup.html',
        settings=settings,
        oauth_configured=oauth_configured,
        oauth_authenticated=oauth_authenticated,
        timezones=timezones
    )


@app.route('/run', methods=['POST'])
def run_summary():
    """Manually trigger summary generation."""
    settings = load_settings()
    lookback_days = int(request.form.get('lookback_days', settings.get('lookback_days', 1)))

    success, result = generate_summary(lookback_days)

    if success:
        flash(f'Summary generated successfully! Report saved to: {result}', 'success')
    else:
        flash(f'Error generating summary: {result}', 'error')

    return redirect(url_for('index'))


@app.route('/summary/<date>')
def view_summary(date):
    """View a specific summary."""
    # Find the summary file for this date
    summary_files = list(DATA_DIR.glob(f"summary_{date}*.json"))

    if not summary_files:
        flash('Summary not found', 'error')
        return redirect(url_for('index'))

    # Load the summary
    with open(summary_files[0], 'r') as f:
        summary_data = json.load(f)

    # Load the report
    report_path = Path(summary_data['report_path'])
    if report_path.exists():
        with open(report_path, 'r') as f:
            report_content = f.read()
    else:
        report_content = "Report file not found"

    return render_template(
        'summary.html',
        summary_data=summary_data,
        report_content=report_content
    )


@app.route('/api/test-auth')
def test_auth():
    """Test Google API authentication."""
    try:
        from google_auth import get_gmail_service

        gmail = get_gmail_service()
        profile = gmail.users().getProfile(userId='me').execute()

        return jsonify({
            'success': True,
            'email': profile.get('emailAddress')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/contact', methods=['GET'])
def contact():
    """Contact page."""
    return render_template('contact.html')


@app.route('/contact/submit', methods=['POST'])
def contact_submit():
    """Handle contact form submission."""
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    subject = request.form.get('subject', '').strip()
    message = request.form.get('message', '').strip()

    if not all([name, email, subject, message]):
        flash('Please fill in all fields.', 'error')
        return redirect(url_for('contact'))

    # Log the submission
    logger.info(f"Contact form submission from {name} <{email}>: {subject}")

    flash('Message sent! We\'ll get back to you soon.', 'success')
    return redirect(url_for('contact'))


def get_summaries_by_week():
    """Get all summaries grouped by calendar week."""
    summaries = []

    for summary_file in sorted(DATA_DIR.glob('summary_*.json'), reverse=True):
        try:
            with open(summary_file, 'r') as f:
                summary_data = json.load(f)

            # Parse date
            date = datetime.fromisoformat(summary_data['date'])

            # Get week info
            week_number = date.isocalendar()[1]
            year = date.year
            week_key = f"{year}-W{week_number:02d}"

            summaries.append({
                'date': date,
                'date_str': date.strftime('%Y-%m-%d'),
                'date_display': date.strftime('%B %d, %Y at %I:%M %p'),
                'week_key': week_key,
                'week_display': f"Week {week_number}, {year}",
                'lookback_days': summary_data.get('lookback_days', 1),
                'report_path': summary_data.get('report_path', '')
            })
        except Exception as e:
            logger.warning(f"Error loading summary {summary_file}: {e}")
            continue

    # Group by week
    grouped = {}
    for summary in summaries:
        week_key = summary['week_key']
        if week_key not in grouped:
            grouped[week_key] = {
                'week_display': summary['week_display'],
                'summaries': []
            }
        grouped[week_key]['summaries'].append(summary)

    return grouped


if __name__ == '__main__':
    # Initialize scheduler
    schedule_weekly_summary()
    scheduler.start()

    logger.info("Starting WhatIDid.ai web application...")
    logger.info("Access the app at http://localhost:5555")

    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5555)
