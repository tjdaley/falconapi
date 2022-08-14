"""
decorators.py - Decorators
"""
from fastapi import Request, HTTPException, status
from typing import Optional
from functools import wraps
from pydantic import BaseModel
import os
from jose import JWTError, jwt
from routers.api_version import APIVersion
from database.users_table import UsersTable

# We want an exception to be raised if and of these three variables is missing
SECRET_KEY = os.environ['JWT_SECRET_KEY']
ALGORITHM = os.environ['JWT_ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ['JWT_ACCESS_TOKEN_EXPIRE_MINUTES'])

API_VERSION = APIVersion(1, 0).to_str()
USERS_TABLE = UsersTable()

class TokenData(BaseModel):
    username: Optional[str] = None

def check_api_token(func):
    @wraps(func)
    async def wrapper(*args, request: Request, **kwargs):
        HEADER = os.getenv('API_TOKEN_HEADER', 'x-authorization').lower()
        TOKEN = os.getenv('API_TOKEN', 'falcon')
        auth_header = request.headers.get(HEADER)
        if auth_header and auth_header == TOKEN:
            return await func(*args, request, **kwargs)
        raise(Exception('Invalid API token'))
    return wrapper
