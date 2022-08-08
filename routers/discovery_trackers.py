"""
discovery_trackers.py - Falcon API Routers for Discovery Trackers
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Dict, List
from auth.handler import get_current_active_user
from models.document import Document
from models.response import Response, ResponseAndId
from models.tracker import Tracker
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
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=ResponseAndId, summary='Add a tracker')
async def create_tracker(tracker: Tracker, user: User = Depends(get_current_active_user)):
    if tracker.id in trackers:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tracker already exists")
    #if trackers.get_tracker_by_id(tracker.id):
    #    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Tracker already exists: {tracker.id}")
    tracker.username = user.username
    trackers[tracker.id] = tracker
    #trackers.create_tracker(tracker)
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
        #return trackers.get_trackers_by_username(username)

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

# Delete a tracker
@router.delete('/{tracker_id}', status_code=status.HTTP_200_OK, response_model=ResponseAndId, summary='Delete a tracker')
async def delete_tracker(tracker_id: str, user: User = Depends(get_current_active_user)):
    #tracker = trackers.get_tracker_by_id(tracker_id)
    tracker = trackers.get(tracker_id)
    if not tracker or (tracker.username != user.username and not user.is_admin):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found: {tracker_id}")
    #trackers.delete_tracker(tracker_id)
    del trackers[tracker_id]
    return {'message': "Tracker deleted", 'id': tracker_id}

# Add a document to the documents table
@router.post('/documents', status_code=status.HTTP_201_CREATED, response_model=ResponseAndId, summary='Add a document to the documents collection')
async def add_document(document: Document, user: User = Depends(get_current_active_user)):
    document.added_username = user.username
    documents[document.id] = document
    return {'message': "Document created", 'id': document.id}

# Add a document.id to the tracker document list
@router.patch('/{tracker_id}/documents/{document_id}', status_code=status.HTTP_202_ACCEPTED, response_model=ResponseAndId, summary='Link a document to a tracker')
async def add_document_to_tracker(tracker_id: str, document_id: str, user: User = Depends(get_current_active_user)):
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

    trackers.link_doc(tracker, document)
    return {'message': "Document linked to tracker", 'id': document_id}

# Get a document from a tracker
@router.get('/document', status_code=status.HTTP_200_OK, response_model=Document, summary='Get a document from a tracker')
async def get_document(tracker_id: str, document_id: str, user: User = Depends(get_current_active_user)):
    tracker = trackers.get(tracker_id)
    if tracker is None or tracker.username != user.username:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found: {tracker_id}")
    document = documents.get(document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document not found: {document_id}")
    if trackers.is_linked(tracker, document):
        return document
    return None

# Get all documents from a tracker
@router.get('/documents', status_code=status.HTTP_200_OK, response_model=List[Document], summary='Get all documents from a tracker')
async def get_documents(tracker_id: str, user: User = Depends(get_current_active_user)):
    tracker = trackers.get(tracker_id)
    if tracker is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found: {tracker_id}")
    if tracker.username != user.username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return documents.get_for_tracker(tracker)

# Delete a document from a tracker
@router.delete('/{tracker_id}/documents/{document_id}', status_code=status.HTTP_200_OK, response_model=ResponseAndId, summary='Delete a document from a tracker')
async def delete_document(tracker_id: str, document_id: str, user: User = Depends(get_current_active_user)):
    tracker = trackers.get(tracker_id)
    if tracker is None or tracker.username != user.username:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found: {tracker_id}")
    trackers.unlink_doc(tracker, document_id)
    return {'message': "Document unlinked from tracker", 'id': document_id}
