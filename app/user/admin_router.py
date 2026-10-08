from fastapi import APIRouter, Header, HTTPException, status

from app.config.settings import settings
from app.scheduler import delete_saved_invoices

admin_router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


@admin_router.post("/cleanup", status_code=status.HTTP_200_OK)
async def trigger_cleanup(x_admin_token: str = Header(...)):
    if x_admin_token != settings.ADMIN_CRON_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    delete_saved_invoices()
    return {"message": "Cleanup successfully invoked"}
