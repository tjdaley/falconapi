"""
utility.py - Falcon API Routers for a collection of utility functions
"""
from datetime import datetime
import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from routers.api_version import APIVersion
from util.utility import Utilities


API_VERSION = APIVersion(1, 0).to_str()
ROUTE_PREFIX = '/util'
LOGGER = logging.getLogger(f'falconapi{ROUTE_PREFIX}')


router = APIRouter(
    tags=["Utility Functions"],
    prefix=ROUTE_PREFIX,
    responses={404: {"description": "Not found in Utility Functions"}},
)

# Retrieve property description and valuation data from ATTOM Data Solutions
@router.get('/property', status_code=status.HTTP_200_OK, summary='Get Property Details')
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
