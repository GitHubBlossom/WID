"""Scheduler module for running weekly reports."""
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import config

logger = logging.getLogger(__name__)


class WeeklyScheduler:
    """Schedules and manages weekly report generation."""

    def __init__(self, report_function):
        """Initialize the scheduler.

        Args:
            report_function: Function to call when generating reports
        """
        self.scheduler = BlockingScheduler(
            timezone=pytz.timezone(config.TIMEZONE)
        )
        self.report_function = report_function

    def schedule_weekly_report(self):
        """Schedule the weekly report generation."""
        # Map day names to cron day numbers (0 = Sunday, 6 = Saturday)
        day_mapping = {
            'sunday': 0,
            'monday': 1,
            'tuesday': 2,
            'wednesday': 3,
            'thursday': 4,
            'friday': 5,
            'saturday': 6
        }

        day_of_week = day_mapping.get(config.SCHEDULE_DAY, 0)

        # Create cron trigger
        trigger = CronTrigger(
            day_of_week=day_of_week,
            hour=config.SCHEDULE_HOUR,
            minute=config.SCHEDULE_MINUTE,
            timezone=config.TIMEZONE
        )

        # Add job
        self.scheduler.add_job(
            self.report_function,
            trigger,
            id='weekly_report',
            name='Weekly Activity Report Generation',
            replace_existing=True
        )

        logger.info(
            f"Scheduled weekly report for {config.SCHEDULE_DAY.capitalize()} "
            f"at {config.SCHEDULE_HOUR:02d}:{config.SCHEDULE_MINUTE:02d} "
            f"{config.TIMEZONE}"
        )

    def run_now(self):
        """Run the report generation immediately (for testing)."""
        logger.info("Running report generation now...")
        self.report_function()

    def start(self):
        """Start the scheduler (blocking)."""
        logger.info("Starting scheduler...")
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped by user")
            self.scheduler.shutdown()

    def get_next_run_time(self):
        """Get the next scheduled run time."""
        job = self.scheduler.get_job('weekly_report')
        if job:
            return job.next_run_time
        return None
