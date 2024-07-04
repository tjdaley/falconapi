"""
users.py - Users Routes
"""
from typing import Optional, List
from pymongo.results import UpdateResult
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from models.client import Client
from models.user import User
from models.tracker import TrackerDatasetResponse
from routers.api_version import APIVersion
from database.clients_table import ClientsTable
from auth.handler import get_current_active_user


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

@router.get("/", response_model=List[Client], tags=["Clients"], summary="Get all by id, set id to '*' to get all")
async def get_clients(search_field: str, search_value: str, current_user: User = Depends(get_current_active_user)) -> TrackerDatasetResponse:
    """
    Return client's information.

    Args:
        id (str): The client's ID. Set to '*' to get all clients.

    Returns:
        Client: The Client object if the user is active, None otherwise.
    """
    args = {
        search_field: search_value,
        'username': current_user.email
    }
    data: List[Client] = CLIENTS_TABLE.get_clients(**args)
    return data

@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=Client,
    tags=["Clients"],
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
    xclient: Client = CLIENTS_TABLE.get_clients(client.billing_number, username=user_email)
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
    result = CLIENTS_TABLE.create_client(new_client)
    return {
        'id': new_client.id,
        'name': client.name,
        'billing_number': client.billing_number,
        'created_by': user_email,
        'enabled': True,
        # 'success': result.get('success', False)
        # '_id': str(result.inserted_id),
    }

@router.put(
    '/',
    status_code=status.HTTP_200_OK,
    response_model=Client,
    tags=["Clients"],
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
    result: UpdateResult = CLIENTS_TABLE.update_client(client, current_user.email)
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail=f"Client {client.id} not updated")
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
    result: UpdateResult = CLIENTS_TABLE.delete_client(id, current_user.email)
    if result.deleted_count == 0:
        raise HTTPException(status_code=400, detail=f"Client {id} not deleted")
    return {"message": "Client deleted successfully", "status": "success"}

@router.put(
    '/{id}/add_authorized_user',
    status_code=status.HTTP_200_OK,
    summary="Add an authorized user to a client"
) 
async def add_authorized_user(id: str, authorized_user: str, current_user: User = Depends(get_current_active_user)) -> dict:
    """
    Add an authorized user to a client

    Args:
        id (str): The client's ID.
        authorized_user (str): The authorized user's username.

    Returns:
        dict: A message indicating the user was added.
    """
    result: UpdateResult = CLIENTS_TABLE.add_authorized_user(id, current_user.email, authorized_user)
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail=f"User {authorized_user} not added to client {id}")
    return {"message": f"User {authorized_user} added to client {id}", "status": "success"}

@router.put(
    '/{id}/remove_authorized_user',
    status_code=status.HTTP_200_OK,
    summary="Remove an authorized user from a client"
)
async def remove_authorized_user(id: str, authorized_user: str, current_user: User = Depends(get_current_active_user)) -> dict:
    """
    Remove an authorized user from a client

    Args:
        id (str): The client's ID.
        authorized_user (str): The authorized user's username.

    Returns:
        dict: A message indicating the user was removed.
    """
    result: UpdateResult = CLIENTS_TABLE.remove_authorized_user(id, current_user.email, authorized_user)
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail=f"User {authorized_user} not removed from client {id}")
    return {"message": f"User {authorized_user} removed from client {id}", "status": "success"}
