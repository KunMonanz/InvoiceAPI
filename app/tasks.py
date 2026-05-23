# tasks.py
import os
import time
from config.celery_config import celery
from config.settings import UPLOAD_DIR, FILE_AGE_THRESHOLD
 



@celery.task
def delete_saved_invoices():
    """Scans UPLOAD_DIR and deletes files older than 24 hours."""
    if not os.path.exists(UPLOAD_DIR):
        return f"Directory {UPLOAD_DIR} does not exist. Skipping."

    now = time.time()
    deleted_count = 0

    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename) # type: ignore

        if os.path.isfile(file_path):
            file_creation_time = os.path.getmtime(file_path)
            
            if (now - file_creation_time) > FILE_AGE_THRESHOLD:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception as e:
                    print(f"Failed to delete {filename}: {e}")

    return f"Cleanup complete. Deleted {deleted_count} files."
