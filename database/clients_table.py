"""
users_table.py - Users Table
"""
from typing import List
from uuid import uuid4
from database.db import Database
from models.client import Client

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

    def get_clients(self, id: str = None, billing_number: str = None, username: str = None) -> List[Client]:
        """
        Get clients from the database.

        Must specify either id or billing_id, and username.

        Args:
            id (str): The client's ID. Use '*' to get all clients.
            billing_number (str): The client's billing number.
            username (str): The user's username.

        Returns:
            List[Client]: The Client object if the client exists, empty list otherwise.
        """
        if not id and not billing_number:
            raise MissingSearchParamException()
        if not username:
            raise MissingUsernameException()
        query = {}
        if id and id != '*':
            query['id'] = id
        if billing_number:
            query['billing_number'] = billing_number
        query['$or'] = [{'created_by': username}, {'authorized_users': username}]
        client_docs = self.collection.find(query)
        return [Client(**client_doc) for client_doc in client_docs]

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
                'enabled': client.enabled,
                'version': str(uuid4())
                }
            }
        )
    
    def add_authorized_user(self, id: str, username: str, authorized_user: str) -> dict:
        """
        Add an authorized user to a client

        Args:
            id (str): The client's ID.
            username (str): The user's username.
            authorized_user (str): The authorized user's username.

        Returns:
            dict: The result of the update operation.
        """
        return self.collection.update_one(
            {'id': id, 'created_by': username},
            [
                {'$push': {'authorized_users': authorized_user}},
                {'$set': {'version': str(uuid4())}}
            ]
        )
    
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
        return self.collection.update_one(
            {'id': client_id, 'created_by': username},
            [
                {'$pull': {'authorized_users': authorized_user}},
                {'$set': {'version': str(uuid4())}}
            ]
        )

    def delete_client(self, id: str, username: str) -> dict:
        """
        Delete a client from the database

        Only the user who created the client can delete it.

        Args:
            id (str): The client's ID.
            username (str): The user's username.

        Returns:
            dict: The result of the delete operation.
        """
        return self.collection.update_one(
            {'id': id, 'created_by': username},
            {'$set': {'enabled': False}}
        )
