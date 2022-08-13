"""
test_root.py - Test the root endpoint
"""
import requests
import pytest
import json

API_VERSION = '1_0'
SERVER = 'http://localhost:8000'
PREFIX = f'/api/v{API_VERSION}'

test_user = {
    'email': 'test_user@test.com',
    'username': 'test_user@test.com',
    'password': 'test_password',
    'full_name': 'Test User'
}

LOGIN_DATA  = {'username': test_user['username'], 'password': test_user['password']}
TRACKER_ID_123 = {'id': '123', 'username': test_user['username'], 'name': 'Test Tracker', 'documents': [], 'client_reference':'20202.1'}
TRACKER_ID_124 = {'id': '124', 'username': test_user['username'], 'name': 'Test Tracker', 'documents': [], 'client_reference':'20202.1'}
TRACKER_NO_ID = {'username': test_user['username'], 'name': 'Test Tracker', 'documents': []}
DOC_1 = {
    "id": "doc-1",
    "path":"x:\\shared\\plano\\tjd\\open\\farrar\\discovery\\our production\\2022-07-15 BOA 2304.pdf",
    "filename":"2022-07-15 BOA 2304.pdf",
    "type": "application/pdf",
    "title": "BOA 2304 2022.07.15",
    "create_date":"07/01/2022",
    "document_date": "07/15/2022",
    "beginning_bates": "TD002304",
    "ending_bates": "TD002304",
    "page_count": 1,
    "bates_pattern": "TD\d{6}",
    "added_username": LOGIN_DATA['username']
}
DOC_2 = {
    "id": "doc-2",
    "path": "x:\\shared\\plano\\tjd\\open\\farrar\\discovery\\our production\\2022-08-15 BOA 2304.pdf",
    "filename": "2022-07-15 BOA 2304.pdf",
    "type": "application/pdf",
    "title": "BOA 2304 2022.08.15",
    "create_date": "07/01/2022",
    "document_date": "08/15/2022",
    "beginning_bates": "TD002305",
    "ending_bates": "TD002309",
    "page_count": 5,
    "bates_pattern": "TD\d{6}",
    "added_username": LOGIN_DATA['username']
}

AUTH_HEADER = None
DEL_DOC_ID = None

@pytest.mark.slow
def test_authenticate_user():
    global AUTH_HEADER
    response = requests.post(SERVER + PREFIX + '/users/token', data=LOGIN_DATA)
    assert response.status_code == 200
    my_response = response.json()
    assert 'access_token' in my_response
    assert my_response['access_token'] != ''
    assert my_response['token_type'] == 'bearer'
    token = my_response['access_token']
    token_type = my_response['token_type']
    AUTH_HEADER = {'Authorization': f'{token_type} {token}'}

def test_root():
    response = requests.get(SERVER + '/')
    assert response.status_code == 200
    assert response.json() == {'message': f'Falcon API Copyright (c) 2022, Thomas J. Daley, Esq. - Version v{API_VERSION}'}

def test_add_document_auth():
    response = requests.post(SERVER + PREFIX + '/documents', headers=AUTH_HEADER, json=DOC_1)
    assert response.status_code == 201
    assert response.json() == {'message': 'Document added', 'id': DOC_1['id']}

    # add a second document
    response = requests.post(SERVER + PREFIX + '/documents', headers=AUTH_HEADER, json=DOC_2)
    assert response.status_code == 201
    assert response.json() == {'message': 'Document added', 'id': DOC_2['id']}

    # add a third document with no id -- to be deleted in a later test
    global DEL_DOC_ID
    new_doc   = DOC_1.copy()
    del new_doc['id']
    new_doc['path'] = 'w:\\shared\\plano\\tjd\\open\\farrar\\discovery\\our production\\2022-09-15 BOA 2304.pdf'
    response = requests.post(SERVER + PREFIX + '/documents', headers=AUTH_HEADER, json=new_doc)
    assert response.status_code == 201
    json_response = response.json()
    assert 'message' in json_response
    assert json_response['message'] == 'Document added'
    assert 'id' in json_response
    DEL_DOC_ID = json_response['id']

def test_add_document_no_auth():
    response = requests.post(SERVER + PREFIX + '/documents', json=DOC_1)
    assert response.status_code == 401
    assert response.json() == {'detail': 'Not authenticated'}

def test_add_duplicate_document_id_auth():
    response = requests.post(SERVER + PREFIX + '/documents', headers=AUTH_HEADER, json=DOC_1)
    assert response.status_code == 409
    assert response.json() == {'detail': f"Document already exists: {DOC_1.get('id')}"}
@pytest.mark.slow
def test_add_duplicate_document_path_auth():
    dupe = DOC_1.copy()
    dupe['id'] = None
    response = requests.post(SERVER + PREFIX + '/documents', headers=AUTH_HEADER, json=dupe)
    assert response.status_code == 409
    assert response.json() == {'detail': f"Document already exists: {DOC_1.get('path')}"}

def test_get_document_auth():
    response = requests.get(SERVER + PREFIX + '/documents/?doc_id=' + DOC_1['id'], headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json() == DOC_1

def test_get_document_no_auth():
    response = requests.get(SERVER + PREFIX + '/documents/?doc_id=' + DOC_1['id'])
    assert response.status_code == 401
    assert response.json() == {'detail': 'Not authenticated'}

def test_get_missing_document_auth():
    response = requests.get(SERVER + PREFIX + '/documents/?doc_id=missing', headers=AUTH_HEADER)
    assert response.status_code == 404
    assert response.text == '{"detail":"Document not found: missing"}'
    assert response.json() == {'detail': "Document not found: missing"}

def test_update_document_auth():
    new_doc = DOC_1.copy()
    new_doc['title'] = '**New Title'
    response = requests.put(SERVER + PREFIX + '/documents/', headers=AUTH_HEADER, json=new_doc)
    assert response.status_code == 200
    assert response.json() == {'message': 'Document updated', 'id': new_doc['id']}

def delete_document_auth():
    response = requests.delete(SERVER + PREFIX + '/documents/' + DEL_DOC_ID, headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json() == {'message': 'Document deleted', 'id': DEL_DOC_ID}
