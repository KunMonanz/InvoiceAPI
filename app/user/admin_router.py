from fastapi import APIRouter, Header, HTTPException, status

from app.config.settings import settings
from app.scheduler import delete_saved_invoices
from app.user.utils import verify_cron_signature

admin_router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


@admin_router.post("/cleanup", status_code=status.HTTP_200_OK)
async def trigger_cleanup(
    x_cron_timestamp: str = Header(
        ..., description="Unix timestamp of when the request was made"
    ),
    x_cron_signature: str = Header(
        ..., description="HMAC-SHA256 signature generated with the shared secret"
    ),
):
    verify_cron_signature(
        timestamp=x_cron_timestamp,
        client_signature=x_cron_signature,
        secret_key=settings.ADMIN_CRON_SECRET,
    )

    delete_saved_invoices()
    return {"message": "Cleanup successfully invoked and verified"}
