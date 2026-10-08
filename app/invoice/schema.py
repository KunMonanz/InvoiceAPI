from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class InvoiceItem(BaseModel):
    name: str
    quantity: int = Field(
        ge=1, description="Quantity must be greater than or equal to 1"
    )
    price: Decimal = Field(ge=0, description="Price must be greater than or equal to 0")

    @field_validator("name", mode="before")
    @classmethod
    def transform_to_title_case(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip().title()
        return value


class InvoiceList(BaseModel):
    customer_name: str
    business_name: str | None
    invoice: list[InvoiceItem]

    @field_validator("customer_name", mode="before")
    @classmethod
    def transform_to_title_case(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip().title()
        return value

    @field_validator("business_name", mode="before")
    @classmethod
    def remove_extra_whitespace(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            return value.strip()
        return value


class TaskStatusResponse(BaseModel):
    task_id: str
    status: Literal["processing", "completed", "failed"]


class ErrorResponse(BaseModel):
    detail: str
