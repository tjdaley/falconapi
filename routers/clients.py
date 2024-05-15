"""
users.py - Users Routes
"""
from typing import Optional, List, Union
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from models.client import Client
from models.user import User
from routers.api_version import APIVersion
from database.clients_table import ClientsTable
from auth.handler import create_access_token, get_current_active_user, Token


API_VERSION = APIVersion(1, 0).to_str()
CLIENTS_TABLE = ClientsTable()
ROUTE_PREFIX = '/clients'

router = APIRouter(
    tags=["Clients"],
    prefix=ROUTE_PREFIX,
    responses={404: {"description": "Not found"}}
)

# Class for responding to client registration
class InsertException(BaseModel):
    """A class for responding to client registration errors"""
    detail: Optional[str] = "Client already exists"

@router.get("/", response_model=Union[List[Client], Client] ,tags=["Clients"], summary="Get all clients")
async def get_client(id: str, current_user: User = Depends(get_current_active_user)) -> Client:
    """
    Return client's information.

    Args:
        id (str): The client's ID.

    Returns:
        User: The User object if the user is active, None otherwise.
    """
    return CLIENTS_TABLE.get_client(id, current_user.email)

@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=Client,
    responses={400: {"model": InsertException, "description": "Client already exists"}},
    summary="Register a new client"
)
async def register_client(client: Client, current_user: User = Depends(get_current_active_user)) -> Client:
    """
    Register a new client

        Args:
            client (Client): The client registration data we received from the client.

        Returns:
            Client: The Client record  if the user was created, None otherwise.

        Raises:
            HTTPException: If the client already exists.
    """
    user_email = current_user.email
    xclient: Client = CLIENTS_TABLE.get_client_by_billing_number(client.billing_number, username=user_email)
    if xclient:
        raise HTTPException(status_code=400, detail=f"Client already exists (billing number {client.billing_number})")
    xclient: Client = CLIENTS_TABLE.get_client(client.id, username=user_email)
    if xclient:
        raise HTTPException(status_code=400, detail=f"Client already exists (id {client.id})")

    new_client = Client(
        name=client.name,
        billing_number=client.billing_number,
        created_by=user_email,
        enabled=True,
    )
    result = CLIENTS_TABLE.create_client(client)
    return {
        'id': new_client.id,
        'name': client.name,
        'billing_number': client.billing_number,
        'created_by': current_user.email,
        'enabled': True,
        'message': 'Client created successfully',
        'status': 'success',
        '_id': str(result.inserted_id),
    }

@router.put(
    '/',
    status_code=status.HTTP_200_OK,
    response_model=Client,
    summary="Update a client"
)
async def update_client(client: Client, current_user: User = Depends(get_current_active_user)) -> Client:
    """
    Update a client

    Args:
        client (Client): The client data to update.

    Returns:
        Client: The updated client record.
    """
    CLIENTS_TABLE.update_client(client, current_user.email)
    return client

@router.delete(
    '/{id}',
    status_code=status.HTTP_200_OK,
    summary="Delete a client"
)
async def delete_client(id: str, current_user: User = Depends(get_current_active_user)) -> dict:
    """
    Delete a client

    Args:
        id (str): The client ID to delete.

    Returns:
        dict: A message indicating the client was deleted.
    """
    CLIENTS_TABLE.delete_client(id, current_user.email)
    return {"message": "Client deleted successfully", "status": "success"}
