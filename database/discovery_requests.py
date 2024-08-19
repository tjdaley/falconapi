"""
discovery_requests_table.py - DiscoveryRequests Table
"""
from typing import List
from uuid import uuid4
from database.db import Database
from models.discovery_requests import DiscoveryRequest, DiscoveryRequests, ServedRequest, ServedRequests
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

    def get_request_service_list(self, client_id: str = None, billing_number: str = None, username: str = None) -> ServedRequests:
        """
        Get list of each time discovery was served from the database.

        Must specify either id or billing_id, and username. If you specify both id and billing_id,
        only id will be used.

        Args:
            client_id (str): The client's ID. Use '*' to get all clients.
            billing_number (str): The client's billing number.
            username (str): The user's username.

        Returns:
            List[Client]: The Client object if the client exists, empty list otherwise.
        """
        if not client_id and not billing_number:
            raise MissingSearchParamException()
        if not username:
            raise MissingUsernameException()
        
        if not self.is_authorized(username, client_id, billing_number):
            return ServedRequests(requests=[])
        
        auth_clients: dict = self.clients_table.get_authorized_clients(username)

        if client_id and client_id != '*':
            client_ids = [client_id]
        elif client_id == '*':
            client_ids = [client['id'] for client in auth_clients]
        
        if billing_number and not client_id:
            # get the client_id from the billing_number
            client_ids = [client['id'] for client in auth_clients if client['billing_number'] == billing_number][0]

        query = {'client_id': {'$in': client_ids}}
        request_docs = self.collection.find(query)

        # summarize the requests by combining the request_type, served_by, and served_date and counting the number of requests
        served_requests = {}
        boundary = '::'
        for request_doc in request_docs:
            client_id = request_doc['client_id'].replace(boundary, ' ').strip()
            request_type = request_doc['request_type'].replace(boundary, ' ').strip().title()
            served_by = request_doc['served_by'].replace(boundary, ' ').strip().title()
            served_date = request_doc['served_date'].replace(boundary, ' ').strip()
            key = f"{client_id}{boundary}{request_type}{boundary}{served_by}{boundary}{served_date}"
            if key in served_requests:
                served_requests[key]['request_count'] += 1
            else:
                served_requests[key]['request_count'] = 1
                served_requests[key]['client_id'] = client_id
                served_requests[key]['request_type'] = request_type
                served_requests[key]['served_by'] = served_by
                served_requests[key]['served_date'] = served_date
                served_requests[key]['due_date'] = request_doc['due_date']

            if request_doc.get('response'):
                if 'response_count' not in served_requests[key]:
                    served_requests[key]['response_count'] = 1
                else:
                    served_requests[key]['response_count'] += 1

        request_list = [ServedRequest(**served_request) for served_request in served_requests.values()]
        return ServedRequests(request_list)
    
    def get_requests(self, served_by: str, served_date: str, request_type: str, client_id: str = None, username: str = None) -> ServedRequests:
        """
        Get list of each request of a batch of requests from the database.

        Args:
            served_by (str): The person who served the request.
            served_date (str): The date the request was served.
            request_type (str): The type of request.
            client_id (str): The client's ID.
            username (str): The user's username.

        Returns:
            List[Client]: The Client object if the client exists, empty list otherwise.
        """
        if not client_id:
            raise MissingSearchParamException()
        if not username:
            raise MissingUsernameException()
        
        if not self.is_authorized(username, client_id):
            return ServedRequests(requests=[])
        
        auth_clients: dict = self.clients_table.get_authorized_clients(username)

        query = {'client_id': client_id, 'served_by': served_by, 'served_date': served_date, 'request_type': request_type}
        request_docs = self.collection.find(query)

        return ServedRequests([ServedRequest(**served_request) for served_request in request_docs])
    
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
            print("@@@@ Wildcard not allowed")
            return False

        if client_id == '*':
            print("@@@@ Wildcard allowed")
            return True

        auth_clients: dict = self.clients_table.get_authorized_clients(username)
        if not auth_clients:
            print("@@@@ No authorized clients")
            return False
        
        # if client_id is not None, check if the client_id is in the list of authorized clients
        if client_id:
            if client_id not in [client['id'] for client in auth_clients]:
                print("@@@@ Client not authorized")
                print(f"Client ID: {client_id}")
                print(f"Authorized Clients: {[client['id'] for client in auth_clients]}")
                return False
            print("@@@@ Client authorized")
            return True
        
        # if billing_number is not None, check if the billing_number is in the list of authorized clients
        if billing_number:
            if billing_number not in [client['billing_number'] for client in auth_clients]:
                return False
            return True
        
        return False

    def create_request(self, request: DiscoveryRequest, username: str) -> dict:
        """
        Create a discovery request in the database
        """
        print(f"Creating request for {username}")
        print(f"Client ID: {request.client_id}")
        print(f"Request ID: {request.id}")
        if not self.is_authorized(username=username, client_id=request.client_id):
            if self.fail_silent:
                return self.insert_one_result(request.id)
            raise Exception(f"User {username} is not authorized to create a request for client {request.client_id}")

        return self.collection.insert_one(request.model_dump())

    def update_request(self, request: DiscoveryRequest, username: str) -> dict:
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
        if not self.is_authorized(username=username, client_id=original_request['client_id']):
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
                'due_date': request.due_date,
                'request_type': request.request_type,
                'served_by': request.served_by,
                'served_date': request.served_date,
                'request_number': request.request_number,
                'version': str(uuid4()),
                'last_updated_by': username,
                'last_updated_date': request.last_updated_date
                }
            }
        )
    
    def delete_request(self, request_id: str, username: str) -> dict:
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
        if not self.is_authorized(username=username, client_id=original_request['client_id']):
            if self.fail_silent:
                return self.delete_one_result(request_id)
            raise Exception(f"User {username} is not authorized to delete request {request_id}")
        return self.collection.delete_one(
            {'id': request_id}
        )
