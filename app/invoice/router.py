import io
import os
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from .schema import InvoiceList
from .utils.pdf_utils import render_html_to_pdf

router = APIRouter(prefix="/api/v1/invoices")


UPLOAD_DIR = "./saved_invoices"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def create_invoice(request: Request, payload: InvoiceList):
    customer_name = payload.customer_name
    business_name = payload.business_name
    items = [item.model_dump() for item in payload.invoice]
    
    invoice_pdf = render_html_to_pdf(
        customer_name=customer_name, 
        items=items,
        business_name=business_name
    )

    filename = f"invoice_{customer_name.replace(' ', '_')}.pdf"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as f:
        f.write(invoice_pdf) # type: ignore
    
    pdf_stream = io.BytesIO(invoice_pdf) # type: ignore
    
    return StreamingResponse(
        pdf_stream,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename={filename}"
        }
    )
