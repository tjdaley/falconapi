"""
test_root.py - Test the root endpoint
"""
import requests


SERVER = "http://localhost:8000"
PREFIX = "/api/v1"


def test_root():
    response = requests.get(SERVER + '/')
    assert response.status_code == 200
    assert response.json() == {'message': 'Falcon API Copyright (c) 2022, Thomas J. Daley, Esq. - Version 1.0.0'}

def test_add_tracker():
    response = requests.post(SERVER + PREFIX + '/trackers', json={'id': '123', 'user_name': 'test', 'name': 'Test Tracker'})
    assert response.status_code == 201
    assert response.json() == {'message': 'Tracker created', 'id': '123'}

def test_add_duplicate_tracker():
    response = requests.post(SERVER + PREFIX + '/trackers', json={'id': '124', 'user_name': 'test', 'name': 'Test Tracker'})
    assert response.status_code == 201
    assert response.json() == {'message': 'Tracker created', 'id': '124'}
    response = requests.post(SERVER + PREFIX + '/trackers', json={'id': '124', 'user_name': 'test', 'name': 'Test Tracker'})
    assert response.status_code == 409
    assert response.json() == {'detail': 'Tracker already exists: 124'}

def test_get_tracker():
    response = requests.get(SERVER + PREFIX + '/trackers/123')
    assert response.status_code == 200
    assert response.json() == {
        "id": "123",
        "name": "Test Tracker",
        "user_name": "test",
        "documents": {}
    }

def test_get_tracker_not_found():
    response = requests.get(SERVER + PREFIX + '/trackers/999')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Tracker not found: 999'}

def test_get_trackers_for_user():
    response = requests.get(SERVER + PREFIX + '/trackers/user/test')
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": "123",
            "name": "Test Tracker",
            "user_name": "test",
            "documents": {}
        },
        {
            "id": "124",
            "name": "Test Tracker",
            "user_name": "test",
            "documents": {}
        }
    ]

def test_delete_tracker():
    response = requests.delete(SERVER + PREFIX + '/trackers/124')
    assert response.status_code == 200
    assert response.json() == {'message': 'Tracker deleted', 'id': '124'}

def test_delete_tracker_not_found():
    response = requests.delete(SERVER + PREFIX + '/trackers/999')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Tracker not found: 999'}

def test_add_document():
    doc = {
        "id": "doc-1",
        "tracker_id":"123",
        "path":"x:\\shared\\plano\\tjd\\open\\farrar\\discovery\\our production\\2022-07-15 BOA 2304.pdf",
        "filename":"2022-07-15 BOA 2304.pdf",
        "title": "BOA 2304",
        "create_date":"07/01/2022"   
}
    response = requests.post(SERVER + PREFIX + '/trackers/123/documents', json=doc)
    assert response.status_code == 201
    assert response.json() == {'message': 'Document added', 'id': 'doc-1'}

def test_add_duplicate_document():
    path = "x:\\shared\\plano\\tjd\\open\\farrar\\discovery\\our production\\2022-07-15 BOA 2304.pdf"
    doc = {
        "id": "doc-2",
        "tracker_id": "123",
        "path": path,
        "filename": "2022-07-15 BOA 2304.pdf",
        "title": "BOA 2304",
        "create_date": "07/01/2022"   
    }
    response = requests.post(SERVER + PREFIX + '/trackers/123/documents', json=doc)
    assert response.status_code == 201
    assert response.json() == {'message': 'Document added', 'id': 'doc-2'}
    response = requests.post(SERVER + PREFIX + '/trackers/123/documents', json=doc)
    assert response.status_code == 409
    assert response.json() == {'detail': f'Document already exists: {path}'}

def test_get_documents():
    response = requests.get(SERVER + PREFIX + '/trackers/123/documents')
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

def test_delete_document():
    response = requests.delete(SERVER + PREFIX + '/trackers/123/documents/doc-1')
    assert response.status_code == 200
    assert response.json() == {'message': 'Document deleted', 'id': 'doc-1'}

def test_delete_nonexistent_document():
    response = requests.delete(SERVER + PREFIX + '/trackers/123/documents/doc-999')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Document not found: doc-999'}

def test_add_tracker_no_id():
    response = requests.post(SERVER + PREFIX + '/trackers', json={'user_name': 'test', 'name': 'Test Tracker'})
    assert response.status_code == 201
    assert response.json().get('message') == 'Tracker created'

def test_add_document_no_id():
    doc = {
        "tracker_id":"123",
        "path":"x:\\shared\\plano\\tjd\\open\\farrar\\discovery\\our production\\2022-07-15 BOA 2304.pdf",
        "filename":"2022-07-15 BOA 2304.pdf",
        "title": "BOA 2304",
        "create_date":"07/01/2022"   
    }
    response = requests.post(SERVER + PREFIX + '/trackers/123/documents', json=doc)
    assert response.status_code == 201
    assert response.json().get('message') == 'Document added'

