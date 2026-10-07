from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel


class InvoiceItem(BaseModel):
    name: str
    quantity: int
    price: Decimal


class InvoiceList(BaseModel):
    customer_name: str
    business_name: Optional[str]
    invoice: List[InvoiceItem]


class TaskStatusResponse(BaseModel):
    task_id: str
    status: Literal["processing", "completed", "failed"]


class ErrorResponse(BaseModel):
    detail: str
