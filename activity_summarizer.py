"""Activity summarization module using AI."""
from datetime import datetime
from typing import Dict
import logging
import anthropic
import config

logger = logging.getLogger(__name__)


class ActivitySummarizer:
    """Creates AI-powered summaries of weekly activity."""

    def __init__(self):
        if not config.ANTHROPIC_API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY not set. Please configure it in .env file."
            )
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    def generate_summary(
        self,
        email_data: Dict,
        calendar_data: Dict,
        documents_data: Dict
    ) -> str:
        """Generate a comprehensive weekly activity summary.

        Args:
            email_data: Email activity data
            calendar_data: Calendar activity data
            documents_data: Documents activity data

        Returns:
            Formatted summary text
        """
        logger.info("Generating AI-powered activity summary...")

        # Prepare the data for the AI
        activity_context = self._prepare_activity_context(
            email_data,
            calendar_data,
            documents_data
        )

        # Generate summary using Claude
        try:
            summary = self._generate_ai_summary(activity_context)
            logger.info("Summary generated successfully")
            return summary

        except Exception as e:
            logger.error(f"Error generating AI summary: {e}")
            # Fallback to basic summary
            return self._generate_basic_summary(
                email_data,
                calendar_data,
                documents_data
            )

    def _prepare_activity_context(
        self,
        email_data: Dict,
        calendar_data: Dict,
        documents_data: Dict
    ) -> str:
        """Prepare activity data as context for AI.

        Args:
            email_data: Email activity data
            calendar_data: Calendar activity data
            documents_data: Documents activity data

        Returns:
            Formatted context string
        """
        context_parts = []

        # Email context
        context_parts.append("=== EMAIL ACTIVITY ===")
        context_parts.append(f"Sent: {email_data.get('sent_count', 0)} emails")
        context_parts.append(f"Received: {email_data.get('received_count', 0)} emails")

        # Add some email subjects for context
        subjects = email_data.get('subjects', [])[:20]  # Limit to 20
        if subjects:
            context_parts.append("\nKey email subjects:")
            for subject in subjects:
                context_parts.append(f"- {subject}")

        # Top contacts
        top_contacts = email_data.get('top_contacts', [])[:5]
        if top_contacts:
            context_parts.append("\nTop contacts:")
            for contact in top_contacts:
                context_parts.append(
                    f"- {contact['contact']} ({contact['count']} emails)"
                )

        # Calendar context
        context_parts.append("\n=== CALENDAR ACTIVITY ===")
        context_parts.append(f"Total events: {calendar_data.get('total_events', 0)}")
        context_parts.append(
            f"Meetings attended: {calendar_data.get('meetings_attended', 0)}"
        )
        context_parts.append(
            f"Total meeting hours: {calendar_data.get('total_meeting_hours', 0)}"
        )

        # Add event details
        events = calendar_data.get('events', [])[:15]  # Limit to 15
        if events:
            context_parts.append("\nKey meetings:")
            for event in events:
                attendee_count = len(event.get('attendees', []))
                context_parts.append(
                    f"- {event['summary']} "
                    f"({attendee_count} attendees) - {event['start']}"
                )

        # Documents context
        context_parts.append("\n=== DOCUMENT ACTIVITY ===")
        context_parts.append(
            f"Total documents: {documents_data.get('total_documents', 0)}"
        )
        context_parts.append(
            f"Google Docs: {documents_data.get('docs_count', 0)}"
        )
        context_parts.append(
            f"Google Sheets: {documents_data.get('sheets_count', 0)}"
        )
        context_parts.append(
            f"Google Slides: {documents_data.get('slides_count', 0)}"
        )
        context_parts.append(
            f"Created: {documents_data.get('created_count', 0)}"
        )
        context_parts.append(
            f"Modified: {documents_data.get('modified_count', 0)}"
        )

        # Add document details
        docs_list = []
        for doc in documents_data.get('documents', {}).get('docs', [])[:10]:
            docs_list.append(f"- [DOC] {doc['name']} (modified: {doc['modified_time']})")
        for sheet in documents_data.get('documents', {}).get('sheets', [])[:10]:
            docs_list.append(f"- [SHEET] {sheet['name']} (modified: {sheet['modified_time']})")
        for slide in documents_data.get('documents', {}).get('slides', [])[:10]:
            docs_list.append(f"- [SLIDES] {slide['name']} (modified: {slide['modified_time']})")

        if docs_list:
            context_parts.append("\nDocuments worked on:")
            context_parts.extend(docs_list[:20])  # Limit total

        return "\n".join(context_parts)

    def _generate_ai_summary(self, activity_context: str) -> str:
        """Generate summary using Claude AI.

        Args:
            activity_context: Prepared activity context

        Returns:
            AI-generated summary
        """
        prompt = f"""You are analyzing someone's work activity for the past week.
Based on the data below, create a comprehensive weekly activity report that:

1. Provides an executive summary of the week's work
2. Highlights key meetings and collaborations
3. Identifies main projects and documents worked on
4. Notes communication patterns and key contacts
5. Summarizes productivity and focus areas
6. Suggests areas for follow-up or attention

Be professional, concise, and insightful. Focus on actionable insights.

ACTIVITY DATA:
{activity_context}

Please generate a well-structured weekly report."""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return message.content[0].text

        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            raise

    def _generate_basic_summary(
        self,
        email_data: Dict,
        calendar_data: Dict,
        documents_data: Dict
    ) -> str:
        """Generate a basic summary without AI (fallback).

        Args:
            email_data: Email activity data
            calendar_data: Calendar activity data
            documents_data: Documents activity data

        Returns:
            Basic formatted summary
        """
        lines = []
        lines.append("# WEEKLY ACTIVITY SUMMARY")
        lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("\n" + "=" * 50)

        # Email Summary
        lines.append("\n## EMAIL ACTIVITY")
        lines.append(f"- Sent: {email_data.get('sent_count', 0)} emails")
        lines.append(f"- Received: {email_data.get('received_count', 0)} emails")

        # Calendar Summary
        lines.append("\n## CALENDAR ACTIVITY")
        lines.append(f"- Total events: {calendar_data.get('total_events', 0)}")
        lines.append(
            f"- Meetings attended: {calendar_data.get('meetings_attended', 0)}"
        )
        lines.append(
            f"- Meeting hours: {calendar_data.get('total_meeting_hours', 0)}"
        )

        # Documents Summary
        lines.append("\n## DOCUMENT ACTIVITY")
        lines.append(
            f"- Total documents: {documents_data.get('total_documents', 0)}"
        )
        lines.append(f"- Docs: {documents_data.get('docs_count', 0)}")
        lines.append(f"- Sheets: {documents_data.get('sheets_count', 0)}")
        lines.append(f"- Slides: {documents_data.get('slides_count', 0)}")

        return "\n".join(lines)

    def format_report(
        self,
        summary: str,
        email_data: Dict,
        calendar_data: Dict,
        documents_data: Dict,
        format_type: str = 'markdown'
    ) -> str:
        """Format the complete report.

        Args:
            summary: AI-generated summary
            email_data: Email activity data
            calendar_data: Calendar activity data
            documents_data: Documents activity data
            format_type: Output format (markdown, html, txt)

        Returns:
            Formatted report
        """
        if format_type == 'markdown':
            return self._format_markdown_report(
                summary, email_data, calendar_data, documents_data
            )
        elif format_type == 'html':
            return self._format_html_report(
                summary, email_data, calendar_data, documents_data
            )
        else:
            return self._format_text_report(
                summary, email_data, calendar_data, documents_data
            )

    def _format_markdown_report(
        self,
        summary: str,
        email_data: Dict,
        calendar_data: Dict,
        documents_data: Dict
    ) -> str:
        """Format report as Markdown."""
        report = []
        report.append("# Weekly Activity Report")
        report.append(f"\n**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        report.append(f"\n**Period:** Past {config.LOOKBACK_DAYS} days")
        report.append("\n---")
        report.append("\n## Executive Summary\n")
        report.append(summary)
        report.append("\n---")
        report.append("\n## Activity Statistics\n")
        report.append("### Email")
        report.append(f"- Sent: **{email_data.get('sent_count', 0)}**")
        report.append(f"- Received: **{email_data.get('received_count', 0)}**")
        report.append("\n### Calendar")
        report.append(f"- Total Events: **{calendar_data.get('total_events', 0)}**")
        report.append(f"- Meetings: **{calendar_data.get('meetings_attended', 0)}**")
        report.append(f"- Meeting Hours: **{calendar_data.get('total_meeting_hours', 0)}**")
        report.append("\n### Documents")
        report.append(f"- Total: **{documents_data.get('total_documents', 0)}**")
        report.append(f"- Created: **{documents_data.get('created_count', 0)}**")
        report.append(f"- Modified: **{documents_data.get('modified_count', 0)}**")

        return "\n".join(report)

    def _format_html_report(
        self,
        summary: str,
        email_data: Dict,
        calendar_data: Dict,
        documents_data: Dict
    ) -> str:
        """Format report as HTML."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Weekly Activity Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; margin-top: 30px; }}
        .stats {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .summary {{ line-height: 1.6; }}
    </style>
</head>
<body>
    <h1>Weekly Activity Report</h1>
    <p><strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
    <p><strong>Period:</strong> Past {config.LOOKBACK_DAYS} days</p>
    <hr>
    <h2>Executive Summary</h2>
    <div class="summary">{summary}</div>
    <hr>
    <h2>Activity Statistics</h2>
    <div class="stats">
        <h3>Email</h3>
        <ul>
            <li>Sent: <strong>{email_data.get('sent_count', 0)}</strong></li>
            <li>Received: <strong>{email_data.get('received_count', 0)}</strong></li>
        </ul>
        <h3>Calendar</h3>
        <ul>
            <li>Total Events: <strong>{calendar_data.get('total_events', 0)}</strong></li>
            <li>Meetings: <strong>{calendar_data.get('meetings_attended', 0)}</strong></li>
            <li>Meeting Hours: <strong>{calendar_data.get('total_meeting_hours', 0)}</strong></li>
        </ul>
        <h3>Documents</h3>
        <ul>
            <li>Total: <strong>{documents_data.get('total_documents', 0)}</strong></li>
            <li>Created: <strong>{documents_data.get('created_count', 0)}</strong></li>
            <li>Modified: <strong>{documents_data.get('modified_count', 0)}</strong></li>
        </ul>
    </div>
</body>
</html>"""
        return html

    def _format_text_report(
        self,
        summary: str,
        email_data: Dict,
        calendar_data: Dict,
        documents_data: Dict
    ) -> str:
        """Format report as plain text."""
        report = []
        report.append("WEEKLY ACTIVITY REPORT")
        report.append("=" * 50)
        report.append(f"\nGenerated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        report.append(f"Period: Past {config.LOOKBACK_DAYS} days")
        report.append("\n" + "=" * 50)
        report.append("\nEXECUTIVE SUMMARY")
        report.append("-" * 50)
        report.append(summary)
        report.append("\n" + "=" * 50)
        report.append("\nACTIVITY STATISTICS")
        report.append("-" * 50)
        report.append(f"\nEmail:")
        report.append(f"  Sent: {email_data.get('sent_count', 0)}")
        report.append(f"  Received: {email_data.get('received_count', 0)}")
        report.append(f"\nCalendar:")
        report.append(f"  Total Events: {calendar_data.get('total_events', 0)}")
        report.append(f"  Meetings: {calendar_data.get('meetings_attended', 0)}")
        report.append(f"  Meeting Hours: {calendar_data.get('total_meeting_hours', 0)}")
        report.append(f"\nDocuments:")
        report.append(f"  Total: {documents_data.get('total_documents', 0)}")
        report.append(f"  Created: {documents_data.get('created_count', 0)}")
        report.append(f"  Modified: {documents_data.get('modified_count', 0)}")

        return "\n".join(report)
