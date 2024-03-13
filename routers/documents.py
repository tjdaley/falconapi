"""
documents.py - Falcon API Routers for Documents
"""
from datetime import datetime
import logging
from uuid import uuid4
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from auth.handler import get_current_active_user
from models.document import Document, ExtendedDocumentProperties, DocumentCsvTables, DocumentObjTables, DocumentClassificationStatus
from models.response import ResponseAndId
from models.user import User
from database.documents_table import DocumentsDict
from database.extendedprops_table import ExtendedPropertiesDict
from database.classification_tasks import ClassificationTasksTable, ClassificationStatus
from database.trackers_table import TrackersTable
from routers.api_version import APIVersion
from doc_classifier.openai_classifier import Classifier as OpenAIClassifier
from doc_classifier.palm_classifier import Classifier as PalmClassifier


API_VERSION = APIVersion(1, 0).to_str()
ROUTE_PREFIX = '/documents'
LOGGER = logging.getLogger(f'falconapi{ROUTE_PREFIX}')
OPENAICLASSIFIER = OpenAIClassifier()
PALMCLASSIFIER = PalmClassifier()
CLASSIFICATION_TASKS = ClassificationTasksTable()
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
# pylint: disable=unused-argument
async def add_document_props(props: ExtendedDocumentProperties, user: User = Depends(get_current_active_user)):
    document_id = props.id  # Link to document for these props

    if document_id not in documents:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document not found: {props.id}")

    # If the document already has extended properties, we need to update them.
    verb = 'added'
    if document_id in extendedprops:
        existing_props = extendedprops[document_id]
        for key, _ in props:
            existing_props[key] = props.__dict__.get(key)
        props = ExtendedDocumentProperties(**existing_props)
        verb = 'updated'

    # Add the extended properties
    extendedprops[document_id] = props
    return {'message': f"Document properties {verb}", 'id': document_id}

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

# Get document classification - Synchrnous
@router.get('/classifysync', status_code=status.HTTP_200_OK, response_model=DocumentClassificationStatus, summary='Get document classification synchronously')
async def get_document_classify_sync(doc_id: str, background_tasks: BackgroundTasks, user: User = Depends(get_current_active_user)):
    if doc_id not in extendedprops:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Extended properties not found for document: {doc_id}")
    if documents[doc_id].added_username != user.username and not user.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    classification = _classify(doc_id, None)
    return {
        'task_id': None,
        'document_id': doc_id,
        'status': ClassificationStatus.COMPLETED.value,
        'message': 'Classification complete',
        'classification': classification
    }

# Get document classification - Async
@router.get('/classify', status_code=status.HTTP_200_OK, response_model=DocumentClassificationStatus, summary='Queue document classification and return', description='Queue document classification and return a task_id that can be used to check the status of the classification')
async def get_document_classify(doc_id: str, background_tasks: BackgroundTasks, user: User = Depends(get_current_active_user)):
    """
    Queue a document for classification. Returns a task_id that can be used to check the status of the classification.

    Args:
        doc_id (str): Document ID
        background_tasks (BackgroundTasks): Background tasks
        user (User, optional): User. Defaults to Depends(get_current_active_user).

    Raises:
        HTTPException: Document not found
        HTTPException: Unauthorized

    Returns:
        dict: Classification status
    """
    if doc_id not in extendedprops:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Extended properties not found for document: {doc_id}")
    if documents[doc_id].added_username != user.username and not user.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    classification_task_id = CLASSIFICATION_TASKS.add(doc_id)
    background_tasks.add_task(_classify, doc_id, classification_task_id)
    return {
        'task_id': classification_task_id,
        'document_id': doc_id,
        'status': ClassificationStatus.QUEUED.value,
        'message': 'Classification queued',
    }

@router.get('/classification', status_code=status.HTTP_200_OK, response_model=DocumentClassificationStatus, summary='Get document classification or classification status')
async def get_document_classification(task_id: str, user: User = Depends(get_current_active_user)):
    classification_task = CLASSIFICATION_TASKS.get(task_id)
    if not classification_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Classification task not found: {task_id}")
    if documents[classification_task['document_id']].added_username != user.username and not user.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    if classification_task['status'] == ClassificationStatus.COMPLETED:
        return classification_task['classification']
    return {
        'task_id': task_id,
        'document_id': classification_task['document_id'],
        'status': classification_task['status'],
        'message': classification_task.get('message'),
        'classification': classification_task.get('classification')
    }


# Get a document's Tables - CSV or JSON Formats
@router.get('/tables/csv', status_code=status.HTTP_200_OK, response_model=DocumentCsvTables, summary='Get a document\'s Tables in CSV format')
async def get_document_tables_csv(doc_id: str, user: User = Depends(get_current_active_user)):
    if doc_id not in extendedprops:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Extended properties not found for document: {doc_id}")
    if documents[doc_id].added_username != user.username and not user.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return extendedprops[doc_id]

@router.get('/tables/json', status_code=status.HTTP_200_OK, response_model=DocumentObjTables, summary='Get a document\'s Tables in JSON format')
async def get_document_tables_json(doc_id: str, user: User = Depends(get_current_active_user)):
    if doc_id not in extendedprops:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Extended properties not found for document: {doc_id}")
    if documents[doc_id].added_username != user.username and not user.admin:
        LOGGER.error("Username mismatch:", documents[doc_id].added_username, "vs.", user.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    # Some documents don't have tables
    if 'dict_tables' not in extendedprops[doc_id]:
        tables = {"tables": {}}
        props = extendedprops[doc_id].copy()
        props['dict_tables'] = tables
        return props
    # Some older documents were saved with a list of tables, not a dict of tables
    if not isinstance(extendedprops[doc_id]['dict_tables'], dict):
        tables = {"tables": {e['table_id']: e for e in extendedprops[doc_id]['dict_tables']}}
        props = extendedprops[doc_id].copy()
        props['dict_tables'] = tables
        return props
    return extendedprops[doc_id]

# Delete a table from a document given the table_id and the document_id
@router.delete('/tables', status_code=status.HTTP_200_OK, response_model=ResponseAndId, summary='Delete a table from a document')
async def delete_document_table(doc_id: str, table_id: str, user: User = Depends(get_current_active_user)):
    if doc_id not in extendedprops:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Extended properties not found for document: {doc_id}")
    if documents[doc_id].added_username != user.username and not user.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    # Delete the json-formatted table
    if 'dict_tables' not in extendedprops[doc_id]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document does not have tables: {doc_id}")
    
    xprops = extendedprops[doc_id].copy()
    tables = xprops['dict_tables'].get('tables', [])
    new_tables = [table for table in tables if table['table_id'] != table_id]
    xprops['dict_tables']['tables'] = new_tables

    # Delete the csv-formatted table
    if 'csv_tables' not in extendedprops[doc_id]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document does not have tables: {doc_id}")
    if table_id not in extendedprops[doc_id]['csv_tables']:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Dict Table not found: {table_id}")
    del xprops.get('csv_tables', {})[table_id]
    # synchornizes the datastore with the extendedprops dict
    extendedprops[doc_id] = ExtendedDocumentProperties(**xprops)

    return {'message': "Table deleted", 'id': table_id}

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
    if doc.classification:
        updated_doc.classification = doc.classification
    if doc.sub_classification:
        updated_doc.sub_classification = doc.sub_classification
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


# Convert classification properties to dict, for JSON response.
def _props_to_data(oclass: str, oprops: dict, pclass: str, pprops: dict, doc_id: str, task_id: str):
    data = {
        'document_id': doc_id,
        'task_id': task_id,
        'classifications': [
            {
                'classifier': 'openai',
                'classification': oclass,
                'properties': oprops
            },
            {
                'classifier': 'palm',
                'classification': pclass,
                'properties': pprops
            }
        ],
    }
    return data


# Classify a document
def _classify(doc_id: str, task_id: str) -> dict:
    """
    Classify a document.

    Args:
        doc_id (str): Document ID
        task_id (str): Classification task ID (if None, then there is no task_id because this is a synchronous call)
    
    Raises:
        HTTPException: Extended properties not found

    Returns:
        dict: Document classification    
    """
    xprops = extendedprops.get(doc_id)
    if not xprops:
        if task_id:
            CLASSIFICATION_TASKS.update(task_id, ClassificationStatus.FAILED, f"Extended properties not found: {doc_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Extended properties not found: {doc_id}")

    if task_id:
        CLASSIFICATION_TASKS.update(task_id, ClassificationStatus.PROCESSING, "Classifying document")
    oclass = OPENAICLASSIFIER.classify(xprops['text'])
    pclass = PALMCLASSIFIER.classify(xprops['text'])
    oprops = OPENAICLASSIFIER.subclassify(xprops['text'], oclass)
    pprops = PALMCLASSIFIER.subclassify(xprops['text'], pclass)
    classification = _props_to_data(oclass, oprops, pclass, pprops, doc_id, task_id)
    if task_id:
        CLASSIFICATION_TASKS.update(task_id, ClassificationStatus.COMPLETED, "Classification complete",  classification)
    return classification
