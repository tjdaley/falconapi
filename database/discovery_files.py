"""
discovery_files_table.py - DiscoveryFiles Table
"""
from datetime import datetime
from typing import List
from uuid import uuid4
from database.db import Database
from models.discovery_requests import DiscoveryFile, DiscoveryFileSummary
from database.clients_table import ClientsTable

from falconlogger.flogger import FalconLogger

COLLECTION = 'discovery_files'

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

class DocumentNotFoundException(Exception):
    """
    Exception for missing document
    """
    def __init__(self, message: str = "Document not found") -> None:
        super().__init__(message)

class DiscoveryFileTable(Database):
    """
    Class for interacting with the discovery files table
    """
    def __init__(self, fail_silent: bool = True) -> None:
        super().__init__(fail_silent=fail_silent)
        self.collection = self.conn[self.database][COLLECTION]
        self.clients_table = ClientsTable()
        self.requests = self.conn[self.database]['discovery_requests']

    def add(self, discovery_file: DiscoveryFile, username: str) -> dict:
        """
        Add a discovery file to the database

        Args:
            discovery_file (DiscoveryFile): The discovery file to add.
            username (str): The user's username.

        Returns:
            dict: The result of the insert operation.
        """
        discovery_file.created_by = username
        discovery_file.create_date = datetime.now().strftime("%Y-%m-%d")
        discovery_file.id = str(uuid4())
        print("@@@@", discovery_file.model_dump())
        if not self.is_authorized(username, discovery_file.client_id):
            if self.fail_silent:
                return self.insert_one_result(discovery_file.id)
            raise Exception(f"User {username} is not authorized to add a discovery file for client {discovery_file.client_id}")
        return self.collection.insert_one(discovery_file.model_dump())

    def get(self, discovery_file_id: str, username: str) -> DiscoveryFile:
        """
        Get a discovery file from the database

        Args:
            discovery_file_id (str): The discovery file's ID.
            username (str): The user's username.

        Returns:
            DiscoveryFile: The DiscoveryFile object if the discovery file exists, None otherwise.
        """
        discovery_file = self.collection.find_one({'id': discovery_file_id})
        if not discovery_file:
            return None
        if not self.is_authorized(username, discovery_file.get('client_id')):
            return None
        return DiscoveryFile(**discovery_file)
    
    def get_all(self, client_id: str, username: str) -> List[DiscoveryFile]:
        """
        Get all discovery files from the database

        Args:
            client_id (str): The client's ID.
            username (str): The user's username.

        Returns:
            List[DiscoveryFile]: The DiscoveryFile object if the discovery file exists, empty list otherwise.
        """
        if not self.is_authorized(username, client_id):
            return []
        # Define the aggregation pipeline
        pipeline = [
            {
                "$lookup": {
                    "from": "discovery_requests",
                    "localField": "id",
                    "foreignField": "file_id",
                    "as": "requests"
                }
            },
            {
                "$project": {
                    "id": 1,
                    "client_id": 1,
                    "discovery_type": 1,
                    "service_date": 1,
                    "due_date": 1,
                    "party_name": 1,
                    "created_by": 1,
                    "create_date": 1,
                    "version": 1,
                    "request_count": {"$size": "$requests"}
                }
            }
        ]

        # Execute the aggregation query
        discovery_files = self.collection.aggregate(pipeline)

        # Convert the result to a list
        # result_list = list(result)
        return [DiscoveryFileSummary(**discovery_file) for discovery_file in discovery_files]
    
    def update(self, discovery_file: DiscoveryFile, username: str) -> dict:
        """
        Update a discovery file in the database

        Args:
            discovery_file (DiscoveryFile): The discovery file to update.
            username (str): The user's username.

        Returns:
            dict: The result of the update operation.
        """
        original_discovery_file = self.collection.find_one({'id': discovery_file.id})
        if not self.is_authorized(username, original_discovery_file.get('client_id')):
            if self.fail_silent:
                return self.update_one_result(discovery_file.id)
            raise Exception(f"User {username} is not authorized to update discovery file {discovery_file.id}")
        return self.collection.update_one(
            {'id': discovery_file.id},
            {'$set': {
                'client_id': discovery_file.client_id,
                'discovery_type': discovery_file.discovery_type,
                'service_date': discovery_file.service_date,
                'due_date': discovery_file.due_date,
                'party_name': discovery_file.party_name,
                'created_by': discovery_file.created_by,
                'create_date': discovery_file.create_date,
                'version': str(uuid4())
                }
            }
        )
    
    def delete(self, discovery_file_id: str, username: str) -> dict:
        """
        Delete a discovery file from the database

        Args:
            discovery_file_id (str): The discovery file's ID.
            username (str): The user's username.

        Returns:
            dict: The result of the delete operation.
        """
        discovery_file = self.collection.find_one({'id': discovery_file_id})
        if not self.is_authorized(username, discovery_file.get('client_id')):
            if self.fail_silent:
                return self.delete_one_result(discovery_file_id)
            raise Exception(f"User {username} is not authorized to delete discovery file {discovery_file_id}")
        
        # Delete the document
        delete_document_result = self.collection.delete_one({"id": discovery_file_id})

        if delete_document_result.deleted_count > 0:
            # If the document was successfully deleted, delete the related requests
            delete_requests_result = self.requests.delete_many({"file_id": discovery_file_id})
            print(f"Deleted {delete_requests_result.deleted_count} related requests.")
        else:
            message = f"Document not found or already deleted: {discovery_file_id}"
            raise DocumentNotFoundException(message=message)
        return delete_document_result

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
    