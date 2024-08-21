"""
discovery_requests_table.py - DiscoveryRequests Table
"""
from datetime import datetime
from functools import lru_cache
from typing import List
from uuid import uuid4
from database.db import Database
from models.discovery_requests import DiscoveryRequest
from database.clients_table import ClientsTable

from falconlogger.flogger import FalconLogger

COLLECTION = 'discovery_requests'

class MissingSearchParamException(Exception):
    """
    Exception for missing client
    """
    def __init__(self, message: str = "Must specify either id or billing_number") -> None:
        super().__init__(message)

class MissingUsernameException(Exception):
    """
    Exception for missing username
    """
    def __init__(self, message: str = "Must specify username") -> None:
        super().__init__(message)

class DiscoveryRequestsTable(Database):
    """
    Class for interacting with the discovery requests table
    """
    def __init__(self, fail_silent: bool = True) -> None:
        super().__init__(fail_silent=fail_silent)
        self.collection = self.conn[self.database][COLLECTION]
        self.clients_table = ClientsTable()
        self.files = self.conn[self.database]['discovery_files']

    def get(self, request_id: str, username: str) -> DiscoveryRequest:
        """
        Get a discovery request from the database.

        Args:
            request_id (str): The request ID.
            username (str): The user's username.

        Returns:
            DiscoveryRequest: The DiscoveryRequest object if the request exists, None otherwise.
        """
        request = self.collection.find_one({'id': request_id})
        client_id = self.client_id(request.get('file_id'))
        if not request:
            return None
        if not self.is_authorized(username, client_id=client_id):
            return None
        return DiscoveryRequest(**request)
    
    def get_all(self, file_id: str, username: str) -> List[DiscoveryRequest]:
        """
        Get a list of all discovery requests for the specified discovery file.

        Args:
            file_id (str): The client's ID.
            username (str): The user's username.

        Returns:
            List[Client]: The Client object if the client exists, empty list otherwise.
        """
        client_id = self.files.find_one({'id': file_id})['client_id']
        if not self.is_authorized(username, client_id):
            return []
        requests = self.collection.find({'file_id': file_id})
        return [DiscoveryRequest(**request) for request in requests]

    def add(self, request: DiscoveryRequest, username: str) -> dict:
        """
        Create a discovery request in the database
        """
        request.created_by = username
        request.create_date = datetime.now().strftime("%Y-%m-%d")
        client_id = self.client_id(request.file_id)
        if not self.is_authorized(username=username, client_id=client_id):
            if self.fail_silent:
                return self.insert_one_result(request.id)
            raise Exception(f"User {username} is not authorized to create a request for client {request.client_id}")

        return self.collection.insert_one(request.model_dump())

    def update(self, request: DiscoveryRequest, username: str) -> dict:
        """
        Update a discovery request in the database.

        Only the request, interpretations, privileges, objections, response, responsive_classifications, lookback_date and due_date fields will be updated.

        Retrieve the request from the database, update the fields, and save it back.
        Otherwise the version will be out of sync and the update will fail.

        Args:
            request (DiscoveryRequest): The discovery request to update.
            username (str): The user's username.

        Returns:
            dict: The result of the update operation.
        """
        original_request = self.collection.find_one({'id': request.id})
        client_id = self.client_id(original_request.get('file_id'))
        if not self.is_authorized(username=username, client_id=client_id):
            if self.fail_silent:
                return self.update_one_result(request.id)
            raise Exception(f"User {username} is not authorized to update request {request.id}")
        return self.collection.update_one(
            {'id': request.id, 'version': request.version},
            {'$set': {
                'request_text': request.request_text,
                'interpretations': request.interpretations,
                'privileges': request.privileges,
                'objections': request.objections,
                'response': request.response,
                'responsive_classifications': request.responsive_classifications,
                'lookback_date': request.lookback_date,
                'request_number': request.request_number,
                'version': str(uuid4()),
                'last_updated_by': username,
                'last_updated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
        )
    
    def delete(self, request_id: str, username: str) -> dict:
        """
        Delete a client from the database

        Only the user who created the client can delete it.

        Args:
            client_id (str): The client's ID.
            username (str): The user's username.

        Returns:
            dict: The result of the delete operation.
        """
        original_request = self.collection.find_one({'id': request_id})
        client_id = self.client_id(original_request.get('file_id'))
        if not self.is_authorized(username=username, client_id=client_id):
            if self.fail_silent:
                return self.delete_one_result(request_id)
            raise Exception(f"User {username} is not authorized to delete request {request_id}")
        return self.collection.delete_one(
            {'id': request_id}
        )

    def is_authorized(self, username: str, client_id: str = None, billing_number: str = None, wildcard_allowed=True) -> bool:
        """
        Check if a user is authorized to access a client.

        Args:
            client_id (str): The client's ID.
            username (str): The user's username.

        Returns:
            bool: True if the user is authorized, False otherwise.
        """
        if client_id == '*' and not wildcard_allowed:
            return False

        if client_id == '*':
            return True

        auth_clients: dict = self.clients_table.get_authorized_clients(username)
        if not auth_clients:
            return False
        
        # if client_id is not None, check if the client_id is in the list of authorized clients
        if client_id:
            if client_id not in [client['id'] for client in auth_clients]:
                return False
            return True
        
        # if billing_number is not None, check if the billing_number is in the list of authorized clients
        if billing_number:
            if billing_number not in [client['billing_number'] for client in auth_clients]:
                return False
            return True    
        return False
    
    # This function will tend to be called in batches with the same file_id, so we cache the results
    @lru_cache(maxsize=128)
    def client_id(self, file_id) -> str:
        """
        Get the client ID by reference to the file record
        """
        file_doc = self.files.find_one({'id': file_id})
        return file_doc['client_id']
