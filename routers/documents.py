"""
documents.py - Falcon API Routers for Documents
"""
from datetime import datetime
import logging
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from auth.handler import get_current_active_user
from models.document import Document, PutExtendedDocumentProperties, ExtendedDocumentProperties, DocumentCsvTables, DocumentObjTables, DocumentClassificationStatus
from models.response import ResponseAndId, ResponseAndVersion
from models.user import User
from database.documents_table import DocumentsDict
from database.extendedprops_table import ExtendedPropertiesDict
from database.classification_tasks import ClassificationTasksTable, ClassificationStatus
from database.trackers_table import TrackersTable
from routers.api_version import APIVersion


API_VERSION = APIVersion(1, 0).to_str()
ROUTE_PREFIX = '/documents'
LOGGER = logging.getLogger(f'falconapi{ROUTE_PREFIX}')
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
    return {'message': "Document added", 'id': doc.id, 'version': doc.version}


# Add extended document properties
@router.post('/props', status_code=status.HTTP_201_CREATED, response_model=ResponseAndId, summary="Add extended document properties")
# pylint: disable=unused-argument
async def add_document_props(
    props: PutExtendedDocumentProperties, user: User = Depends(get_current_active_user)
):
    document_id = props.id  # Link to document for these props

    if document_id not in documents:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document not found: {props.id}")

    # If the document already has extended properties, we need to update them.
    verb = 'added'
    if document_id in extendedprops:
        existing_props = extendedprops[document_id] or {}
        for key, _ in props:
            existing_props[key] = props.__dict__.get(key)
        props = PutExtendedDocumentProperties(**existing_props)
        verb = 'updated'

    # Add the extended properties
    extendedprops[document_id] = props
    return {'message': f"Document properties {verb}", 'id': document_id, 'version': documents[document_id].version}


# Get a document by ID or path
@router.get('/', status_code=status.HTTP_200_OK, response_model=Document, summary='Get a document by ID or path')
async def get_document(doc_id: str = '', path: str = '', user: User = Depends(get_current_active_user)):
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

# Get a document's Tables - CSV or JSON Formats
@router.get('/tables/csv', status_code=status.HTTP_200_OK, response_model=DocumentCsvTables, summary='Get a document\'s Tables in CSV format')
async def get_document_tables_csv(doc_id: str, user: User = Depends(get_current_active_user)):
    if doc_id not in extendedprops:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Extended properties not found for document: {doc_id}")
    if documents[doc_id].added_username != user.username and not user.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    if 'tables' not in (extendedprops[doc_id] or {}):
        return {"id": doc_id, "csv_tables": {}, "version": (extendedprops[doc_id] or {}).get('version')}
    csv_tables = make_csv_tables((extendedprops[doc_id] or {}).get('tables', {}))
    return {"id": doc_id, "csv_tables": csv_tables, "version": (extendedprops[doc_id] or {}).get('version')}

def make_csv_tables(tables: dict):
    """
    Convert tables to CSV format

    Args:
        tables (dict): Tables in JSON format

    Returns:
        dict: Tables in CSV format
    """
    if not tables:
        return {}
    csv_tables = {}
    for table_id, table in tables.items():
        table_rows = list(table[0].keys())
        data_rows = [list(row.values()) for row in table]
        csv_tables[table_id] = {'headers': table_rows, 'data': data_rows}
    return csv_tables

@router.get('/tables/json', status_code=status.HTTP_200_OK, response_model=DocumentObjTables, summary='Get a document\'s Tables in JSON format')
async def get_document_tables_json(doc_id: str, user: User = Depends(get_current_active_user)):
    if doc_id not in extendedprops:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Extended properties not found for document: {doc_id}")
    if documents[doc_id].added_username != user.username and not user.admin:
        LOGGER.error("Username mismatch:", documents[doc_id].added_username, "vs.", user.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    xprops = extendedprops.get(doc_id) or {}
    return {'id': doc_id, 'tables': xprops.get('tables', {}) or {}, 'version': xprops.get('version', '*unversioned*')}

# Get the document's version
@router.get('/version', status_code=status.HTTP_200_OK, response_model=ResponseAndVersion, summary='Get a document\'s version. Can also be used to check if a document exists.')
async def get_document_version(doc_id: str, user: User = Depends(get_current_active_user)):
    LOGGER.info(f"VERSION: Checking version for document: %s", doc_id)
    if doc_id not in documents:
        LOGGER.error(f"VERSION: Document not found: %s", doc_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document not found: {doc_id}")
    if documents[doc_id].added_username != user.username and not user.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Unauthorized - username mismatch. Added by {documents[doc_id].added_username} but requested by {user.username}")
    doc = documents.get(doc_id)
    if doc:
        return {'message': "Document version", 'id': doc_id, 'version': doc.version}
    return {'message': "Document not found", 'id': doc_id, 'version': None}

# Delete a table from a document given the table_id and the document_id
@router.delete('/tables', status_code=status.HTTP_200_OK, response_model=ResponseAndId, summary='Delete a table from a document')
async def delete_document_table(doc_id: str, table_id: str, user: User = Depends(get_current_active_user)):
    if doc_id not in extendedprops:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Extended properties not found for document: {doc_id}")
    if documents[doc_id].added_username != user.username and not user.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    # Delete the json-formatted table
    xprops = extendedprops.get(doc_id) or {}
    if 'dict_tables' not in xprops:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document does not have tables: {doc_id}")
    
    xprops = xprops.copy()
    tables = xprops['dict_tables'].get('tables', [])
    new_tables = [table for table in tables if table['table_id'] != table_id]
    xprops['dict_tables']['tables'] = new_tables

    # Delete the csv-formatted table
    if 'csv_tables' not in xprops:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document does not have tables: {doc_id}")
    if table_id not in xprops['csv_tables']:
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Unauthorized - username mismatch. Added by {documents[doc.id].added_username} but requested by {user.username}")

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
    updated_doc.page_max = doc.page_max
    updated_doc.missing_pages = doc.missing_pages
    if doc.classification:
        updated_doc.classification = doc.classification
    if doc.sub_classification:
        updated_doc.sub_classification = doc.sub_classification
    documents[doc.id] = updated_doc

    return {'message': "Document updated", 'id': doc.id, 'version': updated_doc.version}


# Update extended document properties
@router.put('/props', status_code=status.HTTP_200_OK, response_model=ResponseAndId, summary='Update extended document properties')
async def update_document_props(
    props: PutExtendedDocumentProperties, user: User = Depends(get_current_active_user)
):
    if props.id not in extendedprops:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Extended properties not found for document: {props.id}")
    if documents[props.id].added_username != user.username and not user.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Unauthorized - username mismatch. Added by {documents[props.id].added_username} but requested by {user.username}")

    # Save the extended properties
    extendedprops[props.id] = props
    LOGGER.info(f"Updated extended properties for document: %s job_status: %s job_id: %s", props.id, props.job_status, props.job_id)
    return {"message": f"Document properties updated (put)", "id": props.id, "version": documents[props.id].version}


def update_tables(existing_tables: dict, new_tables: dict):
    """
    Update a table in the extended properties

    Args:
        existing_tables (dict): Existing tables
        new_tables (dict): New tables

    Returns:
        dict: Updated tables
    """
    if not new_tables:
        return existing_tables
    if not existing_tables:
        return new_tables

    for table_id, table in new_tables.items():
        if isinstance(table, list):
            existing_tables[table_id] = table
    return existing_tables

# Delete a document
# TODO: Do not delete a document if it is in other trackers - Switch.
# TODO: Delete references to the document from trackers
@router.delete('/', status_code=status.HTTP_200_OK, response_model=ResponseAndId, summary='Delete a document')
async def delete_document(doc_id: str, cascade: bool = True, user: User = Depends(get_current_active_user)):
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
    return {'message': "Document deleted", 'id': doc_id, 'version': doc.version}

# Delete extended document properties
@router.delete('/props', status_code=status.HTTP_200_OK, response_model=ResponseAndId, summary='Delete extended document properties')
async def delete_document_props(doc_id: str, user: User = Depends(get_current_active_user)):
    if doc_id not in extendedprops:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Extended properties not found for document: {doc_id}")
    if documents[doc_id].added_username != user.username and not user.admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    del extendedprops[doc_id]
    return {'message': "Document properties deleted", 'id': doc_id, 'version': documents[doc_id].version}
