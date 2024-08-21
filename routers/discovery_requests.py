"""
discovery_requests.py - DiscoveryRequests Routes
"""
from typing import Optional, List
from pymongo.results import UpdateResult, InsertOneResult, DeleteResult
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from models.client import Client
from models.user import User
from models.discovery_requests import DiscoveryRequest
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


@router.get("/file", response_model=List[DiscoveryRequest], tags=["Discovery Requests"], summary="Get all requests for a file")
async def get_requests(file_id: str, current_user: User = Depends(get_current_active_user)) -> List[DiscoveryRequest]:
    """
    Return discovery requests for the specified file.

    Args:
        file_id (str): The file ID to search for.
        current_user (User): The current user.

    Returns:
        ServedRequests: A list of served requests.
    """
    data: List[DiscoveryRequest] = DISCOVERY_REQUESTS_TABLE.get_all(file_id, current_user.email)
    return data

@router.get("/", response_model=DiscoveryRequest, tags=["Discovery Requests"], summary="Get a discovery request")
async def get_request(request_id: str, current_user: User = Depends(get_current_active_user)) -> DiscoveryRequest:
    """
    Return information about all served requests.

    Args:
        request_id (str): The request ID to search for.
        current_user (User): The current user.

    Returns:
        DiscoveryRequest: A single request from a file
    """
    data: DiscoveryRequest = DISCOVERY_REQUESTS_TABLE.get(request_id, current_user.email)
    return data

@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=dict,
    tags=["Discovery Requests"],
    summary="Insert a single discovery request"
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
    user_email = current_user.email

    result: InsertOneResult = DISCOVERY_REQUESTS_TABLE.add(request, user_email)
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
    result: UpdateResult = DISCOVERY_REQUESTS_TABLE.update(request, current_user.email)
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail=f"Discovery Request {request.id} not updated")
    return result

@router.delete(
    '/{request_id}',
    status_code=status.HTTP_200_OK,
    summary="Delete a discovery request"
)
async def delete_request(request_id: str, current_user: User = Depends(get_current_active_user)) -> dict:
    """
    Delete a discovery request

    Args:
        id (str): The discovery request ID to delete.

    Returns:
        dict: A message indicating the request was deleted.
    """
    result: DeleteResult = DISCOVERY_REQUESTS_TABLE.delete(request_id, current_user.email)
    if result.deleted_count == 0:  # We don't delete, we just update the enabled flag
        return {"message": "Discovery request not deleted", "success": False}
    return {"message": "Discovery reqeust deleted successfully", "success": True}
