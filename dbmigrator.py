"""
dbmigrator.py - Database Migrator
"""
import os
from uuid import uuid4
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

load_dotenv()

MONGO_URI = os.getenv('DB_URL')
DATABASE = 'falcon'
client = MongoClient(MONGO_URI)
client_collection = client[DATABASE]['clients']
trackers_collection = client[DATABASE]['trackers']

def create_clients():
    """
    Create a clients document for each unique client_reference in the trackers collection
    """
    client_template = {
        'id': '',
        'name': '',
        'billing_number': '',
        'created_by': 'test_user@test.com',
        'authorized_users': ['test_user@test.com',  'mdaley@koonsfuller.com', 'tdaley@koonsfuller.com'],
        'enabled': True,
        'version': '',
    }
    client_refs = trackers_collection.distinct('client_reference')
    for client_ref in client_refs:
        client_template['id'] = str(uuid4())
        client_template['name'] = client_ref
        client_template['billing_number'] = client_ref
        client_template['version'] = str(uuid4())
        try:
            result = client_collection.insert_one(client_template)
            del client_template['_id']
            print(f'Inserted client {client_ref} with id {result.inserted_id}')
        except DuplicateKeyError as e:
            print(f'Duplicate key error for client {client_ref}: {e}')
            print(f'Conflicting key: {e.details}')
            continue
        except Exception as e:
            print(f'Error inserting client {client_ref}: {e}')
            print(f'Client template: {client_template}')
            continue
        result = trackers_collection.update_many(
            {'client_reference': client_ref},
            {'$set': {'client_id': client_template['id']}}
        )
        print(f'Updated {result.modified_count} trackers with client_id {client_template["id"]}')

def remove_unused_clients():
    """
    Remove clients that are not referenced in the trackers collection
    """
    client_refs = trackers_collection.distinct('client_id')
    result = client_collection.delete_many({'id': {'$nin': client_refs}})
    print(f'Removed {result.deleted_count} clients not referenced in trackers')

if __name__ == '__main__':
    create_clients()
    remove_unused_clients()
