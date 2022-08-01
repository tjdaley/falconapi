"""
user.py - User model
"""
from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = False
    admin: bool | None = False
    token: str | None = None
    hashed_password: str | None = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "username": "me@mydomain.com",
                "email": "me@mydomain.com",
                "full_name": "Thomas J. Daley, Esq.",
                "disabled": False,
                "admin": False,
                "token": "",
                "hashed_password": "$2b$12$CPC0UdsEoanAkwnJGb1iUO4OzRwuQ9pw66wqxADuzpUY1zBAO.FzK"
            }
        }

class UserRegistration(BaseModel):
    username: str
    email: str
    full_name: str
    password: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "username": "me@mydomain.com",
                "email": "me@mydomain.com",
                "full_name": "Thomas J. Daley, Esq.",
                "password": "password",
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
