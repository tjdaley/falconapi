"""
discovery_requests.py - DiscoveryRequests Routes
"""
from typing import Optional, List
from pymongo.results import UpdateResult, InsertOneResult, DeleteResult
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from models.client import Client
from models.user import User
from models.discovery_requests import DiscoveryRequest, DiscoveryRequests, ServedRequest, ServedRequests
from routers.api_version import APIVersion
from database.discovery_requests import DiscoveryRequestsTable
from auth.handler import get_current_active_user


API_VERSION = APIVersion(1, 0).to_str()
DISCOVERY_REQUESTS_TABLE = DiscoveryRequestsTable(fail_silent=False)
ROUTE_PREFIX = '/discovery_requests'

router = APIRouter(
    tags=["Discovery Requests"],
    prefix=ROUTE_PREFIX,
    responses={404: {"description": "Discovery Requests Route Not found"}}
)


@router.get("/", response_model=ServedRequests, tags=["Discovery Requests"], summary="Get all by client_id, set client_id to '*' to get all")
async def get_request_service(search_field: str, search_value: str, current_user: User = Depends(get_current_active_user)) -> ServedRequests:
    """
    Return information about discovery requests.

    Args:
        search_field (str): The field to search within ['client_id', 'billing_number'].
        search_value (str): The value to search for. If searching by 'id', set to '*' to get all clients.
        current_user (User): The current user.

    Returns:
        ServedRequests: A list of served requests.
    """
    valid_search_fields = ['client_id', 'billing_number']
    if search_field not in valid_search_fields:
        raise HTTPException(status_code=400, detail=f"Invalid search field {search_field}. Valid search fields are {valid_search_fields}")
    args = {
        search_field: search_value,
        'username': current_user.email
    }
    data: ServedRequests = DISCOVERY_REQUESTS_TABLE.get_request_service_list(**args)
    return data

@router.get("/requests", response_model=ServedRequests, tags=["Discovery Requests"], summary="Get all served requests")
async def get_requests(client_id: str, party_name: str, discovery_type: str, service_date: str, current_user: User = Depends(get_current_active_user)) -> ServedRequests:
    """
    Return information about all served requests.

    Args:
        client_id (str): The client ID to search for.
        party_name (str): The user who served the request.
        discovery_type (str): The type of discovery request.
        service_date (str): The date the request was served.
        current_user (User): The current user.

    Returns:
        ServedRequests: A list of served requests.
    """
    data: ServedRequests = DISCOVERY_REQUESTS_TABLE.get_requests(party_name, service_date, discovery_type, client_id, current_user.email)
    return data

@router.get("/{id}", response_model=DiscoveryRequest, tags=["Discovery Requests"], summary="Get a specific discovery request")
async def get_request(id: str, current_user: User = Depends(get_current_active_user)) -> DiscoveryRequest:
    """
    Return information about a specific discovery request.

    Args:
        id (str): The discovery request ID.
        current_user (User): The current user.

    Returns:
        DiscoveryRequest: The discovery request.
    """
    data: DiscoveryRequest = DISCOVERY_REQUESTS_TABLE.get_request(id, current_user.email)
    return data

@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=dict,
    tags=["Discovery Requests"],
    summary="Insert a specific discovery request"
)
async def add_request(request: DiscoveryRequest, current_user: User = Depends(get_current_active_user)) -> dict:
    """
    Add a new discovery request

        Args:
            request (DiscoveryRequest): The discovery request to add

        Returns:
            dict: The status of the create operation.

        Raises:
            HTTPException: If the user is not permitted to insert requests for the specified client_id.
    """
    print(f"Adding request for {current_user.email}")
    print(f"Client ID: {request.client_id}")
    user_email = current_user.email

    result: InsertOneResult = DISCOVERY_REQUESTS_TABLE.create_request(request, user_email)
    return {
        'id': request.id,
        'success': result.inserted_id is not None,
    }

@router.put(
    '/',
    status_code=status.HTTP_200_OK,
    response_model=dict,
    tags=["Discovery Requests"],
    summary="Update a discovery request"
)
async def update_request(request: DiscoveryRequest, current_user: User = Depends(get_current_active_user)) -> dict:
    """
    Update a discovery request

    Args:
        request (DiscoveryRequest): The discovery request data to update.

    Returns:
        dict: The updated client record.
    """
    result: UpdateResult = DISCOVERY_REQUESTS_TABLE.update_request(request, current_user.email)
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail=f"Discovery Request {request.id} not updated")
    return result

@router.delete(
    '/{id}',
    status_code=status.HTTP_200_OK,
    summary="Delete a discovery request"
)
async def delete_request(id: str, current_user: User = Depends(get_current_active_user)) -> dict:
    """
    Delete a discovery request

    Args:
        id (str): The discovery request ID to delete.

    Returns:
        dict: A message indicating the request was deleted.
    """
    result: DeleteResult = DISCOVERY_REQUESTS_TABLE.delete_request(id, current_user.email)
    if result.deleted_count == 0:  # We don't delete, we just update the enabled flag
        return {"message": "Discovery request not deleted", "success": False}
    return {"message": "Discovery reqeust deleted successfully", "success": True}
