from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel


class InvoiceItem(BaseModel):
    name: str
    quantity: int
    price: Decimal


class InvoiceList(BaseModel):
    customer_name: str
    business_name: Optional[str]
    invoice: List[InvoiceItem]