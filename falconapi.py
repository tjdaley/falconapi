"""
falconapi.py - Falcon API

TODO: Set up opentelemetry
TODO: Set up an OpenTelemtry exporter for this API
https://grafana.com/blog/2022/05/10/how-to-collect-prometheus-metrics-with-the-opentelemetry-collector-and-grafana/
"""
from sys import prefix
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from routers.api_version import APIVersion
from routers.documents import router as documents
from routers.childsupport import router as childsupport
from routers.discovery_trackers import router as discovery_trackers
from routers.users import router as users
from models.response import Response

import settings  # NOQA

api_version = APIVersion(1, 0)
API_VERSION = api_version.to_str()
API_VERSION_PREFIX = f'/api/{API_VERSION}'
COPYRIGHT = f"Falcon API Copyright (c) 2022, Thomas J. Daley, Esq. - Version {API_VERSION} (updated 2023.11.05)"
SERVERS = [
    {
        "url": "https://api.jdbot.us",
        "description": "Production Server",
    },
]

app = FastAPI(
    title="Falcon API",
    description=COPYRIGHT,
    version=API_VERSION,
    prefix=API_VERSION_PREFIX,
    servers=SERVERS,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(discovery_trackers, prefix=API_VERSION_PREFIX)
app.include_router(users, prefix=API_VERSION_PREFIX)
app.include_router(documents, prefix=API_VERSION_PREFIX)
app.include_router(childsupport, prefix=API_VERSION_PREFIX)

@app.get(
    '/',
    response_model=Response,
    status_code=status.HTTP_200_OK,
    tags=['API'],
    summary='Get the API version'
)
async def root():
    return {"message": COPYRIGHT}

@app.get(
    '/privacy',
    status_code=status.HTTP_200_OK,
    tags=['API'],
    response_model=dict,
    summary='Get the privacy policy')
async def privacy():
    # read in our privacy policy from privacy.txt and privacy.md
    try:
        with open('privacy.txt', 'r') as f:
            privacy_txt = f.read()
    except:
        privacy_txt = None

    try:
        with open('privacy.md', 'r') as f:
            privacy_md = f.read()
    except:
        privacy_md = None
    return {"message": "Privacy Policy", "text": privacy_txt, "markdown": privacy_md}
