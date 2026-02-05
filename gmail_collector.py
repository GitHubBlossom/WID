"""Gmail data collection module."""
from datetime import datetime, timedelta
from typing import List, Dict
import base64
import email
from email.mime.text import MIMEText
import logging
from google_auth import get_gmail_service
import config

logger = logging.getLogger(__name__)


class GmailCollector:
    """Collects email data from Gmail."""

    def __init__(self):
        self.service = get_gmail_service()

    def get_emails(self, days_back: int = 7) -> Dict[str, List[Dict]]:
        """Fetch emails from the past N days.

        Args:
            days_back: Number of days to look back

        Returns:
            Dictionary with 'sent' and 'received' email lists
        """
        logger.info(f"Fetching emails from the past {days_back} days...")

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        # Format date for Gmail query (YYYY/MM/DD)
        after_date = start_date.strftime('%Y/%m/%d')

        emails = {
            'sent': self._get_sent_emails(after_date),
            'received': self._get_received_emails(after_date)
        }

        logger.info(
            f"Found {len(emails['sent'])} sent and "
            f"{len(emails['received'])} received emails"
        )

        return emails

    def _get_sent_emails(self, after_date: str) -> List[Dict]:
        """Get sent emails after a specific date."""
        query = f'in:sent after:{after_date}'
        return self._fetch_emails(query)

    def _get_received_emails(self, after_date: str) -> List[Dict]:
        """Get received emails after a specific date."""
        query = f'in:inbox after:{after_date}'
        return self._fetch_emails(query)

    def _fetch_emails(self, query: str, max_results: int = 500) -> List[Dict]:
        """Fetch emails matching a query.

        Args:
            query: Gmail search query
            max_results: Maximum number of emails to fetch

        Returns:
            List of email dictionaries
        """
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            emails = []

            for msg in messages:
                try:
                    email_data = self._get_email_details(msg['id'])
                    if email_data:
                        emails.append(email_data)
                except Exception as e:
                    logger.warning(f"Error fetching email {msg['id']}: {e}")
                    continue

            return emails

        except Exception as e:
            logger.error(f"Error fetching emails with query '{query}': {e}")
            return []

    def _get_email_details(self, msg_id: str) -> Dict:
        """Get detailed information about a specific email.

        Args:
            msg_id: Gmail message ID

        Returns:
            Dictionary containing email details
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()

            headers = message['payload']['headers']
            header_dict = {h['name']: h['value'] for h in headers}

            # Extract email body
            body = self._get_email_body(message['payload'])

            return {
                'id': msg_id,
                'thread_id': message.get('threadId', ''),
                'subject': header_dict.get('Subject', '(No subject)'),
                'from': header_dict.get('From', ''),
                'to': header_dict.get('To', ''),
                'cc': header_dict.get('Cc', ''),
                'date': header_dict.get('Date', ''),
                'snippet': message.get('snippet', ''),
                'body': body[:1000] if body else '',  # Limit body length
                'labels': message.get('labelIds', [])
            }

        except Exception as e:
            logger.error(f"Error getting email details for {msg_id}: {e}")
            return None

    def _get_email_body(self, payload: Dict) -> str:
        """Extract email body from message payload.

        Args:
            payload: Email payload from Gmail API

        Returns:
            Email body text
        """
        body = ""

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8', errors='ignore')
                        break
                elif part['mimeType'] == 'multipart/alternative':
                    body = self._get_email_body(part)
                    if body:
                        break
        elif 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(
                payload['body']['data']
            ).decode('utf-8', errors='ignore')

        return body

    def get_email_summary(self, days_back: int = 7) -> Dict:
        """Get a summary of email activity.

        Args:
            days_back: Number of days to look back

        Returns:
            Dictionary with email statistics and highlights
        """
        emails = self.get_emails(days_back)

        return {
            'sent_count': len(emails['sent']),
            'received_count': len(emails['received']),
            'sent_emails': emails['sent'],
            'received_emails': emails['received'],
            'top_contacts': self._get_top_contacts(emails),
            'subjects': self._get_email_subjects(emails)
        }

    def _get_top_contacts(self, emails: Dict, limit: int = 10) -> List[Dict]:
        """Get most frequent email contacts."""
        contact_count = {}

        for email in emails['sent']:
            to_addr = email.get('to', '')
            if to_addr:
                contact_count[to_addr] = contact_count.get(to_addr, 0) + 1

        for email in emails['received']:
            from_addr = email.get('from', '')
            if from_addr:
                contact_count[from_addr] = contact_count.get(from_addr, 0) + 1

        sorted_contacts = sorted(
            contact_count.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

        return [{'contact': c[0], 'count': c[1]} for c in sorted_contacts]

    def _get_email_subjects(self, emails: Dict) -> List[str]:
        """Extract all email subjects."""
        subjects = []

        for email in emails['sent']:
            subjects.append(f"[SENT] {email.get('subject', '')}")

        for email in emails['received']:
            subjects.append(f"[RECEIVED] {email.get('subject', '')}")

        return subjects
