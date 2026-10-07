import os
import uuid

from celery.result import AsyncResult
from fastapi import APIRouter, Path, Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse, JSONResponse

from app.invoice.responses import CREATE_INVOICE_TASK, GET_TASK_STATUS
from app.tasks import render_html_to_pdf_task

from .schema import InvoiceList, TaskStatusResponse

router = APIRouter(prefix="/api/v1/invoices")


@router.post(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=TaskStatusResponse,
    summary="Create invoice generation task",
    description="Asynchronously generates a PDF invoice and returns a Celery task ID.",
    responses=CREATE_INVOICE_TASK,
)
async def create_invoice(request: Request, payload: InvoiceList):
    items = [item.model_dump() for item in payload.invoice]

    task = render_html_to_pdf_task.delay(  # pyright: ignore[reportCallIssue]
        payload.customer_name, items, payload.business_name
    )

    return TaskStatusResponse(task_id=task.id, status="processing")


@router.get(
    "/status/{task_id}",
    summary="Check invoice status or download PDF",
    description="Polls the task status. Returns status JSON while running, or the raw PDF once complete.",
    responses=GET_TASK_STATUS,
)
async def get_task_status(task_id: str = Path(..., description="Celery task UUID")):
    try:
        uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid task ID format"
        )

    res = AsyncResult(task_id)

    if res.state in ("PENDING", "STARTED", "RETRY"):
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={"task_id": task_id, "status": "processing"},
        )

    if res.state == "FAILURE":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Task failed: {res.info!s}"},
        )

    if res.state == "SUCCESS":
        result_data = res.result or {}
        file_path = result_data.get("file_path")
        filename = result_data.get("filename")

        if not file_path or not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invoice file not found"
            )

        return FileResponse(
            path=file_path, filename=filename, media_type="application/pdf"
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Task ended in unexpected state: {res.state}",
    )
