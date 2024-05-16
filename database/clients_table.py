"""
users_table.py - Users Table
"""
from database.db import Database
from models.client import Client

COLLECTION = 'clients'

class ClientsTable(Database):
    """
    Class for interacting with the clients table
    """
    def __init__(self) -> None:
        super().__init__()
        self.collection = self.conn[self.database][COLLECTION]

    def get_client(self, id: str, username: str) -> Client:
        """
        Get a client from the database
        """
        if id == '*':
            client_docs = self.get_all_clients(username)
            return [Client(**client_doc) for client_doc in client_docs]
        client_doc = self.collection.find_one({'id': id, 'created_by': username})
        return Client(**client_doc) if client_doc else None

    def create_client(self, client: Client) -> dict:
        """
        Create a client in the database
        """
        existing_client = self.get_client_by_billing_number(client.billing_number, client.created_by)
        if existing_client:
            if self.fail_silent:
                return self.insert_one_result(client.name)
            raise Exception(f"Client {client.billing_number} already exists")
        return self.collection.insert_one(client.dict())

    def update_client(self, client: Client, username: str) -> dict:
        """
        Update a client in the database
        """
        return self.collection.update_one(
            {'id': client.id, 'created_by': username},
            {'$set': {
                'name': client.name,
                'billing_number': client.billing_number,
                'enabled': client.enabled,
                }
            }
        )

    def delete_client(self, id: str, username: str) -> dict:
        """
        Delete a client from the database
        """
        return self.collection.delete_one({'id': id, 'created_by': username})

    def get_all_clients(self, username: str) -> list:
        """
        Get all clients from the database
        """
        return list(self.collection.find({'created_by': username}))

    def get_client_by_billing_number(self, billing_number: str, username: str) -> Client:
        """
        Get a client from the database by billing_number
        """
        client_doc = self.collection.find_one({'billing_number': billing_number, 'created_by': username})
        return Client(**client_doc) if client_doc else None
