from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .network_scanner import run_scan
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def schedule_scan(cron_expression, scan_id):
    try:
        job = scheduler.add_job(
            run_scan, 
            CronTrigger.from_crontab(cron_expression),
            args=[scan_id],
            id=f'scan_{scan_id}'
        )
        logger.info(f"Scheduled scan {scan_id} with cron expression: {cron_expression}")
        return job
    except ValueError as e:
        logger.error(f"Invalid cron expression for scan {scan_id}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error scheduling scan {scan_id}: {str(e)}")
        raise

def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")
    else:
        logger.warning("Scheduler is already running")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
    else:
        logger.warning("Scheduler is not running")

def remove_scheduled_scan(scan_id):
    job_id = f'scan_{scan_id}'
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        logger.info(f"Removed scheduled scan {scan_id}")
    else:
        logger.warning(f"No scheduled scan found with id {scan_id}")
