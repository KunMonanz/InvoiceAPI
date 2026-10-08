import os
import uuid

from fastapi import APIRouter, BackgroundTasks, Path, Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse, JSONResponse

from app.invoice.responses import CREATE_INVOICE_TASK, GET_TASK_STATUS
from app.invoice.taskstore import get_task_state, update_task_state
from app.middleware.ratelimit_middleware import limiter
from app.tasks import render_html_to_pdf_background_task

from .schema import InvoiceList, TaskStatusResponse

router = APIRouter(prefix="/api/v1/invoices", tags=["Invoices"])


@router.post(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=TaskStatusResponse,
    summary="Create invoice generation task",
    description="Asynchronously generates a PDF invoice using native background tasks.",
    responses=CREATE_INVOICE_TASK,
)
@limiter.limit("5/day")
async def create_invoice(
    request: Request, payload: InvoiceList, background_tasks: BackgroundTasks
):
    items = [item.model_dump() for item in payload.invoice]

    task_id = str(uuid.uuid4())

    update_task_state(task_id, "PENDING")

    background_tasks.add_task(
        render_html_to_pdf_background_task,
        task_id=task_id,
        customer_name=payload.customer_name,
        items=items,
        business_name=payload.business_name,
    )

    return TaskStatusResponse(task_id=task_id, status="processing")


@router.get(
    "/status/{task_id}",
    summary="Check invoice status or download PDF",
    description="Polls the task status. Returns status JSON while running, or the raw PDF once complete.",
    responses=GET_TASK_STATUS,
)
async def get_task_status(task_id: str = Path(..., description="Task UUID")):
    try:
        uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid task ID format"
        )

    task_info = get_task_state(task_id)

    if not task_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task ID not found"
        )

    state = task_info["state"]
    result = task_info["result"]

    if state in ("PENDING", "STARTED", "RETRY"):
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={"task_id": task_id, "status": "processing"},
        )

    if state == "FAILURE":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Task failed: {result}"},
        )

    if state == "SUCCESS":
        result_data = result or {}
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
        detail=f"Task ended in unexpected state: {state}",
    )
