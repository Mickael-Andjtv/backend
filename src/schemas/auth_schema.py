from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from .customer_schema import CustomerResponseSchema


class RegisterPreferences(BaseModel):
    isVegetarian: bool = False
    isGlutenFree: bool = False
    allergies: Optional[List[str]] = None
    preferredTableNotes: Optional[str] = None


class RegisterSchema(BaseModel):
    firstName: str = Field(min_length=1)
    lastName: str = Field(min_length=1)
    email: EmailStr
    phone: Optional[str] = None
    password: str = Field(min_length=6)
    preferences: Optional[RegisterPreferences] = None


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class AuthResponseSchema(BaseModel):
    token: str
    customer: CustomerResponseSchema


class MeResponseSchema(BaseModel):
    customer: CustomerResponseSchema