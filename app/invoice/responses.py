from typing import Any

from app.invoice.schema import ErrorResponse, TaskStatusResponse

GET_TASK_STATUS: dict[int | str, dict[str, Any]] | None = {
    200: {
        "description": "Invoice is ready. Returns the PDF file.",
        "content": {
            "application/pdf": {
                "schema": {
                    "type": "string",
                    "format": "binary",
                }
            }
        },
        "headers": {
            "Content-Disposition": {
                "description": "Inline or attachment display directive containing filename.",
                "schema": {
                    "type": "string",
                    "example": 'inline; filename="invoice_John_Doe_a1b2c3d4.pdf"',
                },
            }
        },
    },
    202: {
        "model": TaskStatusResponse,
        "description": "Invoice rendering is still pending or processing.",
    },
    404: {
        "model": ErrorResponse,
        "description": "Task ID not found or generated file missing.",
    },
    500: {
        "model": ErrorResponse,
        "description": "PDF generation task failed in the worker.",
    },
}

CREATE_INVOICE_TASK: dict[int | str, dict[str, Any]] | None = {
    202: {
        "model": TaskStatusResponse,
        "description": "Task accepted and queued for processing.",
    },
    400: {
        "model": ErrorResponse,
        "description": "Invalid payload supplied.",
    },
}
