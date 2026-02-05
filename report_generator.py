"""Main report generation orchestrator."""
from datetime import datetime
from pathlib import Path
import logging
from gmail_collector import GmailCollector
from calendar_collector import CalendarCollector
from drive_collector import DriveCollector
from activity_summarizer import ActivitySummarizer
import config

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Orchestrates the collection and generation of weekly activity reports."""

    def __init__(self):
        self.gmail_collector = None
        self.calendar_collector = None
        self.drive_collector = None
        self.summarizer = None

    def generate_report(self):
        """Generate the weekly activity report."""
        try:
            logger.info("Starting weekly activity report generation...")
            logger.info(f"Looking back {config.LOOKBACK_DAYS} days")

            # Initialize collectors (lazy initialization)
            if not self.gmail_collector:
                self.gmail_collector = GmailCollector()
            if not self.calendar_collector:
                self.calendar_collector = CalendarCollector(config.TIMEZONE)
            if not self.drive_collector:
                self.drive_collector = DriveCollector()
            if not self.summarizer:
                self.summarizer = ActivitySummarizer()

            # Collect data
            logger.info("Collecting email data...")
            email_data = self.gmail_collector.get_email_summary(config.LOOKBACK_DAYS)

            logger.info("Collecting calendar data...")
            calendar_data = self.calendar_collector.get_events_summary(
                config.LOOKBACK_DAYS
            )

            logger.info("Collecting documents data...")
            documents_data = self.drive_collector.get_documents_summary(
                config.LOOKBACK_DAYS
            )

            # Generate summary
            logger.info("Generating activity summary...")
            summary = self.summarizer.generate_summary(
                email_data,
                calendar_data,
                documents_data
            )

            # Format report
            logger.info(f"Formatting report as {config.REPORT_FORMAT}...")
            formatted_report = self.summarizer.format_report(
                summary,
                email_data,
                calendar_data,
                documents_data,
                config.REPORT_FORMAT
            )

            # Save report
            report_path = self._save_report(formatted_report)
            logger.info(f"Report saved to: {report_path}")

            # Print summary to console
            self._print_summary(email_data, calendar_data, documents_data, report_path)

            return report_path

        except Exception as e:
            logger.error(f"Error generating report: {e}", exc_info=True)
            raise

    def _save_report(self, content: str) -> Path:
        """Save the report to a file.

        Args:
            content: Report content

        Returns:
            Path to saved report
        """
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        extension = {
            'markdown': 'md',
            'html': 'html',
            'txt': 'txt'
        }.get(config.REPORT_FORMAT, 'md')

        filename = f"weekly_report_{timestamp}.{extension}"
        report_path = config.REPORT_OUTPUT_DIR / filename

        # Ensure directory exists
        config.REPORT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        # Write report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return report_path

    def _print_summary(
        self,
        email_data: dict,
        calendar_data: dict,
        documents_data: dict,
        report_path: Path
    ):
        """Print a summary to the console.

        Args:
            email_data: Email statistics
            calendar_data: Calendar statistics
            documents_data: Documents statistics
            report_path: Path where report was saved
        """
        print("\n" + "=" * 60)
        print("WEEKLY ACTIVITY REPORT GENERATED")
        print("=" * 60)
        print(f"\n📧 Email Activity:")
        print(f"   Sent: {email_data.get('sent_count', 0)}")
        print(f"   Received: {email_data.get('received_count', 0)}")
        print(f"\n📅 Calendar Activity:")
        print(f"   Events: {calendar_data.get('total_events', 0)}")
        print(f"   Meetings: {calendar_data.get('meetings_attended', 0)}")
        print(f"   Meeting Hours: {calendar_data.get('total_meeting_hours', 0)}")
        print(f"\n📄 Document Activity:")
        print(f"   Total: {documents_data.get('total_documents', 0)}")
        print(f"   Docs: {documents_data.get('docs_count', 0)}")
        print(f"   Sheets: {documents_data.get('sheets_count', 0)}")
        print(f"   Slides: {documents_data.get('slides_count', 0)}")
        print(f"\n💾 Report saved to: {report_path}")
        print("=" * 60 + "\n")
