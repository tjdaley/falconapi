"""
users.py - Users Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
import os
from passlib.context import CryptContext
from models.user import User, UserRegistration, RegistrationResponse
from routers.api_version import APIVersion
from database.users_table import UsersTable


API_VERSION = APIVersion(1, 0).to_str()
USERS_TABLE = UsersTable()
ROUTE_PREFIX = '/users'

# We want an exception to be raised if and of these three variables is missing
SECRET_KEY = os.environ['JWT_SECRET_KEY']
ALGORITHM = os.environ['JWT_ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ['JWT_ACCESS_TOKEN_EXPIRE_MINUTES'])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f'api/{API_VERSION}{ROUTE_PREFIX}/token')

router = APIRouter(
    tags=["Users"],
    prefix=ROUTE_PREFIX,
    responses={404: {"description": "Not found"}}
)

# Classes for creating tokens
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

# Class for responding to user registration
class InsertException(BaseModel):
    detail: str | None = "User already exists"

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
Create an access token for a user.

Args:

"""
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token):
    return USERS_TABLE.get_user_by_token(token)

def hash_password(password: str):
    return "$$" + password

"""
Get the user whose username is contained in the token.

Args:
    token (str): The token we received from the client.

Returns:
    User: The user object if the token was decoded and the user is in the DB, None otherwise.
"""
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = USERS_TABLE.get_user_by_username(token_data.username)
    if user is None:
        raise credentials_exception
    return user     

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=RegistrationResponse,
    responses={400: {"model": InsertException, "description": "User already exists"}},
    summary="Register a new user"
)
async def register_user(user_registration: UserRegistration):
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
