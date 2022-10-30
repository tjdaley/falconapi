"""
documents.py - Falcon API Routers for Documents
"""
from datetime import datetime
import json
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from auth.handler import get_current_active_user
from models.document import Document, ExtendedDocumentProperties
from models.response import ResponseAndId
from models.user import User
from database.documents_table import DocumentsDict
from database.extendedprops_table import ExtendedPropertiesDict
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
extendedprops = ExtendedPropertiesDict()
trackers = TrackersTable()

# Add a document
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=ResponseAndId, summary='Add a document')
async def add_document(doc: Document, user: User = Depends(get_current_active_user)):
    if doc.id in documents:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Document already exists: {doc.id}")
    if documents.get_by_path(doc.path):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Document already exists: {doc.path}")
    doc.added_username = user.username
    doc.added_date = datetime.now()
    doc.version = str(uuid4())
    documents[doc.id] = doc
    return {'message': "Document added", 'id': doc.id}

# Add extended document properties
@router.post('/props', status_code=status.HTTP_201_CREATED, response_model=ResponseAndId, summary="Add extended document properties")
async def add_document_props(props: ExtendedDocumentProperties, user: User = Depends(get_current_active_user)):
    if props.id not in documents:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document not found: {props.id}")
    
    verb = 'added'
    if props.id in extendedprops:
        existing_props = extendedprops[props.id]
        for key in props:
            existing_props[key] = props[key]
        props = existing_props
        verb = 'updated'
        # raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Extended properties already exist for document: {props.id}")
    extendedprops[props.id] = props
    return {'message': f"Document properties {verb}", 'id': props.id}

# Get a document by ID or path
@router.get('/', status_code=status.HTTP_200_OK, response_model=Document, summary='Get a document by ID or path')
async def get_document(doc_id: str = None, path: str = None, user: User = Depends(get_current_active_user)):
    if doc_id:
        doc = documents.get(doc_id)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document not found: {doc_id}")
        if doc.added_username != user.username and not user.admin:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
        return doc

    if path:
        doc = documents.get_by_path(path)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document not found: {path}")
        if doc.added_username != user.username and not user.admin:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
        return doc

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Must provide either doc_id or path")

# Get extended document properties
@router.get('/props', status_code=status.HTTP_200_OK, response_model=ExtendedDocumentProperties, summary='Get extended document properties')
async def get_document_props(doc_id: str, user: User = Depends(get_current_active_user)):
    if doc_id not in extendedprops:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Extended properties not found for document: {doc_id}")
    if documents[doc_id].added_username != user.username and not user.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return extendedprops[doc_id]

# Update a document
@router.put('/', status_code=status.HTTP_200_OK, response_model=ResponseAndId, summary='Update a document')
async def update_document(doc: Document, user: User = Depends(get_current_active_user)):
    if not doc.id in documents:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document not found: {doc.id}")
    if doc.version != documents[doc.id].version:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Document version conflict: {doc.id}")
    if documents[doc.id].added_username != user.username and not user.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    # Mark document as being updated
    updated_doc = documents.get(doc.id)
    updated_doc.updated_username = user.username
    updated_doc.updated_date = datetime.now()
    updated_doc.version = str(uuid4())

    # We don't let the caller update every field...just these:
    updated_doc.beginning_bates = doc.beginning_bates
    updated_doc.document_date = doc.document_date
    updated_doc.ending_bates = doc.ending_bates
    updated_doc.page_count = doc.page_count
    updated_doc.title = doc.title
    updated_doc.type = doc.type
    documents[doc.id] = updated_doc

    return {'message': "Document updated", 'id': doc.id}

# Update extended document properties
@router.put('/props', status_code=status.HTTP_200_OK, response_model=ResponseAndId, summary='Update extended document properties')
async def update_document_props(props: ExtendedDocumentProperties, user: User = Depends(get_current_active_user)):
    if props.id not in extendedprops:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Extended properties not found for document: {props.id}")
    if documents[props.id].added_username != user.username and not user.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    extendedprops[props.id] = props
    return {'message': "Document properties updated", 'id': props.id}

# Delete a document
# TODO: Do not delete a document if it is in other trackers - Switch.
# TODO: Delete references to the document from trackers
@router.delete('/', status_code=status.HTTP_200_OK, response_model=ResponseAndId, summary='Delete a document')
async def delete_document(doc_id: str, cascade: bool = 'true', user: User = Depends(get_current_active_user)):
    should_cascade = cascade == 'true'
    if not doc_id in documents:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document not found: {doc_id}")
    doc = documents.get(doc_id)
    if doc.added_username != user.username and not user.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    trackers_linked_to_doc = trackers.get_trackers_linked_to_doc(doc_id)

    # This document is not in other trackers, so we can delete it.
    if not trackers_linked_to_doc:
        del documents[doc_id]
        del extendedprops[doc_id]
        return {'message': "Document deleted", 'id': doc_id}
    
    # This document is in other trackers but the cascade flag is set to false - we cannot delete it.
    if not should_cascade:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Document is in trackers: {trackers_linked_to_doc}")
    
    # This document is in other trackers and the cascade flag is set to true - we can delete it.
    del documents[doc_id]
    trackers.delete_document_from_trackers(doc_id)
    del extendedprops[doc_id]
    return {'message': "Document deleted", 'id': doc_id}

# Delete extended document properties
@router.delete('/props', status_code=status.HTTP_200_OK, response_model=ResponseAndId, summary='Delete extended document properties')
async def delete_document_props(doc_id: str, user: User = Depends(get_current_active_user)):
    if doc_id not in extendedprops:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Extended properties not found for document: {doc_id}")
    if documents[doc_id].added_username != user.username and not user.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    del extendedprops[doc_id]
    return {'message': "Document properties deleted", 'id': doc_id}
