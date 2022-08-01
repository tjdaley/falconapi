"""
falconapi.py - Falcon API
"""
from sys import prefix
from fastapi import FastAPI, status
from routers.api_version import APIVersion
from routers.discovery_trackers import router as discovery_trackers
from routers.users import router as users
from models.response import Response

import settings  # NOQA

api_version = APIVersion(1, 0)
API_VERSION = api_version.to_str()
API_VERSION_PREFIX = f'/api/{API_VERSION}'

app = FastAPI(
    title="Falcon API",
    description=f"Falcon API Copyright (c) 2022, Thomas J. Daley, Esq. - Version {API_VERSION}",
    version=API_VERSION,
    prefix=API_VERSION_PREFIX,
)

app.include_router(discovery_trackers, prefix=API_VERSION_PREFIX)
app.include_router(users, prefix=API_VERSION_PREFIX)

@app.get(
    '/',
    response_model=Response,
    status_code=status.HTTP_200_OK,
    tags=['API'],
    summary='Get the API version'
)
async def root():
    return {"message": f"Falcon API Copyright (c) 2022, Thomas J. Daley, Esq. - Version {API_VERSION}"}
