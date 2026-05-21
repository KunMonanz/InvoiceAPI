from decimal import Decimal
from typing import List
from pydantic import BaseModel


class InvoiceItem(BaseModel):
    name: str
    quantity: int
    price: Decimal


class InvoiceList(BaseModel):
    customer_name: str
    invoice: List[InvoiceItem]