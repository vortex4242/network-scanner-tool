from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.job import Job
from .network_scanner import run_scan
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def schedule_scan(cron_expression: str, scan_id: int, user_id: int) -> Optional[Job]:
    """
    Schedule a new scan with the given cron expression.

    :param cron_expression: A string representing the cron schedule
    :param scan_id: The ID of the scan to be scheduled
    :param user_id: The ID of the user scheduling the scan
    :return: The scheduled job if successful, None otherwise
    """
    try:
        job = scheduler.add_job(
            run_scan, 
            CronTrigger.from_crontab(cron_expression),
            args=[scan_id, user_id],
            id=f'scan_{scan_id}_{user_id}',
            replace_existing=True
        )
        logger.info(f"Scheduled scan {scan_id} for user {user_id} with cron expression: {cron_expression}")
        return job
    except ValueError as e:
        logger.error(f"Invalid cron expression for scan {scan_id}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error scheduling scan {scan_id}: {str(e)}")
        raise

def start_scheduler() -> None:
    """Start the scheduler if it's not already running."""
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")
    else:
        logger.warning("Scheduler is already running")

def stop_scheduler() -> None:
    """Stop the scheduler if it's running."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
    else:
        logger.warning("Scheduler is not running")

async def remove_scheduled_scan(scan_id: int, user_id: int) -> None:
    """
    Remove a scheduled scan for a specific user.

    :param scan_id: The ID of the scan to be removed
    :param user_id: The ID of the user who scheduled the scan
    """
    job_id = f'scan_{scan_id}_{user_id}'
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        logger.info(f"Removed scheduled scan {scan_id} for user {user_id}")
    else:
        logger.warning(f"No scheduled scan found with id {scan_id} for user {user_id}")

async def get_scheduled_scans(user_id: int) -> List[Dict[str, Any]]:
    """
    Get all scheduled scans for a specific user.

    :param user_id: The ID of the user
    :return: A list of dictionaries containing information about scheduled scans
    """
    jobs = scheduler.get_jobs()
    user_jobs = [job for job in jobs if job.id.endswith(f'_{user_id}')]
    return [
        {
            'scan_id': int(job.id.split('_')[1]),
            'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
            'cron_expression': job.trigger.expression
        }
        for job in user_jobs
    ]
