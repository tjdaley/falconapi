"""
falconapi.py - Falcon API
"""
from sys import prefix
from fastapi import FastAPI, status
from routers.discovery_trackers import router as discovery_trackers
from models.response import Response

API_VERSION_PREFIX = "/api/v1"

app = FastAPI(
    title="Falcon API",
    description="Falcon API Copyright (c) 2022, Thomas J. Daley, Esq. - Version 1.0.0",
    version="1.0.0",
    prefix=API_VERSION_PREFIX,
)

app.include_router(discovery_trackers, prefix=API_VERSION_PREFIX)

@app.get('/', response_model=Response, status_code=status.HTTP_200_OK, tags=['API'], summary='Get the API version')
async def root():
    return {"message": "Falcon API Copyright (c) 2022, Thomas J. Daley, Esq. - Version 1.0.0"}
