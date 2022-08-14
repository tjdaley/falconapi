"""
discovery_trackers.py - Falcon API Routers for Discovery Trackers
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import List
from auth.handler import get_current_active_user
from models.document import Document
from models.response import Response, ResponseAndId
from models.tracker import Tracker, TrackerUpdate
from models.user import User
from database.trackers_table import TrackersDict
from database.documents_table import DocumentsDict
from routers.api_version import APIVersion


API_VERSION = APIVersion(1, 0).to_str()
ROUTE_PREFIX = '/trackers'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f'api/{API_VERSION}{ROUTE_PREFIX}/token')

router = APIRouter(
    tags=["Discovery Trackers"],
    prefix=ROUTE_PREFIX,
    responses={404: {"description": "Not found"}}
)

trackers = TrackersDict()
documents = DocumentsDict()

# Add a tracker
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=ResponseAndId, summary='Create a tracker')
async def create_tracker(tracker: Tracker, user: User = Depends(get_current_active_user)):
    if tracker.id in trackers:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Tracker already exists: {tracker.id}")
    tracker.username = user.username
    trackers[tracker.id] = tracker
    return {'message': "Tracker created", 'id': tracker.id}

# Get a tracker by Tracker ID
@router.get('/', status_code=status.HTTP_200_OK, response_model=Tracker, summary='Get a tracker by Tracker ID')
async def get_tracker(tracker_id: str, user: User = Depends(get_current_active_user)):
    tracker = trackers.get(tracker_id)
    if not tracker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found: {tracker_id}")
    if tracker.username != user.username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return tracker

# Get all trackers for a user
@router.get('/user', status_code=status.HTTP_200_OK, response_model=List[Tracker], summary='Get all trackers for a user')
async def get_trackers_for_user(username: str | None = None, user: User = Depends(get_current_active_user)):
    if username is None:
        username = user.username
    if user.admin or user.username == username:
        return trackers.get_for_username(username)

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

# Update a tracker
@router.put('/', status_code=status.HTTP_200_OK, response_model=ResponseAndId, summary='Update a tracker')
async def update_tracker(tracker: TrackerUpdate, user: User = Depends(get_current_active_user)):
    existing_tracker = trackers.get(tracker.id)
    if not existing_tracker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found: {existing_tracker.id}")
    if existing_tracker.username != user.username and not user.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    trackers[tracker.id] = tracker
    return {'message': "Tracker updated", 'id': tracker.id}

# Delete a tracker
@router.delete('/', status_code=status.HTTP_200_OK, response_model=ResponseAndId, summary='Delete a tracker')
async def delete_tracker(tracker_id: str, user: User = Depends(get_current_active_user)):
    tracker = trackers.get(tracker_id)
    if not tracker or (tracker.username != user.username and not user.is_admin):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found: {tracker_id}")
    del trackers[tracker_id]
    return {'message': "Tracker deleted", 'id': tracker_id}

# Link a document.id to the tracker document list
@router.patch('/{tracker_id}/documents/link/{document_id}', status_code=status.HTTP_202_ACCEPTED, response_model=ResponseAndId, summary='Link a document to a tracker')
async def link_document(tracker_id: str, document_id: str, user: User = Depends(get_current_active_user)):
    tracker = trackers.get(tracker_id)
    if not tracker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found: {tracker_id}")
    if tracker.username != user.username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    document = documents.get(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document not found: {document_id}")
    if document.id in tracker.documents:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Document already linked: {document_id}")

    r = trackers.link_doc(tracker, document)
    return {'message': "Document linked to tracker", 'id': document_id}

# Unlink a document from a tracker
@router.patch('/{tracker_id}/documents/unlink/{document_id}', status_code=status.HTTP_200_OK, response_model=ResponseAndId, summary='Delete a document from a tracker')
async def unlink_document(tracker_id: str, document_id: str, user: User = Depends(get_current_active_user)):
    tracker = trackers.get(tracker_id)
    if tracker is None or tracker.username != user.username:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found: {tracker_id}")
    trackers.unlink_doc(tracker, document_id)
    return {'message': "Document unlinked from tracker", 'id': document_id}

# Get all documents from a tracker
@router.get('/{tracker_id}/documents', status_code=status.HTTP_200_OK, response_model=List[Document], summary='Get all documents from a tracker')
async def get_documents(tracker_id: str, user: User = Depends(get_current_active_user)):
    tracker = trackers.get(tracker_id)
    if tracker is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found: {tracker_id}")
    if tracker.username != user.username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return documents.get_for_tracker(tracker)
