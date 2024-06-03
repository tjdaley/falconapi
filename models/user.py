"""
user.py - User model
"""
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field

class User(BaseModel):
    username: str
    email: str
    full_name: str
    disabled: Optional[bool] = False
    admin: Optional[bool] = False
    token: Optional[str] = None
    hashed_password: Optional[str] = None
    version: Optional[str] = str(uuid4())
    id: Optional[str] = ''
    twilio_factor_id: Optional[str] = ''
    phone_number: Optional[str] = ''

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "username": "me@mydomain.com",
                "email": "me@mydomain.com",
                "full_name": "Thomas J. Daley, Esq.",
                "disabled": False,
                "admin": False,
                "user_id": "UUIDXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                "twilio_factor_id": "FAXXXXXXXXXXXXXXXXXXXXXXXXXX"
            }
        }

class UserRegistration(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    twilio_factor_id: Optional[str] = ''
    phone_number: Optional[str] = ''
    site_code: str
    id: Optional[str] = str(uuid4())

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "username": "me@mydomain.com",
                "email": "me@mydomain.com",
                "full_name": "Thomas J. Daley, Esq.",
                "password": "password",
                "twilio_factor_id": "FAxxxxxxxxxxxxxxxxx",
                "phone_number": "+12145550505",
                "site_code": "FASxxxxxxxxxxxxxxxxxxxxxxxxx"
            }
        }

class RegistrationResponse(BaseModel):
    username: str
    message: str
    status: str
    user_id: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "username": "me@mydomain.com",
                "message": "User created successfully",
                "status": "success",
                "user_id": "62e72880301b8a8b57a743c6"
            }
        }
