from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from .customer_schema import CustomerResponseSchema


class RegisterSchema(BaseModel):
    firstName: str = Field(min_length=1)
    lastName: str = Field(min_length=1)
    email: EmailStr
    phone: Optional[str] = None
    password: str = Field(min_length=6)


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class AuthResponseSchema(BaseModel):
    token: str
    customer: CustomerResponseSchema


class MeResponseSchema(BaseModel):
    customer: CustomerResponseSchema