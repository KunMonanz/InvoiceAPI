import asyncio
import logging
import os
import re
import time
import uuid

from celery import shared_task
from celery.utils import gen_unique_id

from app.config.celery_config import celery
from app.config.settings import settings
from app.invoice.taskstore import update_task_state
from app.invoice.utils.pdf_utils import generate_pdf_file_name, render_html_to_pdf

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

logger = logging.getLogger(__name__)


@celery.task
def delete_saved_invoices():
    """Scans UPLOAD_DIR and deletes files older than 24 hours."""
    if not os.path.exists(settings.UPLOAD_DIR):
        return f"Directory {settings.UPLOAD_DIR} does not exist. Skipping."

    now = time.time()
    deleted_count = 0

    for filename in os.listdir(settings.UPLOAD_DIR):
        file_path = os.path.join(settings.UPLOAD_DIR, filename)  # type: ignore

        if os.path.isfile(file_path):
            file_creation_time = os.path.getmtime(file_path)

            if (now - file_creation_time) > settings.FILE_AGE_THRESHOLD:
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

        file_name_path_dto = generate_pdf_file_name(customer_name)

        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        with open(file_name_path_dto.file_path, "wb") as f:
            f.write(pdf_bytes)

        logger.info(f"Successfully generated PDF: {file_name_path_dto.filename}")
        return {
            "filename": file_name_path_dto.filename,
            "file_path": file_name_path_dto.file_path,
            "status": "completed",
        }

    except Exception as exc:
        raise self.retry(exc=exc)


async def render_html_to_pdf_background_task(
    task_id: str,
    customer_name: str,
    items: list[dict],
    business_name: str | None = None,
    retries_left: int = 3,
    delay: int = 60,
):
    """FastAPI Background Task to render HTML to PDF and save it to disk with built-in retries."""
    try:
        if retries_left == 3:
            update_task_state(task_id, "STARTED")

        pdf_bytes = render_html_to_pdf(customer_name, items, business_name)

        file_name_path_dto = generate_pdf_file_name(customer_name)

        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

        with open(file_name_path_dto.file_path, "wb") as f:
            f.write(pdf_bytes)

        logger.info(f"Successfully generated PDF: {file_name_path_dto.filename}")

        result_payload = {
            "filename": file_name_path_dto.filename,
            "file_path": file_name_path_dto.file_path,
            "status": "completed",
        }
        update_task_state(task_id, "SUCCESS", result=result_payload)
        return result_payload

    except Exception as exc:
        logger.warning(
            f"PDF generation failed: {str(exc)}. Retries left: {retries_left}"
        )

        if retries_left > 0:
            update_task_state(task_id, "RETRY", result=str(exc))

            await asyncio.sleep(delay)

            await render_html_to_pdf_background_task(
                task_id=task_id,
                customer_name=customer_name,
                items=items,
                business_name=business_name,
                retries_left=retries_left - 1,
                delay=delay,
            )
        else:
            logger.error(
                f"Task failed permanently after exhausting all retries. Exception: {str(exc)}"
            )
            update_task_state(task_id, "FAILURE", result=str(exc))
            raise exc
