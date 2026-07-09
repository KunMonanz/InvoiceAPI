from pydantic import BaseModel, ConfigDict, EmailStr, model_validator
from typing import Optional


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str]
    last_name: Optional[str]
    organization_name: Optional[str]

    @model_validator(mode="after")
    def validate_conditional_fileds(self):
        if not self.first_name or not self.last_name:
            if not self.organization_name:
                raise ValueError("If there's no first name or last name, an organization name should be provided")
        
        if self.first_name and not self.last_name:
            raise ValueError("If a first name is provided, a lastname should be provided")
        
        if self.last_name and not self.first_name:
            raise ValueError("If a lastname is provided, a first name should be provided as well")
        
        return self
    

class UserResponse(BaseModel):
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    organization_name: Optional[str]
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    