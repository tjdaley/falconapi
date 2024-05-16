"""
discovery_trackers.py - Falcon API Routers for Discovery Trackers
"""
from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List
import os
from auth.handler import get_current_active_user
from models.audit import Audit
from models.document import Document, CategorySubcategoryResponse
from models.response import Response, ResponseAndId
from models.tracker import Tracker, TrackerUpdate, TrackerDatasetResponse
from models.user import User
from database.audit_table import AuditTable
from database.trackers_table import TrackersDict, TrackersTable
from database.documents_table import DocumentsDict
from routers.api_version import APIVersion
from util.log_util import get_logger
import settings  # NOQA


API_VERSION = APIVersion(1, 0).to_str()
ROUTE_PREFIX = '/trackers'
LOGGER = get_logger(f'falconapi{ROUTE_PREFIX}')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f'api/{API_VERSION}{ROUTE_PREFIX}/token')

router = APIRouter(
    tags=["Discovery Trackers"],
    prefix=ROUTE_PREFIX,
    responses={404: {"description": "Not found"}}
)

audittable = AuditTable()
trackers = TrackersDict()
tracker_db = TrackersTable()
documents = DocumentsDict()

AUDIT_LOGGING_ENABLED = os.getenv('AUDIT_LOGGING_ENABLED', 'False').lower() == 'true'
LOGGER.info("AUDIT_LOGGING_ENABLED: %s", AUDIT_LOGGING_ENABLED)

# Log an audit event
def log_audit_event(event: str, doc_id: str, user: User, old_data: BaseModel = None, new_data: BaseModel = None, success: bool = True, message: str = None) -> None:
    if AUDIT_LOGGING_ENABLED:
        if old_data and isinstance(old_data, BaseModel):
            str_old_data = old_data.json(exclude_none=True, exclude_unset=True)
        else:
            str_old_data = old_data
        if new_data and isinstance(new_data, BaseModel):
            str_new_data = new_data.json(exclude_none=True, exclude_unset=True)
        else:
            str_new_data = new_data
        audit = Audit(
            description=event,
            table=str(trackers),
            record_id=doc_id,
            username=user.username,
            admin_user=user.admin,
            event_date=datetime.now(),
            success = success,
            message = message,
            old_data=str_old_data if old_data else None,
            new_data=str_new_data if new_data else None
        )
        audittable.create_event(audit)
    else:
        LOGGER.debug("AUDIT_LOGGING_ENABLED is False, so not logging audit event: %s - %s", event, message if message else "(no message provided)")

# Add a tracker
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=ResponseAndId, summary='Create a tracker')
async def create_tracker(tracker: Tracker, user: User = Depends(get_current_active_user)):
    if tracker.id in trackers:
        log_audit_event('create_tracker', tracker.id, user, success=False, message=f"Tracker {tracker.id} already exists")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Tracker already exists: {tracker.id}")
    tracker.added_username = user.username
    tracker.added_date = datetime.now()
    tracker.auth_usernames = [user.username]
    tracker.version = str(uuid4())
    trackers[tracker.id] = tracker
    log_audit_event('create_tracker', tracker.id, user, new_data=tracker)
    return {'message': "Tracker created", 'id': tracker.id}

# Get a tracker by Tracker ID
@router.get('/', status_code=status.HTTP_200_OK, response_model=Tracker, summary='Get a tracker by Tracker ID')
async def get_tracker(tracker_id: str, user: User = Depends(get_current_active_user)):
    tracker = trackers.get(tracker_id)
    if not tracker:
        log_audit_event('get_tracker', tracker_id, user, success=False, message=f"Tracker {tracker_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found: {tracker_id}")
    if user.username not in tracker.auth_usernames and not user.admin:
        log_audit_event('get_tracker', tracker_id, user, success=False, message=f"User {user.username} not authorized to get tracker {tracker_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    log_audit_event('get_tracker', tracker_id, user)
    return tracker

# Get all trackers for a user
@router.get('/user', status_code=status.HTTP_200_OK, response_model=List[Tracker], summary='Get all trackers for a user')
async def get_trackers_for_user(username: str = None, user: User = Depends(get_current_active_user)):
    message = f"get_trackers_for_user: username={username} by user={user.username}. Requesting user is admin={user.admin}"
    LOGGER.info(message)
    log_audit_event(f'get_trackers_for_user::{username}', '', user, success=False, message=message)
    if username is None:
        username = user.username
    if user.admin or user.username == username:
        log_audit_event(f'get_trackers_for_user::{username}', '', user)
        return trackers.get_for_username(username)

    log_audit_event(f'get_trackers_for_user::{username}', '', user, success=False, message=message)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Unauthorized - user {user.username} not authorized to get trackers for user {username}")

# Update a tracker
@router.put('/', status_code=status.HTTP_200_OK, response_model=ResponseAndId, summary='Update a tracker')
async def update_tracker(tracker: TrackerUpdate, user: User = Depends(get_current_active_user)):
    existing_tracker = trackers.get(tracker.id)
    if not existing_tracker:
        log_audit_event('update_tracker', tracker.id, user, success=False, message=f"Tracker {tracker.id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found: {existing_tracker.id}")
    if user.username not in existing_tracker.auth_usernames and not user.admin:
        log_audit_event('update_tracker', tracker.id, user, success=False, message=f"User {user.username} not authorized to update tracker {tracker.id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    if existing_tracker.version != tracker.version:
        log_audit_event('update_tracker', tracker.id, user, success=False, message=f"Tracker {tracker.id} version mismatch")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Tracker version conflict: {existing_tracker.id}")
    tracker.updated_username = user.username
    tracker.updated_date = datetime.now()
    tracker.version = str(uuid4())
    trackers[tracker.id] = tracker
    log_audit_event('update_tracker', tracker.id, user, old_data=existing_tracker, new_data=tracker)
    return {'message': "Tracker updated", 'id': tracker.id}

# Add user to the list of authorized users for a tracker
@router.put('/auth', status_code=status.HTTP_200_OK, response_model=ResponseAndId, summary='Add user to the list of authorized users for a tracker')
async def add_user_to_tracker_auth(tracker_id: str, username: str, user: User = Depends(get_current_active_user)):
    existing_tracker = trackers.get(tracker_id)
    if not existing_tracker:
        log_audit_event('add_user_to_tracker_auth', tracker_id, user, success=False, message=f"Tracker {tracker_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found: {existing_tracker.id}")
    if user.username not in existing_tracker.auth_usernames and not user.admin:
        log_audit_event('add_user_to_tracker_auth', tracker_id, user, success=False, message=f"User {user.username} not authorized to add user {username} to tracker {tracker_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    if username in existing_tracker.auth_usernames:
        log_audit_event('add_user_to_tracker_auth', tracker_id, user, success=False, message=f"User {username} already authorized for tracker {tracker_id}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User already authorized: {username}")
    old_data = existing_tracker.json(exclude_none=True, exclude_unset=True)
    existing_tracker.auth_usernames.append(username)
    trackers[tracker_id] = existing_tracker
    log_audit_event('add_user_to_tracker_auth', tracker_id, user, new_data=existing_tracker, old_data=old_data)
    return {'message': "User added to list of authorized users", 'id': tracker_id}

# Delete a tracker
@router.delete('/', status_code=status.HTTP_200_OK, response_model=ResponseAndId, summary='Delete a tracker')
async def delete_tracker(tracker_id: str, user: User = Depends(get_current_active_user)):
    tracker = trackers.get(tracker_id)
    if not tracker:
        log_audit_event('delete_tracker', tracker_id, user, success=False, message=f"Tracker {tracker_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found: {tracker_id}")
    if user.username not in tracker.auth_usernames and not user.admin:
        log_audit_event('delete_tracker', tracker_id, user, success=False, message=f"User {user.username} not authorized to delete tracker {tracker_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    # If this is the user who created the tracker or an admin user, then delete the tracker.
    if user.username == tracker.added_username or user.admin:
        del trackers[tracker_id]
        log_audit_event('delete_tracker', tracker_id, user, old_data=tracker)
        return {'message': "Tracker deleted", 'id': tracker_id}
    
    # Otherwise, just remove the user from the auth_usernames list.
    old_data = tracker.copy()
    tracker.auth_usernames.remove(user.username)
    trackers[tracker.id] = tracker
    log_audit_event(f'delete_tracker::for user {user.username}', tracker_id, user, new_data=tracker, old_data=old_data)
    return {'message': "Tracker updated", 'id': tracker_id}

# Link a document.id to the tracker document list
@router.patch('/{tracker_id}/documents/link/{document_id}', status_code=status.HTTP_202_ACCEPTED, response_model=ResponseAndId, summary='Link a document to a tracker')
async def link_document(tracker_id: str, document_id: str, user: User = Depends(get_current_active_user)):
    tracker = trackers.get(tracker_id)
    if not tracker:
        log_audit_event('link_document', tracker_id, user, success=False, message=f"Tracker {tracker_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found: {tracker_id}")
    if user.username not in tracker.auth_usernames and not user.admin:
        log_audit_event('link_document', tracker_id, user, success=False, message=f"User {user.username} not authorized to link document {document_id} to tracker {tracker_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    document = documents.get(document_id)
    if not document:
        log_audit_event('link_document', tracker_id, user, success=False, message=f"Document {document_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document not found: {document_id}")
    if document.id in tracker.documents:
        log_audit_event('link_document', tracker_id, user, success=False, message=f"Document {document_id} already linked to tracker {tracker_id}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Document already linked: {document_id}")

    r = trackers.link_doc(tracker, document)
    log_audit_event('link_document', tracker_id, user, new_data="{'document_id': document_id}")
    return {'message': "Document linked to tracker", 'id': document_id}

# Unlink a document from a tracker
@router.patch('/{tracker_id}/documents/unlink/{document_id}', status_code=status.HTTP_200_OK, response_model=ResponseAndId, summary='Delete a document from a tracker')
async def unlink_document(tracker_id: str, document_id: str, user: User = Depends(get_current_active_user)):
    tracker = trackers.get(tracker_id)
    if tracker is None:
        log_audit_event('unlink_document', tracker_id, user, success=False, message=f"Tracker {tracker_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found: {tracker_id}")
    if user.username not in tracker.auth_usernames and not user.admin:
        log_audit_event('unlink_document', tracker_id, user, success=False, message=f"User {user.username} not authorized to unlink document {document_id} from tracker {tracker_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    trackers.unlink_doc(tracker, document_id)
    log_audit_event('unlink_document', tracker_id, user, old_data="{'document_id': document_id}")
    return {'message': "Document unlinked from tracker", 'id': document_id}

# Get all documents from a tracker
@router.get('/{tracker_id}/documents', status_code=status.HTTP_200_OK, response_model=List[Document], summary='Get all documents from a tracker')
async def get_documents(tracker_id: str, user: User = Depends(get_current_active_user)):
    tracker = trackers.get(tracker_id)
    if tracker is None:
        log_audit_event('get_documents', tracker_id, user, success=False, message=f"Tracker {tracker_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found: {tracker_id}")
    if user.username not in tracker.auth_usernames and not user.admin:
        log_audit_event('get_documents', tracker_id, user, success=False, message=f"User {user.username} not authorized to get documents from tracker {tracker_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    log_audit_event('get_documents', tracker_id, user)
    return documents.get_for_tracker(tracker)

# Get list of unique categories from a tracker
@router.get('/{tracker_id}/categories', status_code=status.HTTP_200_OK, response_model=List[str], summary='Get all categories of documents from a tracker')
async def get_categories(tracker_id: str, user: User = Depends(get_current_active_user)):
    tracker = trackers.get(tracker_id)
    if tracker is None:
        log_audit_event('get_categories', tracker_id, user, success=False, message=f"Tracker {tracker_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found: {tracker_id}")
    if user.username not in tracker.auth_usernames and not user.admin:
        log_audit_event('get_categories', tracker_id, user, success=False, message=f"User {user.username} not authorized to get categories from tracker {tracker_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    log_audit_event('get_categories', tracker_id, user)
    return documents.get_categories_for_tracker(tracker)

# Get a list of unique category+subcategory pairs from a tracker
@router.get('/{tracker_id}/category_subcategory_pairs', status_code=status.HTTP_200_OK, response_model=List[CategorySubcategoryResponse], summary='Get all category+subcategory pairs from a tracker')
async def get_category_subcategory_pairs(tracker_id: str, user: User = Depends(get_current_active_user)):
    tracker = trackers.get(tracker_id)
    if tracker is None:
        log_audit_event('get_category_subcategory_pairs', tracker_id, user, success=False, message=f"Tracker {tracker_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found: {tracker_id}")
    if user.username not in tracker.auth_usernames and not user.admin:
        log_audit_event('get_category_subcategory_pairs', tracker_id, user, success=False, message=f"User {user.username} not authorized to get category+subcategory pairs from tracker {tracker_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    log_audit_event('get_category_subcategory_pairs', tracker_id, user)
    return documents.get_category_subcategory_pairs_for_tracker(tracker)

# Get datasets for a tracker
@router.get('/{tracker_id}/datasets/{dataset_name}', status_code=status.HTTP_200_OK, response_model=TrackerDatasetResponse, summary='Get datasets for a tracker')
async def get_datasets(tracker_id: str, dataset_name: str, user: User = Depends(get_current_active_user)):
    tracker = trackers.get(tracker_id)
    if tracker is None:
        log_audit_event('get_datasets', tracker_id, user, success=False, message=f"Tracker {tracker_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found: {tracker_id}")
    if user.username not in tracker.auth_usernames and not user.admin:
        log_audit_event('get_datasets', tracker_id, user, success=False, message=f"User {user.username} not authorized to get datasets from tracker {tracker_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    log_audit_event('get_datasets', tracker_id, user, dataset_name)
    result = tracker_db.get_dataset(tracker, dataset_name)
    return result

# Get compliance matrix for a tracker
@router.get('/{tracker_id}/compliance_matrix/{classification}', status_code=status.HTTP_200_OK, summary='Get compliance matrix for a tracker')
async def get_compliance_matrix(tracker_id: str, classification: str, user: User = Depends(get_current_active_user)):
    tracker = trackers.get(tracker_id)
    if tracker is None:
        log_audit_event('get_compliance_matrix', tracker_id, user, success=False, message=f"Tracker {tracker_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tracker not found: {tracker_id}")
    if user.username not in tracker.auth_usernames and not user.admin:
        log_audit_event('get_compliance_matrix', tracker_id, user, success=False, message=f"User {user.username} not authorized to get compliance matrix from tracker {tracker_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    log_audit_event('get_compliance_matrix', tracker_id, user, classification)
    return tracker_db.get_compliance_matrix(tracker, classification)
