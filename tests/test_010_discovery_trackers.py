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
    assert response.json() == {'detail': 'Tracker already exists'}

def test_get_tracker_auth():
    response = requests.get(SERVER + PREFIX + '/trackers?tracker_id=123', headers=AUTH_HEADER)
    assert response.status_code == 200
    print(json.dumps(response.json(), indent=4))
    print('*'*80)
    print(json.dumps(TRACKER_ID_123, indent=4))
    print('*'*80)
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
    print(json.dumps(response.json(), indent=4))
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

def test_add_document_auth():
    response = requests.post(SERVER + PREFIX + '/trackers/documents', json=DOC_2, headers=AUTH_HEADER)
    response = requests.post(SERVER + PREFIX + '/trackers/documents', json=DOC_1, headers=AUTH_HEADER)
    if response.status_code != 201:
        assert response.json() == {'message': 'Document created', 'id': 'doc-1'}
    assert response.status_code == 201
    assert response.json() == {'message': 'Document created', 'id': 'doc-1'}

def test_link_document_auth():
    #/{tracker_id}/documents/{document_id}
    response = requests.patch(SERVER + PREFIX + '/trackers/123/documents/doc-1', headers=AUTH_HEADER)
    assert response.status_code == 202
    assert response.json() == {'message': 'Document linked to tracker', 'id': 'doc-1'}

def test_link_document_no_auth():
    response = requests.patch(SERVER + PREFIX + '/trackers/123/documents/doc-1')
    assert response.status_code == 401

def test_link_duplicate_document():
    doc_id = DOC_2.get('id')
    response = requests.patch(SERVER + PREFIX + f'/trackers/123/documents/{doc_id}', headers=AUTH_HEADER)
    assert response.status_code == 202
    assert response.json() == {'message': 'Document linked to tracker', 'id': doc_id}
    response = requests.patch(SERVER + PREFIX + f'/trackers/123/documents/{doc_id}', headers=AUTH_HEADER)
    assert response.status_code == 409
    assert response.json() == {'detail': f'Document already linked: {doc_id}'}

def test_get_document_auth():
    response = requests.get(SERVER + PREFIX + '/trackers/document?tracker_id=123&document_id=doc-1', headers=AUTH_HEADER)
    assert response.status_code == 200
    my_response = response.json()
    assert my_response.get('id') == 'doc-1' # id is returned in the response
    assert my_response.get('path') == DOC_1.get('path') # path is returned in the response

def test_get_document_no_auth():
    response = requests.get(SERVER + PREFIX + '/trackers/document?tracker_id=123&document_id=doc-1')
    assert response.status_code == 401

@pytest.mark.slow
def test_get_documents_auth():
    response = requests.get(SERVER + PREFIX + '/trackers/documents?tracker_id=123', headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json() == [DOC_1, DOC_2]

def test_get_documents_no_auth():
    response = requests.get(SERVER + PREFIX + '/trackers/documents?tracker_id=123')
    assert response.status_code == 401

def test_unlink_document_auth():
    response = requests.delete(SERVER + PREFIX + '/trackers/123/documents/doc-1', headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json() == {'message': 'Document unlinked from tracker', 'id': 'doc-1'}

def test_unlink_document_no_auth():
    response = requests.delete(SERVER + PREFIX + '/trackers/123/documents/doc-1')
    assert response.status_code == 401

def test_unlink_nonexistent_document():
    response = requests.delete(SERVER + PREFIX + '/trackers/123/documents/doc-999', headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json() == {'message': 'Document unlinked from tracker', 'id': 'doc-999'}

def test_add_tracker_no_id_auth():
    response = requests.post(SERVER + PREFIX + '/trackers', json={'username': 'test', 'name': 'Test Tracker'}, headers=AUTH_HEADER)
    assert response.status_code == 201
    assert response.json().get('message') == 'Tracker created'

def test_add_tracker_no_id_no_auth():
    response = requests.post(SERVER + PREFIX + '/trackers', json={'username': 'test', 'name': 'Test Tracker'})
    assert response.status_code == 401

def test_add_document_no_id_auth():
    doc = {
        "path":"x:\\shared\\plano\\tjd\\open\\farrar\\discovery\\our production\\2022-07-15 BOA 2304.pdf",
        "filename":"2022-07-15 BOA 2304.pdf",
        "title": "BOA 2304",
        "create_date":"07/01/2022",
        "type": "application/pdf"  
    }
    response = requests.post(SERVER + PREFIX + '/trackers/documents', json=doc, headers=AUTH_HEADER)
    if response.status_code != 201:
        print('***', response.status_code, response.json())
    assert response.status_code == 201
    assert response.json().get('message') == 'Document created'

def test_add_document_no_id_no_auth():
    doc = {
        "path":"x:\\shared\\plano\\tjd\\open\\farrar\\discovery\\our production\\2022-07-15 BOA 2304.pdf",
        "filename":"2022-07-15 BOA 2304.pdf",
        "title": "BOA 2304",
        "create_date":"07/01/2022",
        "type": "application/pdf"
    }
    response = requests.post(SERVER + PREFIX + '/trackers/documents', json=doc)
    assert response.status_code == 401
