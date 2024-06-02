"""
users.py - Users Routes
"""
import json
import os
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
SITE_CODES_FILE = 'site_codes.json'

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    tags=["Users"],
    prefix=ROUTE_PREFIX,
    responses={404: {"description": "Not found"}}
)

# Class for responding to user registration
class InsertException(BaseModel):
    """A class for responding to user registration errors"""
    detail: Optional[str] = "User already exists"

def verify_password(plain_password, hashed_password) -> bool:
    """
    Verify that the password we received, when hashed, matches the hashed password in the database.

    Args:
        plain_password (str): The password we received from the client.
        hashed_password (str): The hashed password stored in the database.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password) -> str:
    """
    Hash the password before storing it in the database.

    Args:
        password (str): The password we received from the client.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str) -> User:
    """
    Authenticate a user with username and password.

    Args:
        username (str): The username we received from the client.
        password (str): The password we received from the client.

    Returns:
        User: The user object if the username and password match, None otherwise.
    """
    user = USERS_TABLE.get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    """
    Authenticate a user with token.

    Args: (in formdata)
        response_model (Token): The token we received from the client. 

    Returns:
        dict: 'access_token' and 'token_type' if the username and password match, otherwise an error message.

    Raises:
        HTTPException: If the username or password is invalid.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_response = create_access_token(user)
    return token_response

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Return current user's information.

    Args:
        None (token is provided in the Authorization header)

    Returns:
        User: The User object if the user is active, None otherwise.
    """
    return current_user

@router.get(
    '/lookup',
    status_code=status.HTTP_200_OK,
    response_model=User,
    responses={404: {'model': LookupException, 'description': "User ID not found"}},
    summary="Lookup a user by id"
)
async def get_user(user_id: str) -> User:
    """
    Lookup a user by user ID.

    Args:
        user_id (str): id from the users table.

    Returns:
        User record or error
    """
    user = USERS_TABLE.get_user_by_id(user_id)
    result_user = User(user)
    return result_user.json()

@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=RegistrationResponse,
    responses={400: {"model": InsertException, "description": "User already exists"}},
    summary="Register a new user"
)
async def register_user(user_registration: UserRegistration) -> RegistrationResponse:
    """
    Register a new user

        Args:
            user_registration (UserRegistration): The user registration data we received from the client.

        Returns:
            RegistrationResponse: The user registration data if the user was created, None otherwise.

        Raises:
            HTTPException: If the user already exists.
    """
    if not validate_site_code(user_registration.site_code):
        raise HTTPException(status_code=403, detail="Unauthorized site for user registration")
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
        hashed_password=hashed_password,
        twilio_factor_id=user_registration.twilio_factor_id,
        phone_number=user_registration.phone_number
    )
    result = USERS_TABLE.create_user(user)
    return {
        'username': user.username,
        'message': 'User created successfully',
        'status': 'success',
        'user_id': str(result.inserted_id)
    }

#----------------------------------------------------------
# U T I L I T Y   F U N C T I O N S
#----------------------------------------------------------
def validate_site_code(site_code: str) -> bool:
    """
    Validate the site code for a user registration request.

    Args:
        site_code(str): Site code from site seeking to register user

    Returns:
        (bool): True is validated otherwise False.
    """
    with open(SITE_CODES_FILE, 'r') as file:
        site_codes = json.load(file)
    return site_code in site_codes
