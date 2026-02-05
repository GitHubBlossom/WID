#!/usr/bin/env python3
"""
Weekly Activity Summary Application

This application automatically generates weekly activity reports by analyzing:
- Gmail emails (sent and received)
- Google Calendar appointments
- Google Drive documents (Docs, Sheets, Slides)

It uses AI to create insightful summaries of your weekly work.
"""

import sys
import argparse
import logging
from pathlib import Path
import colorlog

from report_generator import ReportGenerator
from scheduler import WeeklyScheduler
import config


def setup_logging(verbose: bool = False):
    """Configure logging with colors.

    Args:
        verbose: Enable verbose logging
    """
    log_level = logging.DEBUG if verbose else logging.INFO

    # Create formatter with colors
    formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(name)s%(reset)s: %(message)s',
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )

    # Configure root logger
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)

    # Reduce noise from Google API libraries
    logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
    logging.getLogger('googleapiclient.discovery').setLevel(logging.WARNING)
    logging.getLogger('google.auth').setLevel(logging.WARNING)


def run_now_command(args):
    """Run report generation immediately.

    Args:
        args: Command line arguments
    """
    logger = logging.getLogger(__name__)
    logger.info("Running weekly activity report generation...")

    try:
        generator = ReportGenerator()
        report_path = generator.generate_report()
        print(f"\n✅ Report generated successfully!")
        print(f"📄 Location: {report_path}\n")
        return 0

    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        if args.verbose:
            logger.exception("Full traceback:")
        return 1


def schedule_command(args):
    """Start the scheduler.

    Args:
        args: Command line arguments
    """
    logger = logging.getLogger(__name__)

    try:
        generator = ReportGenerator()
        scheduler = WeeklyScheduler(generator.generate_report)
        scheduler.schedule_weekly_report()

        next_run = scheduler.get_next_run_time()
        print("\n" + "=" * 60)
        print("⏰ WEEKLY ACTIVITY REPORT SCHEDULER STARTED")
        print("=" * 60)
        print(f"\n📅 Schedule: Every {config.SCHEDULE_DAY.capitalize()}")
        print(f"⏰ Time: {config.SCHEDULE_HOUR:02d}:{config.SCHEDULE_MINUTE:02d} {config.TIMEZONE}")
        print(f"\n🔜 Next run: {next_run}")
        print("\n💡 Press Ctrl+C to stop the scheduler")
        print("=" * 60 + "\n")

        scheduler.start()
        return 0

    except KeyboardInterrupt:
        logger.info("\nScheduler stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Scheduler error: {e}")
        if args.verbose:
            logger.exception("Full traceback:")
        return 1


def test_auth_command(args):
    """Test Google API authentication.

    Args:
        args: Command line arguments
    """
    logger = logging.getLogger(__name__)
    logger.info("Testing Google API authentication...")

    try:
        from google_auth import (
            get_gmail_service,
            get_calendar_service,
            get_drive_service
        )

        print("\n" + "=" * 60)
        print("🔐 TESTING GOOGLE API AUTHENTICATION")
        print("=" * 60)

        print("\n📧 Testing Gmail API...")
        gmail = get_gmail_service()
        profile = gmail.users().getProfile(userId='me').execute()
        print(f"   ✅ Connected as: {profile.get('emailAddress')}")

        print("\n📅 Testing Calendar API...")
        calendar = get_calendar_service()
        cal_list = calendar.calendarList().list(maxResults=1).execute()
        print(f"   ✅ Found {len(cal_list.get('items', []))} calendar(s)")

        print("\n📄 Testing Drive API...")
        drive = get_drive_service()
        about = drive.about().get(fields='user').execute()
        print(f"   ✅ Connected as: {about['user']['emailAddress']}")

        print("\n" + "=" * 60)
        print("✅ All authentication tests passed!")
        print("=" * 60 + "\n")
        return 0

    except FileNotFoundError as e:
        logger.error(str(e))
        print("\n❌ Authentication failed!")
        print("\n📝 Setup instructions:")
        print("   1. Go to https://console.cloud.google.com/")
        print("   2. Create a new project or select existing one")
        print("   3. Enable Gmail, Calendar, and Drive APIs")
        print("   4. Create OAuth 2.0 credentials")
        print("   5. Download credentials.json to this directory")
        print("   6. Run this command again\n")
        return 1

    except Exception as e:
        logger.error(f"Authentication test failed: {e}")
        if args.verbose:
            logger.exception("Full traceback:")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Weekly Activity Summary - AI-powered work activity reports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s run-now              Generate report immediately
  %(prog)s schedule             Start scheduler (runs weekly)
  %(prog)s test-auth            Test Google API authentication

For more information, see README.md
        """
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # run-now command
    parser_run = subparsers.add_parser(
        'run-now',
        help='Generate weekly report immediately'
    )
    parser_run.set_defaults(func=run_now_command)

    # schedule command
    parser_schedule = subparsers.add_parser(
        'schedule',
        help='Start the scheduler to run reports weekly'
    )
    parser_schedule.set_defaults(func=schedule_command)

    # test-auth command
    parser_test = subparsers.add_parser(
        'test-auth',
        help='Test Google API authentication'
    )
    parser_test.set_defaults(func=test_auth_command)

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    # Show help if no command specified
    if not args.command:
        parser.print_help()
        return 1

    # Run the command
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
