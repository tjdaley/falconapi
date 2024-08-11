"""
users_table.py - Users Table
"""
from typing import List
from uuid import uuid4
from database.db import Database
from models.client import Client
from pymongo.results import InsertOneResult, UpdateResult  # NOQA

COLLECTION = 'clients'

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

class ClientsTable(Database):
    """
    Class for interacting with the clients table
    """
    def __init__(self) -> None:
        super().__init__()
        self.collection = self.conn[self.database][COLLECTION]

    def get_clients(self, client_id: str = None, billing_number: str = None, username: str = None) -> List[Client]:
        """
        Get clients from the database.

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
        query = {}
        if client_id and client_id != '*':
            query['id'] = client_id
        if billing_number and not client_id:
            query['billing_number'] = billing_number
        query['$or'] = [{'created_by': username}, {'authorized_users': username.lower()}]
        client_docs = self.collection.find(query)
        return [Client(**client_doc) for client_doc in client_docs]
    
    def get_authorized_clients(self, username: str) -> List[dict]:
        """
        Get a list of client IDs and billing numbers that a user is authorized to access.

        Args:
            username (str): The user's username.

        Returns:
            List[dict]: A list of client IDs and billing numbers. {'id': 'uuid', 'billing_number': '1234'}
        """
        query = {'$or': [{'created_by': username}, {'authorized_users': username.lower()}]}
        client_docs = self.collection.find(query , {'id': 1, 'billing_number': 1})
        return [{'id': client_doc['id'], 'billing_number': client_doc['billing_number']} for client_doc in client_docs]
    
    def is_authorized(self, client_id: str, username: str) -> bool:
        """
        Check if a user is authorized to access a client.

        Args:
            client_id (str): The client's ID.
            username (str): The user's username.

        Returns:
            bool: True if the user is authorized, False otherwise.
        """
        client = self.collection.find_one({'id': client_id})
        if not client:
            return False
        return username.lower() in client['authorized_users']

    def create_client(self, client: Client) -> dict:
        """
        Create a client in the database
        """
        existing_client = self.get_clients(billing_number=client.billing_number, username=client.created_by)
        if existing_client:
            if self.fail_silent:
                return self.insert_one_result(client.name)
            raise Exception(f"Client {client.billing_number} already exists")
        if client.created_by not in client.authorized_users:
            client.authorized_users.append(client.created_by)

        client.authorized_users = [au.lower() for au in client.authorized_users]
        return self.collection.insert_one(client.model_dump())

    def update_client(self, client: Client, username: str) -> dict:
        """
        Update a client in the database.

        Only the name, billing_number, and enabled fields will be updated.

        Only the user who created the client can update it.
        
        Retrieve the client from the database, update the fields, and save it back.
        Otherwise the version will be out of sync and the update will fail.

        Args:
            client (Client): The client to update.
            username (str): The user's username.

        Returns:
            dict: The result of the update operation.
        """
        return self.collection.update_one(
            {'id': client.id, 'created_by': username, 'version': client.version},
            {'$set': {
                'name': client.name,
                'billing_number': client.billing_number,
                'us_state': client.us_state,
                'county': client.county,
                'court_name': client.court_name,
                'cause_number': client.cause_number,
                'court_type': client.court_type,
                'matter_type': client.matter_type,
                'enabled': client.enabled,
                'version': str(uuid4())
                }
            }
        )
    
    def add_authorized_user(self, client_id: str, username: str, authorized_user: str) -> dict:
        """
        Add an authorized user to a client.

        Args:
            client_id (str): The client's ID.
            username (str): The user's username.
            authorized_user (str): The authorized user's username.

        Returns:
            dict: The result of the update operation.
        """
        # First update: Add to authorized_users
        result = self.collection.update_one(
            {'id': client_id, 'created_by': username},
            {'$addToSet': {'authorized_users': authorized_user.lower()}}
        )

        # NOTE: We the update is broken into two parts to ensure the version is only
        # updated if the authorized_users field is updated. If we combined the two
        # updates into one, the version would be updated even if the authorized_users
        # field was not updated.
        
        # Second update: Update the version
        if result.modified_count > 0:
            self.collection.update_one(
                {'id': client_id, 'created_by': username},
                {'$set': {'version': str(uuid4())}}
            )

        return result
    
    def remove_authorized_user(self, client_id: str, username: str, authorized_user: str) -> dict:
        """
        Remove an authorized user from a client

        Only the user who created the client can remove an authorized user.

        Args:
            client_id (str): The client's ID.
            username (str): The user's username.
            authorized_user (str): The authorized user's username.

        Returns:
            dict: The result of the update operation.
        """
        # First update: Add to authorized_users
        result = self.collection.update_one(
            {'id': client_id, 'created_by': username},
            {'$pull': {'authorized_users': authorized_user.lower()}}
        )
        
        # NOTE: We the update is broken into two parts to ensure the version is only
        # updated if the authorized_users field is updated. If we combined the two
        # updates into one, the version would be updated even if the authorized_users
        # field was not updated.
        
        # Second update: Update the version
        if result.modified_count > 0:
            self.collection.update_one(
                {'id': client_id, 'created_by': username},
                {'$set': {'version': str(uuid4())}}
            )

        return result

    def delete_client(self, client_id: str, username: str) -> dict:
        """
        Delete a client from the database

        Only the user who created the client can delete it.

        Args:
            client_id (str): The client's ID.
            username (str): The user's username.

        Returns:
            dict: The result of the delete operation.
        """
        return self.collection.update_one(
            {'id': client_id, 'created_by': username},
            {'$set': {'enabled': False}}
        )
