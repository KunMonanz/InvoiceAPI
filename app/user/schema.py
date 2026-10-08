from typing import Literal, Optional
from weakref import ref

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, model_validator


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None
    organization_name: str | None = None

    @field_validator("first_name", "last_name", "organization_name", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: str | None) -> str | None:
        if isinstance(v, str):
            v = v.strip()
            return v if v else None
        return v

    @model_validator(mode="after")
    def validate_conditional_fields(self):
        has_first = bool(self.first_name)
        has_last = bool(self.last_name)
        has_org = bool(self.organization_name)

        if has_first and not has_last:
            raise ValueError(
                "If a first name is provided, a last name must be provided as well."
            )

        if has_last and not has_first:
            raise ValueError(
                "If a last name is provided, a first name must be provided as well."
            )

        if not (has_first and has_last) and not has_org:
            raise ValueError(
                "You must provide either an organization name or both first and last names."
            )

        return self


class UserResponse(BaseModel):
    email: EmailStr
    first_name: str | None
    last_name: str | None
    organization_name: str | None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"]


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class MessageResponse(BaseModel):
    message: str
