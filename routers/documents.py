"""
documents.py - Falcon API Routers for Documents
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from auth.handler import get_current_active_user
from models.document import Document
from models.response import ResponseAndId
from models.user import User
from database.documents_table import DocumentsDict
from database.trackers_table import TrackersTable
from routers.api_version import APIVersion


API_VERSION = APIVersion(1, 0).to_str()
ROUTE_PREFIX = '/documents'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f'api/{API_VERSION}{ROUTE_PREFIX}/token')

router = APIRouter(
    tags=["Documents"],
    prefix=ROUTE_PREFIX,
    responses={404: {"description": "Not found"}}
)

documents = DocumentsDict()
trackers = TrackersTable()

# Add a document
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=ResponseAndId, summary='Add a document')
async def add_document(doc: Document, user: User = Depends(get_current_active_user)):
    if doc.id in documents:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Document already exists: {doc.id}")
    if documents.get_by_path(doc.path):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Document already exists: {doc.path}")
    doc.added_username = user.username
    documents[doc.id] = doc
    return {'message': "Document added", 'id': doc.id}

# Get a document by ID
@router.get('/', status_code=status.HTTP_200_OK, response_model=Document, summary='Get a document by ID')
async def get_document(doc_id: str, user: User = Depends(get_current_active_user)):
    doc = documents.get(doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document not found: {doc_id}")
    if doc.added_username != user.username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return doc

# Update a document
@router.put('/', status_code=status.HTTP_200_OK, response_model=ResponseAndId, summary='Update a document')
async def update_document(doc: Document, user: User = Depends(get_current_active_user)):
    if not doc.id in documents:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document not found: {doc.id}")
    doc.added_username = user.username
    documents[doc.id] = doc
    return {'message': "Document updated", 'id': doc.id}

# Delete a document
# TODO: Do not delete a document if it is in other trackers - Switch.
# TODO: Delete references to the document from trackers
@router.delete('/', status_code=status.HTTP_200_OK, response_model=ResponseAndId, summary='Delete a document')
async def delete_document(doc_id: str, cascade: bool = 'true', user: User = Depends(get_current_active_user)):
    should_cascade = cascade == 'true'
    if not doc_id in documents:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document not found: {doc_id}")
    doc = documents.get(doc_id)
    if doc.added_username != user.username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    trackers_linked_to_doc = trackers.get_trackers_linked_to_doc(doc_id)

    # This document is not in other trackers, so we can delete it.
    if not trackers_linked_to_doc:
        del documents[doc_id]
        return {'message': "Document deleted", 'id': doc_id}
    
    # This document is in other trackers but the cascade flag is set to false - we cannot delete it.
    if not should_cascade:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Document is in trackers: {trackers_linked_to_doc}")
    
    # This document is in other trackers and the cascade flag is set to true - we can delete it.
    del documents[doc_id]
    trackers.delete_document_from_trackers(doc_id)
    return {'message': "Document deleted", 'id': doc_id}
