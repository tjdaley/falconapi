"""
discovery_files.py - DiscoveryFile Routes
"""
from datetime import datetime
from typing import Optional, List, Union
from pymongo.results import UpdateResult, InsertOneResult, DeleteResult
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from models.client import Client
from models.user import User
from models.discovery_requests import DiscoveryFile, DiscoveryFileSummary
from routers.api_version import APIVersion
from database.discovery_files import DiscoveryFileTable
from auth.handler import get_current_active_user


API_VERSION = APIVersion(1, 0).to_str()
DISCOVERY_FILES_TABLE = DiscoveryFileTable(fail_silent=False)
ROUTE_PREFIX = '/discovery_files'

router = APIRouter(
    tags=["Discovery Files"],
    prefix=ROUTE_PREFIX,
    responses={404: {"description": "Discovery Files Route Not found"}}
)


@router.get("/", response_model=DiscoveryFile, tags=["Discovery Files"], summary="Get a discovery file")
async def get_discovery_file(file_id: str, current_user: User = Depends(get_current_active_user)):
    """
    Return information about a discovery file or all files.

    Args:
        file_id (str): The file ID to find or '*' for all.
        current_user (User): The current user.

    Returns:
        One or more DiscoveryFile objects.
    """
    data = DISCOVERY_FILES_TABLE.get(file_id, current_user.email)
    return data

@router.get("/client", response_model=List[DiscoveryFileSummary], tags=["Discovery Files"], summary="Get all discovery files for a client")
async def get_all_discovery_files(client_id: str, current_user: User = Depends(get_current_active_user)) -> List[DiscoveryFileSummary]:
    """
    Return information about all discovery files.

    Args:
        client_id (str): The client ID to search for.
        current_user (User): The current user.

    Returns:
        List[DiscoveryFileSummary]: A list of discovery files.
    """
    data = DISCOVERY_FILES_TABLE.get_all(client_id, current_user.email)
    return data

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=dict, tags=["Discovery Files"], summary="Add a discovery file")
async def add_discovery_file(discovery_file: DiscoveryFile, current_user: User = Depends(get_current_active_user)) -> dict:
    """
    Add a new discovery file

    Args:
        discovery_file (DiscoveryFile): The discovery file to add.

    Returns:
        dict: The status of the create operation.
    """
    discovery_file.created_by = current_user.email
    discovery_file.create_date = datetime.now().strftime("%Y-%m-%d")
    result = DISCOVERY_FILES_TABLE.add(discovery_file, current_user.email)
    return {
        'id': discovery_file.id,
        'success': result.inserted_id is not None,
    }

@router.put("/", status_code=status.HTTP_200_OK, response_model=dict, tags=["Discovery Files"], summary="Update a discovery file")
async def update_discovery_file(discovery_file: DiscoveryFile, current_user: User = Depends(get_current_active_user)) -> dict:
    """
    Update a discovery file

    Args:
        discovery_file (DiscoveryFile): The discovery file to update.

    Returns:
        dict: The status of the update operation.
    """
    result = DISCOVERY_FILES_TABLE.update(discovery_file, current_user.email)
    return {
        'id': discovery_file.id,
        'success': result.modified_count > 0,
    }

@router.delete("/{file_id}", status_code=status.HTTP_200_OK, summary="Delete a discovery file")
async def delete_discovery_file(file_id: str, current_user: User = Depends(get_current_active_user)) -> dict:
    """
    Delete a discovery file

    Args:
        file_id (str): The discovery file ID to delete.

    Returns:
        dict: A message indicating the file was deleted.
    """
    result = DISCOVERY_FILES_TABLE.delete(file_id, current_user.email)
    return {
        'id': file_id,
        'success': result.deleted_count > 0,
    }
