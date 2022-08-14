"""
users.py - Users Routes
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from models.user import User, UserRegistration, RegistrationResponse
from routers.api_version import APIVersion
from database.users_table import UsersTable
from auth.handler import create_access_token, get_current_active_user, Token


API_VERSION = APIVersion(1, 0).to_str()
USERS_TABLE = UsersTable()
ROUTE_PREFIX = '/users'

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    tags=["Users"],
    prefix=ROUTE_PREFIX,
    responses={404: {"description": "Not found"}}
)

# Class for responding to user registration
class InsertException(BaseModel):
    detail: Optional[str] = "User already exists"

"""
Verify that the password we received, when hashed, matches the hashed password in the database.

Args:
    plain_password (str): The password we received from the client.
    hashed_password (str): The hashed password stored in the database.

Returns:
    bool: True if the passwords match, False otherwise.
"""
def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

"""
Hash the password before storing it in the database.

Args:
    password (str): The password we received from the client.

Returns:
    str: The hashed password.
"""
def get_password_hash(password) -> str:
    return pwd_context.hash(password)

"""
Authenticate a user with username and password.

Args:
    username (str): The username we received from the client.
    password (str): The password we received from the client.

Returns:
    User: The user object if the username and password match, None otherwise.
"""
def authenticate_user(username: str, password: str) -> User:
    user = USERS_TABLE.get_user_by_username(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

"""
Authenticate a user with username and password.

Args: (in formdata)
    username (str): The username we received from the client. 
    password (str): The password we received from the client.

Returns:
    dict: 'access_token' and 'token_type' if the username and password match, otherwise an error message.

Raises:
    HTTPException: If the username or password is invalid.
"""
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_response = create_access_token(user.username)
    return token_response

"""
Return current user's information.

Args:
    None (token is provided in the Authorization header)

Returns:
    User: The User object if the user is active, None otherwise.
"""
@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)) -> User:
    return current_user

"""
Register a new user

    Args:
        user_registration (UserRegistration): The user registration data we received from the client.

    Returns:
        RegistrationResponse: The user registration data if the user was created, None otherwise.

    Raises:
        HTTPException: If the user already exists.
"""
@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=RegistrationResponse,
    responses={400: {"model": InsertException, "description": "User already exists"}},
    summary="Register a new user"
)
async def register_user(user_registration: UserRegistration) -> RegistrationResponse:
    user = USERS_TABLE.get_user_by_username(user_registration.username)
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = get_password_hash(user_registration.password)
    user = User(
        username=user_registration.username,
        email=user_registration.email,
        full_name=user_registration.full_name,
        admin=False,
        disabled=False,
        hashed_password=hashed_password
    )
    result = USERS_TABLE.create_user(user)
    return {
        'username': user.username,
        'message': 'User created successfully',
        'status': 'success',
        'user_id': str(result.inserted_id)
    }
