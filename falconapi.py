"""
falconapi.py - Falcon API
"""
from fastapi import FastAPI, HTTPException, status
from typing import Dict, List
from models.document import Document
from models.response import Response
from models.tracker import Tracker

app = FastAPI(
    title="Falcon API",
    description="Falcon API Copyright (c) 2022, Thomas J. Daley, Esq. - Version 1.0.0",
    version="1.0.0"
)

trackers: Dict[str, Tracker] = {}

@app.get('/', response_model=Response, status_code=status.HTTP_200_OK, tags=['api'], summary='Get the API version')
async def root():
    return {"message": "Falcon API Copyright (c) 2022, Thomas J. Daley, Esq. - Version 1.0.0"}

# Add a tracker
@app.post('/api/v1/trackers', status_code=status.HTTP_201_CREATED, response_model=Response, tags=['trackers'], summary='Add a tracker')
async def create_tracker(tracker: Tracker):
    if tracker.id in trackers:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Tracker already exists: {tracker.id}")
    trackers[tracker.id] = tracker
    return {'message': "Tracker created"}

# Get a tracker by Tracker ID
@app.get('/api/v1/trackers/{tracker_id}', status_code=status.HTTP_200_OK, response_model=Tracker, tags=['trackers'], summary='Get a tracker by Tracker ID')
async def get_tracker(tracker_id: str):
    if tracker_id not in trackers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found: {tracker_id}")
    return trackers[tracker_id]

# Get all trackers for a user
@app.get('/api/v1/trackers/user/{user_name}', status_code=status.HTTP_200_OK, response_model=List[Tracker], tags=['trackers'], summary='Get all trackers for a user')
async def get_trackers_for_user(user_name: str):
    return [tracker for tracker in trackers.values() if tracker.user_name == user_name]

# Delete a tracker
@app.delete('/api/v1/trackers/{tracker_id}', status_code=status.HTTP_200_OK, response_model=Response, tags=['trackers'], summary='Delete a tracker')
async def delete_tracker(tracker_id: str):
    if tracker_id not in trackers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found: {tracker_id}")
    del trackers[tracker_id]
    return {'message': "Tracker deleted"}

# Add a document to a tracker
@app.post('/api/v1/trackers/{tracker_id}/documents', status_code=status.HTTP_201_CREATED, response_model=Response, tags=['trackers'], summary='Add a document to a tracker')
async def add_document_to_tracker(document: Document):
    if document.tracker_id not in trackers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found:")
    if document.path not in trackers[document.tracker_id]:
        trackers[document.tracker_id].documents[document.id] = document
        return {'message': "Document added"}
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Document already exists: {document.path}")

# Get a document from a tracker
@app.get('/api/v1/trackers/{tracker_id}/documents/{document_id}', status_code=status.HTTP_200_OK, response_model=Document, tags=['trackers'], summary='Get a document from a tracker')
async def get_document(tracker_id: str, document_id: str):
    tracker = trackers.get(tracker_id, None)
    if tracker is None:
        raise HTTPException(status_code=404, detail=f"Tracker not found: {tracker_id}")
    doc = tracker.documents.get(document_id, None)
    if doc is None:
        raise HTTPException(status_code=404, detail=f"Document not found: {id}")
    return doc

# Get all documents from a tracker
@app.get('/api/v1/trackers/{tracker_id}/documents', status_code=status.HTTP_200_OK, response_model=Dict[str, Document], tags=['trackers'], summary='Get all documents from a tracker')
async def get_documents(tracker_id: str):
    tracker = trackers.get(tracker_id, None)
    if tracker is None:
        raise HTTPException(status_code=404, detail=f"Tracker not found: {tracker_id}")
    return tracker.documents

# Delete a document from a tracker
@app.delete('/api/v1/trackers/{tracker_id}/documents/{document_id}', status_code=status.HTTP_200_OK, response_model=Response, tags=['trackers'], summary='Delete a document from a tracker')
async def delete_document(tracker_id: str, document_id: str):
    tracker = trackers.get(tracker_id, None)
    if tracker is None:
        raise HTTPException(status_code=404, detail=f"Tracker not found: {tracker_id}")
    doc = tracker.get(document_id, None)
    if doc is None:
        raise HTTPException(status_code=404, detail=f"Document not found: {document_id}")
    del tracker[document_id]
    return {'message': "Document deleted"}
