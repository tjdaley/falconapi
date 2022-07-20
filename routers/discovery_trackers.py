"""
discovery_trackers.py - Falcon API Routers for Discovery Trackers
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, List
from models.document import Document
from models.response import Response, ResponseAndId
from models.tracker import Tracker

router = APIRouter(
    tags=["Discovery Trackers"],
    prefix="/trackers",
    responses={404: {"description": "Not found"}}
)

trackers: Dict[str, Tracker] = {}

# Add a tracker
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=ResponseAndId, summary='Add a tracker')
async def create_tracker(tracker: Tracker):
    if tracker.id in trackers:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Tracker already exists: {tracker.id}")
    trackers[tracker.id] = tracker
    return {'message': "Tracker created", 'id': tracker.id}

# Get a tracker by Tracker ID
@router.get('/{tracker_id}', status_code=status.HTTP_200_OK, response_model=Tracker, summary='Get a tracker by Tracker ID')
async def get_tracker(tracker_id: str):
    if tracker_id not in trackers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found: {tracker_id}")
    return trackers[tracker_id]

# Get all trackers for a user
@router.get('/user/{user_name}', status_code=status.HTTP_200_OK, response_model=List[Tracker], summary='Get all trackers for a user')
async def get_trackers_for_user(user_name: str):
    return [tracker for tracker in trackers.values() if tracker.user_name == user_name]

# Delete a tracker
@router.delete('/{tracker_id}', status_code=status.HTTP_200_OK, response_model=ResponseAndId, summary='Delete a tracker')
async def delete_tracker(tracker_id: str):
    if tracker_id not in trackers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found: {tracker_id}")
    del trackers[tracker_id]
    return {'message': "Tracker deleted", 'id': tracker_id}

# Add a document to a tracker
@router.post('/{tracker_id}/documents', status_code=status.HTTP_201_CREATED, response_model=ResponseAndId, summary='Add a document to a tracker')
async def add_document_to_tracker(document: Document):
    if document.tracker_id not in trackers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found:")
    if document.id not in trackers[document.tracker_id].documents:
        trackers[document.tracker_id].documents[document.id] = document
        return {'message': "Document added", 'id': document.id}
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Document already exists: {document.path}")

# Get a document from a tracker
@router.get('/{tracker_id}/documents/{document_id}', status_code=status.HTTP_200_OK, response_model=Document, summary='Get a document from a tracker')
async def get_document(tracker_id: str, document_id: str):
    tracker = trackers.get(tracker_id, None)
    if tracker is None:
        raise HTTPException(status_code=404, detail=f"Tracker not found: {tracker_id}")
    doc = tracker.documents.get(document_id, None)
    if doc is None:
        raise HTTPException(status_code=404, detail=f"Document not found: {id}")
    return doc

# Get all documents from a tracker
@router.get('/{tracker_id}/documents', status_code=status.HTTP_200_OK, response_model=Dict[str, Document], summary='Get all documents from a tracker')
async def get_documents(tracker_id: str):
    tracker = trackers.get(tracker_id, None)
    if tracker is None:
        raise HTTPException(status_code=404, detail=f"Tracker not found: {tracker_id}")
    return tracker.documents

# Delete a document from a tracker
@router.delete('/{tracker_id}/documents/{document_id}', status_code=status.HTTP_200_OK, response_model=ResponseAndId, summary='Delete a document from a tracker')
async def delete_document(tracker_id: str, document_id: str):
    tracker = trackers.get(tracker_id, None)
    if tracker is None:
        raise HTTPException(status_code=404, detail=f"Tracker not found: {tracker_id}")
    doc = tracker.documents.get(document_id, None)
    if doc is None:
        raise HTTPException(status_code=404, detail=f"Document not found: {document_id}")
    del tracker.documents[document_id]
    return {'message': "Document deleted", 'id': document_id}
