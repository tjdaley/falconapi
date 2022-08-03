"""
test_root.py - Test the root endpoint
"""
import requests
import pytest

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
TRACKER_ID_123 = {'id': '123', 'username': test_user['username'], 'name': 'Test Tracker', 'documents': {}}
TRACKER_ID_124 = {'id': '124', 'username': test_user['username'], 'name': 'Test Tracker', 'documents': {}}
TRACKER_NO_ID = {'username': test_user['username'], 'name': 'Test Tracker', 'documents': {}}
DOC_1 = {
        "id": "doc-1",
        "tracker_id":"123",
        "path":"x:\\shared\\plano\\tjd\\open\\farrar\\discovery\\our production\\2022-07-15 BOA 2304.pdf",
        "filename":"2022-07-15 BOA 2304.pdf",
        "title": "BOA 2304",
        "create_date":"07/01/2022"   
}
DOC_2 = {
    "id": "doc-2",
    "tracker_id": "123",
    "path": "x:\\shared\\plano\\tjd\\open\\farrar\\discovery\\our production\\2022-07-15 BOA 2304.pdf",
    "filename": "2022-07-15 BOA 2304.pdf",
    "title": "BOA 2304",
    "create_date": "07/01/2022"   
}


AUTH_HEADER = None
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

@pytest.mark.slow
def test_add_tracker_auth():
    response = requests.post(SERVER + PREFIX + '/trackers', json=TRACKER_ID_123, headers=AUTH_HEADER)
    assert response.status_code == 201
    assert response.json() == {'message': 'Tracker created', 'id': '123'}

def test_add_tracker_no_auth():
    response = requests.post(SERVER + PREFIX + '/trackers', json=TRACKER_ID_123)
    assert response.status_code == 401

def test_add_duplicate_tracker_auth():
    response = requests.post(SERVER + PREFIX + '/trackers', json=TRACKER_ID_124, headers=AUTH_HEADER)
    assert response.status_code == 201
    assert response.json() == {'message': 'Tracker created', 'id': '124'}
    response = requests.post(SERVER + PREFIX + '/trackers', json=TRACKER_ID_124, headers=AUTH_HEADER)
    assert response.status_code == 409
    assert response.json() == {'detail': 'Tracker already exists: 124'}

def test_get_tracker_auth():
    response = requests.get(SERVER + PREFIX + '/trackers?tracker_id=123', headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json() == TRACKER_ID_123

def test_get_tracker_no_auth():
    response = requests.get(SERVER + PREFIX + '/trackers?tracker_id=123')
    assert response.status_code == 401

def test_get_tracker_not_found_auth():
    response = requests.get(SERVER + PREFIX + '/trackers?tracker_id=999', headers=AUTH_HEADER)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Tracker not found: 999'}

def test_get_tracker_not_found_no_auth():
    response = requests.get(SERVER + PREFIX + '/trackers?tracker_id=999')
    assert response.status_code == 401

def test_get_trackers_for_named_user_auth():
    response = requests.get(SERVER + PREFIX + f"/trackers/user?username={test_user['username']}", headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json() == [TRACKER_ID_123, TRACKER_ID_124]

def test_get_trackers_for_logged_in_user_auth():
    response = requests.get(SERVER + PREFIX + f"/trackers/user", headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json() == [TRACKER_ID_123, TRACKER_ID_124]

def test_get_trackers_for_user_no_auth():
    response = requests.get(SERVER + PREFIX + f"/trackers/user?username={test_user['username']}")
    assert response.status_code == 401

def test_delete_tracker_auth():
    response = requests.delete(SERVER + PREFIX + '/trackers/124', headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json() == {'message': 'Tracker deleted', 'id': '124'}

def test_delete_tracker_no_auth():
    response = requests.delete(SERVER + PREFIX + '/trackers/124')
    assert response.status_code == 401

def test_delete_tracker_not_found():
    response = requests.delete(SERVER + PREFIX + '/trackers/999', headers=AUTH_HEADER)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Tracker not found: 999'}

@pytest.mark.slow
def test_add_document_auth():
    response = requests.post(SERVER + PREFIX + '/trackers/123/documents', json=DOC_1, headers=AUTH_HEADER)
    assert response.status_code == 201
    assert response.json() == {'message': 'Document added', 'id': 'doc-1'}

def test_add_document_no_auth():
    response = requests.post(SERVER + PREFIX + '/trackers/123/documents', json=DOC_1)
    assert response.status_code == 401

def test_add_duplicate_document():
    path = DOC_2.get('path')
    response = requests.post(SERVER + PREFIX + '/trackers/123/documents', json=DOC_2, headers=AUTH_HEADER)
    assert response.status_code == 201
    assert response.json() == {'message': 'Document added', 'id': 'doc-2'}
    response = requests.post(SERVER + PREFIX + '/trackers/123/documents', json=DOC_2, headers=AUTH_HEADER)
    assert response.status_code == 409
    assert response.json() == {'detail': f'Document already exists: {path}'}

@pytest.mark.slow
def test_get_document_auth():
    response = requests.get(SERVER + PREFIX + '/trackers/document?tracker_id=123&document_id=doc-1', headers=AUTH_HEADER)
    assert response.status_code == 200
    my_response = response.json()
    assert my_response.get('id') == 'doc-1' # id is returned in the response
    assert my_response.get('path') == DOC_1.get('path') # path is returned in the response
    assert my_response.get('tracker_id') == '123' # tracker_id is returned in the response  

def test_get_document_no_auth():
    response = requests.get(SERVER + PREFIX + '/trackers/document?tracker_id=123&document_id=doc-1')
    assert response.status_code == 401

def test_get_documents_auth():
    response = requests.get(SERVER + PREFIX + '/trackers/documents?tracker_id=123', headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json() == {
        "doc-1": {
            "id": "doc-1",
            "tracker_id": "123",
            "path": "x:\\shared\\plano\\tjd\\open\\farrar\\discovery\\our production\\2022-07-15 BOA 2304.pdf",
            "filename": "2022-07-15 BOA 2304.pdf",
            "title": "BOA 2304",
            "create_date": "07/01/2022",
            "document_date": None,
            "beginning_bates": None,
            "ending_bates": None,
            "page_count": None,
            "bates_pattern": None
        },
        "doc-2": {
            "id": "doc-2",
            "tracker_id": "123",
            "path": "x:\\shared\\plano\\tjd\\open\\farrar\\discovery\\our production\\2022-07-15 BOA 2304.pdf",
            "filename": "2022-07-15 BOA 2304.pdf",
            "title": "BOA 2304",
            "create_date": "07/01/2022",
            "document_date": None,
            "beginning_bates": None,
            "ending_bates": None,
            "page_count": None,
            "bates_pattern": None
        }
    }

def test_get_documents_no_auth():
    response = requests.get(SERVER + PREFIX + '/trackers/documents?tracker_id=123')
    assert response.status_code == 401

def test_delete_document_auth():
    response = requests.delete(SERVER + PREFIX + '/trackers/123/documents/doc-1', headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json() == {'message': 'Document deleted', 'id': 'doc-1'}

def test_delete_document_no_auth():
    response = requests.delete(SERVER + PREFIX + '/trackers/123/documents/doc-1')
    assert response.status_code == 401

def test_delete_nonexistent_document():
    response = requests.delete(SERVER + PREFIX + '/trackers/123/documents/doc-999', headers=AUTH_HEADER)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Document not found: doc-999'}

def test_add_tracker_no_id_auth():
    response = requests.post(SERVER + PREFIX + '/trackers', json={'username': 'test', 'name': 'Test Tracker'}, headers=AUTH_HEADER)
    assert response.status_code == 201
    assert response.json().get('message') == 'Tracker created'

def test_add_tracker_no_id_no_auth():
    response = requests.post(SERVER + PREFIX + '/trackers', json={'username': 'test', 'name': 'Test Tracker'})
    assert response.status_code == 401

def test_add_document_no_id_auth():
    doc = {
        "tracker_id":"123",
        "path":"x:\\shared\\plano\\tjd\\open\\farrar\\discovery\\our production\\2022-07-15 BOA 2304.pdf",
        "filename":"2022-07-15 BOA 2304.pdf",
        "title": "BOA 2304",
        "create_date":"07/01/2022"   
    }
    response = requests.post(SERVER + PREFIX + '/trackers/123/documents', json=doc, headers=AUTH_HEADER)
    assert response.status_code == 201
    assert response.json().get('message') == 'Document added'

def test_add_document_no_id_no_auth():
    doc = {
        "tracker_id":"123",
        "path":"x:\\shared\\plano\\tjd\\open\\farrar\\discovery\\our production\\2022-07-15 BOA 2304.pdf",
        "filename":"2022-07-15 BOA 2304.pdf",
        "title": "BOA 2304",
        "create_date":"07/01/2022"   
    }
    response = requests.post(SERVER + PREFIX + '/trackers/123/documents', json=doc)
    assert response.status_code == 401
