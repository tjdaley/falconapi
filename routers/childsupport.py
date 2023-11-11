"""
documents.py - Falcon API Routers for Documents
"""
from datetime import datetime
import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from models.childsupport import ChildSupportRequest, ChildSupportResponse
from routers.api_version import APIVersion
from util.childsupport import TxChildSupportCalculator


API_VERSION = APIVersion(1, 0).to_str()
ROUTE_PREFIX = '/txchildsupport'
LOGGER = logging.getLogger(f'falconapi{ROUTE_PREFIX}')

CALCULATOR = TxChildSupportCalculator()

router = APIRouter(
    tags=["Child Support Calculator"],
    prefix=ROUTE_PREFIX,
    responses={404: {"description": "Not found in Child Support Calculator"}},
)

# Add a document
@router.post('/calculate', status_code=status.HTTP_201_CREATED, response_model=ChildSupportResponse, summary='Calculate Child Support')
async def add_document(parms: ChildSupportRequest):
    return CALCULATOR.calculate(parms)
