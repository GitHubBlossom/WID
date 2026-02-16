"""Email sender module using Gmail API."""
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import logging
from google_auth import get_gmail_service

logger = logging.getLogger(__name__)


class EmailSender:
    """Sends emails using Gmail API."""

    def __init__(self):
        self.service = get_gmail_service()
        self.user_email = self._get_user_email()

    def _get_user_email(self):
        """Get the authenticated user's email address."""
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return profile.get('emailAddress')
        except Exception as e:
            logger.error(f"Error getting user email: {e}")
            return None

    def send_summary_email(self, report_path: Path, summary_date: str):
        """Send a productivity summary email.

        Args:
            report_path: Path to the generated report file
            summary_date: ISO format date string for the summary
        """
        if not self.user_email:
            raise Exception("Could not determine user email address")

        # Read the report content
        with open(report_path, 'r', encoding='utf-8') as f:
            report_content = f.read()

        # Create email
        subject = f"📊 Your Weekly Productivity Summary - {summary_date[:10]}"

        # Create HTML email with embedded report
        html_content = self._create_email_html(report_content, summary_date)

        # Send email
        self._send_email(
            to=self.user_email,
            subject=subject,
            html_content=html_content
        )

        logger.info(f"Summary email sent to {self.user_email}")

    def _create_email_html(self, report_content: str, summary_date: str) -> str:
        """Create HTML email content.

        Args:
            report_content: The report content (markdown or HTML)
            summary_date: ISO format date string

        Returns:
            HTML email content
        """
        # Convert markdown to HTML if needed
        if report_content.startswith('#'):
            # Simple markdown to HTML conversion
            html_report = self._markdown_to_html(report_content)
        else:
            html_report = report_content

        # Wrap in email template
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .email-container {{
            background-color: white;
            border-radius: 8px;
            padding: 40px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        h3 {{
            color: #7f8c8d;
        }}
        .stats {{
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .stat-item {{
            margin: 10px 0;
        }}
        strong {{
            color: #2c3e50;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            font-size: 12px;
            color: #95a5a6;
            text-align: center;
        }}
        ul {{
            padding-left: 20px;
        }}
        li {{
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        {html_report}

        <div class="footer">
            <p>Generated on {summary_date[:10]} by Productivity Analyzer</p>
            <p>This is an automated email. You're receiving this because automatic emails are enabled in your settings.</p>
        </div>
    </div>
</body>
</html>
"""
        return html_template

    def _markdown_to_html(self, markdown: str) -> str:
        """Simple markdown to HTML conversion.

        Args:
            markdown: Markdown content

        Returns:
            HTML content
        """
        html = markdown

        # Headers
        html = html.replace('\n# ', '\n<h1>').replace('</h1>', '')
        html = html.replace('\n## ', '\n<h2>').replace('</h2>', '')
        html = html.replace('\n### ', '\n<h3>').replace('</h3>', '')

        # Add closing tags
        lines = html.split('\n')
        result = []
        for i, line in enumerate(lines):
            if line.startswith('<h1>'):
                result.append(line + '</h1>')
            elif line.startswith('<h2>'):
                result.append(line + '</h2>')
            elif line.startswith('<h3>'):
                result.append(line + '</h3>')
            elif line.startswith('- '):
                # List items
                result.append('<li>' + line[2:] + '</li>')
            elif line.startswith('**') and line.endswith('**'):
                # Bold
                result.append('<strong>' + line[2:-2] + '</strong>')
            elif line.strip() == '---':
                # Horizontal rule
                result.append('<hr>')
            else:
                # Paragraph
                if line.strip():
                    result.append('<p>' + line + '</p>')
                else:
                    result.append('')

        return '\n'.join(result)

    def _send_email(self, to: str, subject: str, html_content: str):
        """Send an email using Gmail API.

        Args:
            to: Recipient email address
            subject: Email subject
            html_content: HTML email content
        """
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['To'] = to
            message['From'] = self.user_email
            message['Subject'] = subject

            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)

            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            # Send message
            self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            logger.info(f"Email sent successfully to {to}")

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            raise
