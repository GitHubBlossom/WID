"""
Google Data Sync - Integration with existing Google API collectors.

This module connects the existing Gmail, Calendar, and Drive collectors
to the Flask app's data store.
"""

from datetime import datetime, timedelta
from typing import List
import uuid
import logging

from models import DataStore, Activity, ActivitySource, ActivityCategory
from gmail_collector import GmailCollector
from calendar_collector import CalendarCollector
from drive_collector import DriveCollector


logger = logging.getLogger(__name__)


def sync_google_data(data_store: DataStore, lookback_days: int = 7) -> List[Activity]:
    """Sync data from Google services and convert to activities.

    Args:
        data_store: DataStore instance
        lookback_days: Number of days to look back

    Returns:
        List of newly created activities
    """
    new_activities = []

    try:
        # Sync Gmail
        logger.info("Syncing Gmail data...")
        gmail_activities = sync_gmail(lookback_days)
        for activity in gmail_activities:
            data_store.save_activity(activity)
        new_activities.extend(gmail_activities)
        logger.info(f"Synced {len(gmail_activities)} email activities")

    except Exception as e:
        logger.error(f"Error syncing Gmail: {e}")

    try:
        # Sync Calendar
        logger.info("Syncing Calendar data...")
        calendar_activities = sync_calendar(lookback_days)
        for activity in calendar_activities:
            data_store.save_activity(activity)
        new_activities.extend(calendar_activities)
        logger.info(f"Synced {len(calendar_activities)} calendar activities")

    except Exception as e:
        logger.error(f"Error syncing Calendar: {e}")

    try:
        # Sync Drive
        logger.info("Syncing Drive data...")
        drive_activities = sync_drive(lookback_days)
        for activity in drive_activities:
            data_store.save_activity(activity)
        new_activities.extend(drive_activities)
        logger.info(f"Synced {len(drive_activities)} document activities")

    except Exception as e:
        logger.error(f"Error syncing Drive: {e}")

    logger.info(f"Total activities synced: {len(new_activities)}")
    return new_activities


def sync_gmail(lookback_days: int) -> List[Activity]:
    """Sync Gmail data and convert to activities.

    Args:
        lookback_days: Number of days to look back

    Returns:
        List of Activity objects
    """
    collector = GmailCollector()
    gmail_data = collector.get_email_summary(days=lookback_days)

    activities = []

    # Process sent emails
    for email in gmail_data.get('sent_emails', [])[:50]:  # Limit to 50
        # Create unique ID based on email ID
        activity_id = f"gmail-sent-{email.get('id', str(uuid.uuid4()))}"

        activity = Activity(
            id=activity_id,
            date=email.get('date', datetime.now().date().isoformat()),
            timestamp=email.get('timestamp', datetime.now().isoformat()),
            title=f"Sent: {email.get('subject', 'No subject')}",
            description=f"To: {', '.join(email.get('to', []))}",
            category=ActivityCategory.EMAIL.value,
            source=ActivitySource.GMAIL.value,
            duration_minutes=5,  # Estimate 5 minutes per email
            tags=['sent', 'email'],
            metadata={
                'email_id': email.get('id'),
                'recipients': email.get('to', []),
                'thread_id': email.get('thread_id')
            }
        )
        activities.append(activity)

    # Process important received emails (limit to top conversations)
    for email in gmail_data.get('received_emails', [])[:30]:
        activity_id = f"gmail-received-{email.get('id', str(uuid.uuid4()))}"

        activity = Activity(
            id=activity_id,
            date=email.get('date', datetime.now().date().isoformat()),
            timestamp=email.get('timestamp', datetime.now().isoformat()),
            title=f"Received: {email.get('subject', 'No subject')}",
            description=f"From: {email.get('from', 'Unknown')}",
            category=ActivityCategory.EMAIL.value,
            source=ActivitySource.GMAIL.value,
            duration_minutes=3,  # Estimate 3 minutes per email read
            tags=['received', 'email'],
            metadata={
                'email_id': email.get('id'),
                'sender': email.get('from'),
                'thread_id': email.get('thread_id')
            }
        )
        activities.append(activity)

    return activities


def sync_calendar(lookback_days: int) -> List[Activity]:
    """Sync Calendar data and convert to activities.

    Args:
        lookback_days: Number of days to look back

    Returns:
        List of Activity objects
    """
    collector = CalendarCollector()
    calendar_data = collector.get_calendar_summary(days=lookback_days)

    activities = []

    for event in calendar_data.get('events', []):
        # Create unique ID based on event ID
        activity_id = f"calendar-{event.get('id', str(uuid.uuid4()))}"

        # Calculate duration
        start_time = event.get('start')
        end_time = event.get('end')
        duration_minutes = None

        if start_time and end_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                duration_minutes = int((end_dt - start_dt).total_seconds() / 60)
            except Exception as e:
                logger.debug(f"Error calculating duration: {e}")
                duration_minutes = 60  # Default to 1 hour

        # Determine if it's a meeting or just an event
        attendees = event.get('attendees', [])
        is_meeting = len(attendees) > 1

        activity = Activity(
            id=activity_id,
            date=event.get('date', datetime.now().date().isoformat()),
            timestamp=event.get('start', datetime.now().isoformat()),
            title=event.get('summary', 'Untitled Event'),
            description=event.get('description', ''),
            category=ActivityCategory.MEETING.value if is_meeting else ActivityCategory.WORK.value,
            source=ActivitySource.CALENDAR.value,
            duration_minutes=duration_minutes,
            tags=['meeting' if is_meeting else 'event', 'calendar'],
            metadata={
                'event_id': event.get('id'),
                'attendees': attendees,
                'location': event.get('location'),
                'organizer': event.get('organizer')
            }
        )
        activities.append(activity)

    return activities


def sync_drive(lookback_days: int) -> List[Activity]:
    """Sync Drive data and convert to activities.

    Args:
        lookback_days: Number of days to look back

    Returns:
        List of Activity objects
    """
    collector = DriveCollector()
    drive_data = collector.get_drive_summary(days=lookback_days)

    activities = []

    for doc in drive_data.get('documents', []):
        # Create unique ID based on document ID and modification time
        activity_id = f"drive-{doc.get('id', str(uuid.uuid4()))}"

        # Determine document type
        mime_type = doc.get('mime_type', '')
        if 'document' in mime_type:
            doc_type = 'Doc'
        elif 'spreadsheet' in mime_type:
            doc_type = 'Sheet'
        elif 'presentation' in mime_type:
            doc_type = 'Slides'
        else:
            doc_type = 'File'

        # Check if created or modified
        is_new = doc.get('is_new', False)
        action = 'Created' if is_new else 'Modified'

        activity = Activity(
            id=activity_id,
            date=doc.get('date', datetime.now().date().isoformat()),
            timestamp=doc.get('modified_time', datetime.now().isoformat()),
            title=f"{action}: {doc.get('name', 'Untitled')}",
            description=f"{doc_type} - {doc.get('name', 'Untitled')}",
            category=ActivityCategory.DOCUMENT.value,
            source=ActivitySource.DRIVE.value,
            duration_minutes=30 if is_new else 15,  # Estimate based on creation vs modification
            tags=['document', doc_type.lower()],
            metadata={
                'file_id': doc.get('id'),
                'mime_type': mime_type,
                'owner': doc.get('owner'),
                'url': doc.get('url')
            }
        )
        activities.append(activity)

    return activities
