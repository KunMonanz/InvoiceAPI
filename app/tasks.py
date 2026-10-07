import os
import re
import time
import uuid

from celery import shared_task

from app.config.celery_config import celery
from app.config.settings import FILE_AGE_THRESHOLD, UPLOAD_DIR

os.makedirs(UPLOAD_DIR, exist_ok=True)


@celery.task
def delete_saved_invoices():
    """Scans UPLOAD_DIR and deletes files older than 24 hours."""
    if not os.path.exists(UPLOAD_DIR):
        return f"Directory {UPLOAD_DIR} does not exist. Skipping."

    now = time.time()
    deleted_count = 0

    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)  # type: ignore

        if os.path.isfile(file_path):
            file_creation_time = os.path.getmtime(file_path)

            if (now - file_creation_time) > FILE_AGE_THRESHOLD:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception as e:
                    print(f"Failed to delete {filename}: {e}")

    return f"Cleanup complete. Deleted {deleted_count} files."


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def render_html_to_pdf_task(
    self, customer_name: str, items: list[dict], business_name: str | None = None
):
    """Celery task to render HTML to PDF and save it to disk."""
    try:
        from invoice.utils.pdf_utils import render_html_to_pdf

        pdf_bytes = render_html_to_pdf(customer_name, items, business_name)

        safe_name = re.sub(r"[^\w\-]", "_", customer_name.strip())
        unique_id = uuid.uuid4().hex[:8]
        filename = f"invoice_{safe_name}_{unique_id}.pdf"
        file_path = os.path.join(UPLOAD_DIR, filename)

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(pdf_bytes)

        return {
            "filename": filename,
            "file_path": file_path,
            "status": "completed",
        }

    except Exception as exc:
        raise self.retry(exc=exc)
