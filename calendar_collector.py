"""Google Calendar data collection module."""
from datetime import datetime, timedelta
from typing import List, Dict
import logging
from google_auth import get_calendar_service
import pytz

logger = logging.getLogger(__name__)


class CalendarCollector:
    """Collects calendar event data from Google Calendar."""

    def __init__(self, timezone: str = 'UTC'):
        self.service = get_calendar_service()
        self.timezone = pytz.timezone(timezone)

    def get_events(self, days_back: int = 7) -> List[Dict]:
        """Fetch calendar events from the past N days.

        Args:
            days_back: Number of days to look back

        Returns:
            List of event dictionaries
        """
        logger.info(f"Fetching calendar events from the past {days_back} days...")

        # Calculate date range
        end_date = datetime.now(self.timezone)
        start_date = end_date - timedelta(days=days_back)

        # Convert to RFC3339 format
        time_min = start_date.isoformat()
        time_max = end_date.isoformat()

        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=500,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            logger.info(f"Found {len(events)} calendar events")

            parsed_events = []
            for event in events:
                parsed_event = self._parse_event(event)
                if parsed_event:
                    parsed_events.append(parsed_event)

            return parsed_events

        except Exception as e:
            logger.error(f"Error fetching calendar events: {e}")
            return []

    def _parse_event(self, event: Dict) -> Dict:
        """Parse a calendar event into a simplified format.

        Args:
            event: Raw event data from Google Calendar API

        Returns:
            Parsed event dictionary
        """
        try:
            # Get start and end times
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))

            # Check if it's an all-day event
            is_all_day = 'date' in event['start']

            # Parse attendees
            attendees = []
            if 'attendees' in event:
                attendees = [
                    {
                        'email': attendee.get('email', ''),
                        'name': attendee.get('displayName', ''),
                        'status': attendee.get('responseStatus', 'needsAction')
                    }
                    for attendee in event.get('attendees', [])
                ]

            return {
                'id': event.get('id', ''),
                'summary': event.get('summary', '(No title)'),
                'description': event.get('description', ''),
                'start': start,
                'end': end,
                'is_all_day': is_all_day,
                'location': event.get('location', ''),
                'attendees': attendees,
                'creator': event.get('creator', {}).get('email', ''),
                'organizer': event.get('organizer', {}).get('email', ''),
                'status': event.get('status', ''),
                'html_link': event.get('htmlLink', '')
            }

        except Exception as e:
            logger.warning(f"Error parsing event: {e}")
            return None

    def get_events_summary(self, days_back: int = 7) -> Dict:
        """Get a summary of calendar activity.

        Args:
            days_back: Number of days to look back

        Returns:
            Dictionary with event statistics and details
        """
        events = self.get_events(days_back)

        # Calculate statistics
        total_events = len(events)
        meetings_attended = sum(
            1 for event in events
            if event.get('attendees') and len(event['attendees']) > 1
        )
        solo_events = total_events - meetings_attended

        # Calculate total meeting time
        total_meeting_time = self._calculate_total_time(events)

        # Get event categories
        event_by_day = self._group_events_by_day(events)

        return {
            'total_events': total_events,
            'meetings_attended': meetings_attended,
            'solo_events': solo_events,
            'total_meeting_hours': round(total_meeting_time / 60, 2),
            'events': events,
            'events_by_day': event_by_day,
            'top_attendees': self._get_top_attendees(events)
        }

    def _calculate_total_time(self, events: List[Dict]) -> float:
        """Calculate total time spent in events (in minutes).

        Args:
            events: List of event dictionaries

        Returns:
            Total time in minutes
        """
        total_minutes = 0

        for event in events:
            if event['is_all_day']:
                continue

            try:
                start = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
                end = datetime.fromisoformat(event['end'].replace('Z', '+00:00'))
                duration = (end - start).total_seconds() / 60
                total_minutes += duration
            except Exception as e:
                logger.warning(f"Error calculating time for event: {e}")
                continue

        return total_minutes

    def _group_events_by_day(self, events: List[Dict]) -> Dict[str, List[Dict]]:
        """Group events by day.

        Args:
            events: List of event dictionaries

        Returns:
            Dictionary with dates as keys and event lists as values
        """
        events_by_day = {}

        for event in events:
            try:
                if event['is_all_day']:
                    date_str = event['start']
                else:
                    start_dt = datetime.fromisoformat(
                        event['start'].replace('Z', '+00:00')
                    )
                    date_str = start_dt.strftime('%Y-%m-%d')

                if date_str not in events_by_day:
                    events_by_day[date_str] = []

                events_by_day[date_str].append(event)

            except Exception as e:
                logger.warning(f"Error grouping event by day: {e}")
                continue

        return events_by_day

    def _get_top_attendees(self, events: List[Dict], limit: int = 10) -> List[Dict]:
        """Get most frequent meeting attendees.

        Args:
            events: List of event dictionaries
            limit: Maximum number of attendees to return

        Returns:
            List of top attendees with counts
        """
        attendee_count = {}

        for event in events:
            for attendee in event.get('attendees', []):
                email = attendee.get('email', '')
                if email:
                    attendee_count[email] = attendee_count.get(email, 0) + 1

        sorted_attendees = sorted(
            attendee_count.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

        return [
            {'email': email, 'meeting_count': count}
            for email, count in sorted_attendees
        ]
