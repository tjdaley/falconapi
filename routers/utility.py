"""
utility.py - Falcon API Routers for a collection of utility functions
"""
from datetime import datetime
import logging
import os
from dotenv import load_dotenv
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from routers.api_version import APIVersion
from util.utility import Utilities
from models.realproperty import RealPropertyInfoRequest, RealPropertyInfoResponse
from models.queue_request import QueueRequest
from models.user import User
from distributed_work_queue.workqueue import DistributedWorkQueue
from distributed_work_queue.jobstatus import JobStatus
from auth.handler import get_current_active_user

load_dotenv()
API_VERSION = APIVersion(1, 0).to_str()
ROUTE_PREFIX = '/util'
LOGGER = logging.getLogger(f'falconapi{ROUTE_PREFIX}')
# Global job status object
JOBSTATUS = JobStatus()


router = APIRouter(
    tags=["Utility Functions"],
    prefix=ROUTE_PREFIX,
    responses={404: {"description": "Not found in Utility Functions"}},
)

work_queue = DistributedWorkQueue(
    os.getenv("WORK_QUEUE_HOST", 'localhost'),
    int(os.getenv("WORK_QUEUE_PORT", "6379")),
    int(os.getenv("WORK_QUEUE_DB", "0")),
    os.getenv("WORK_QUEUE_NAME_CLASSIFY", 'classification_queue'),
)

# Retrieve property description and valuation data from ATTOM Data Solutions
@router.get('/property', status_code=status.HTTP_200_OK, response_model=RealPropertyInfoResponse, summary='Get Property Details')
# async def get_property_details(info_request: RealPropertyInfoRequest):
async def get_property_details(address: str, city: str, state: str, zip_code: str):
    """
    Retrieve property description and valuation data from ATTOM Data Solutions

    Args:
        address (str): Street address
        city (str): City
        state (str): State
        zip_code (str): Zip code

    Returns:
        dict: Property details
    """
    return Utilities.get_property_details(address, city, state, zip_code)


# Queue a request for processing
@router.post('/enqueue', status_code=status.HTTP_201_CREATED, summary='Queue a Request')
async def queue_request(
    request: QueueRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_active_user),
):
    """
    Queue a request for processing

    Args:
        request (QueueRequest): Request to be queued
        background_tasks (BackgroundTasks): Background tasks to be executed
    """
    if request.task == 'stop':
        LOGGER.info(f"Ignoring {request.task} task")
        return {"message": f"{request.task} task ignored, fucko", "id": request.request_id}
    work_queue.enqueue_work(request.json())
    JOBSTATUS.add_job(request.request_id)
    return {"message": f"{request.task} task queued", "id": request.request_id}

# Check the status of a queued request
@router.get('/status', status_code=status.HTTP_200_OK, summary='Check the Status of a Queued Request')
async def queue_status(request_id: str, user: User = Depends(get_current_active_user)):
    return JOBSTATUS.get_status(request_id)
