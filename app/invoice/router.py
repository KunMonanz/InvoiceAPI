import io

from fastapi import APIRouter, Request
from fastapi.responses import Response, StreamingResponse

from .schema import InvoiceList
from .utils.pdf_utils import render_html_to_pdf

from app.middleware.ratelimit_middleware import limiter

router  = APIRouter(
    prefix="/api/v1/invoices"
)


@router.post("/")
@limiter.limit("5/day")
def create_invoice(request: Request, payload: InvoiceList):
    customer_name = payload.customer_name
    items = [item.model_dump() for item in payload.invoice]
    
    invoice_pdf = render_html_to_pdf(customer_name, items)
    
    pdf_stream = io.BytesIO(invoice_pdf) # type: ignore
    
    return StreamingResponse(
        pdf_stream,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=invoice.pdf"}
    )
    
    