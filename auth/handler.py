_id"""
handler.py - Handle Authentication
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
import time
from typing import Dict, Optional
import os
from jose import jwt, JWTError
from datetime import datetime, timedelta
# from routers.users import USERS_TABLE
import settings  # NOQA
from database.users_table import UsersTable
from routers.api_version import APIVersion
from models.user import User


# We want an exception to be raised if and of these three variables is missing
JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
JWT_ALGORITHM = os.environ['JWT_ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ['JWT_ACCESS_TOKEN_EXPIRE_MINUTES'])


API_VERSION = APIVersion(1, 0).to_str()
USERS_TABLE = UsersTable()
ROUTE_PREFIX = '/users'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f'api/{API_VERSION}{ROUTE_PREFIX}/token')

# Classes for creating tokens
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str = Field(default='')  # the field name when serialized is 'user_id', db name is 'id'
    twilio_factor_id: str = Field(default='')


class TokenData(BaseModel):
    username: Optional[str] = None


def token_response(token: str, user: User) -> Token:
    token_info = {
        "access_token": token,
        "token_type": "bearer"
    }
    return Token(**user.dict(), **token_info, user_id=user.id)

"""
Create an access token for a user.

Args:
    username (str): The username of the user.

Returns:
    str: The JWT-encoded access token.
"""
def create_access_token(user: User, expires_delta: timedelta = None) -> Dict[str, str]:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": user.username,
        "exp": expire
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    return token_response(token, user)

"""
Decode JWT token and return the username.

Args:
    token (str): The JWT token we received from the client.

Returns:
    dict: The decoded JWT token containing at least the keys 'sub' and 'exp'.
"""
def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token.get('exp', 0) >= time.time() else None
    except:
        return {}

"""
Get the user whose username is contained in the token.

Args:
    token (str): The token we received from the client.

Returns:
    User: The user object if the token was decoded and the user is in the DB, None otherwise.

Raises:
    HTTPException: If the token is invalid, or if the user is not in the DB.
"""
async def get_current_user(token: str = Depends(oauth2_scheme)):
    invalid_credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credentials are invalid (missing sub aka username)",
        headers={"WWW-Authenticate": "Bearer"},
    )
    decode_credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unable to decode credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unable to find user in database",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_jwt(token)
        username: str = payload.get("sub")
        if username is None:
            raise invalid_credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise decode_credentials_exception
    user = USERS_TABLE.get_user_by_username(token_data.username)
    if user is None:
        raise user_credentials_exception
    return user     

"""
Verify that current user is active.

Args:
    current_user (User): The User object associated with the credentials given.

Returns:
    User: The User object if the user is active, None otherwise.

Raises:
    HTTPException: If the user is not active.
"""
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
