import logging
import os
import time

from apscheduler.schedulers.background import BackgroundScheduler

from app.config.settings import settings

logger = logging.getLogger(__name__)


def delete_saved_invoices():
    """Scans UPLOAD_DIR and deletes files older than 24 hours."""
    if not os.path.exists(settings.UPLOAD_DIR):
        logger.warning(f"Directory {settings.UPLOAD_DIR} does not exist. Skipping.")
        return

    now = time.time()
    deleted_count = 0

    for filename in os.listdir(settings.UPLOAD_DIR):
        file_path = os.path.join(settings.UPLOAD_DIR, filename)

        if os.path.isfile(file_path):
            file_creation_time = os.path.getmtime(file_path)

            if (now - file_creation_time) > settings.FILE_AGE_THRESHOLD:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Failed to delete {filename}: {e}")

    logger.info(f"Cleanup complete. Deleted {deleted_count} files.")


def start_scheduler():
    """Starts the background engine inside the FastAPI app instance."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_saved_invoices, "interval", hours=1)
    scheduler.start()
    logger.info("In-app cleanup scheduler started successfully.")
