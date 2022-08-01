"""
test_root.py - Test the root endpoint
"""
import requests

API_VERSION = '1_0'
SERVER = 'http://localhost:8000'
PREFIX = f'/api/v{API_VERSION}'


test_user = {
    'email': 'test_user@test.copm',
    'username': 'test_user@test.com',
    'password': 'test_password',
    'full_name': 'Test User'
}
def test_add_user():
    response = requests.post(SERVER + PREFIX + '/users/register', json=test_user)
    assert response.status_code == 201
    my_response = response.json()
    assert my_response['message'] == 'User created successfully'
    assert my_response['username'] == test_user['username']
    assert my_response['status'] == 'success'
    assert 'user_id' in my_response
    assert my_response['user_id'] != ''

def test_add_duplicate_user():
    response = requests.post(SERVER + PREFIX + '/users/register', json=test_user)
    assert response.status_code == 400
    assert response.json() == {'detail': 'User already exists'}

TOKEN = None
TOKEY_TYPE = None
def test_authenticate_user():
    global TOKEN, TOKEY_TYPE
    response = requests.post(SERVER + PREFIX + '/users/token', data={'username': test_user['username'], 'password': test_user['password']})
    assert response.status_code == 200
    my_response = response.json()
    assert 'access_token' in my_response
    assert my_response['access_token'] != ''
    assert my_response['token_type'] == 'bearer'
    TOKEN = my_response['access_token']
    TOKEY_TYPE = my_response['token_type']

def test_get_current_user():
    response = requests.get(SERVER + PREFIX + '/users/me', headers={'Authorization': f'{TOKEY_TYPE} {TOKEN}'})
    assert response.status_code == 200
    my_response = response.json()
    assert my_response['username'] == test_user['username']
    assert my_response['full_name'] == test_user['full_name']
    assert my_response['email'] == test_user['email']
    assert my_response['disabled'] == False
    assert my_response['admin'] == False

def test_authenticate_wrong_password():
    response = requests.post(SERVER + PREFIX + '/users/token', data={'username': test_user['username'], 'password': test_user['password']+'$'})
    assert response.status_code == 401
    my_response = response.json()
    assert my_response['detail'] == 'Incorrect username or password'

def test_authenticate_wrong_username():
    response = requests.post(SERVER + PREFIX + '/users/token', data={'username': test_user['username']+'$', 'password': test_user['password']})
    assert response.status_code == 401
    my_response = response.json()
    assert my_response['detail'] == 'Incorrect username or password'
