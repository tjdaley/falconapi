"""
trackers_table.py - Trackers Table
"""
from collections import defaultdict
import calendar
from datetime import datetime
from typing import List
from uuid import uuid4

from database.db import Database
from models.tracker import Tracker
from models.document import Document
from database.documents_table import DocumentsDict
from models.tracker import TrackerDatasetResponse
from database.clients_table import ClientsTable
from doc_classifier.openai_prompt_data import PromptData

COLLECTION = 'trackers'
CLIENTS_DB = ClientsTable()

class TrackersDict(dict):
    """
    Dictionary of trackers

    This is a dictionary of trackers. It acts like a dictionary that is backed up by a database.
    The one problem is that in a regular dictionary, you would be able to update a value
    just by refering to it in the dictionary like this:

        d = DocumentsDict()
        d['doc1'] = Document(**{'id': 'doc1', 'name': 'Document 1'})
        d['doc1'].name = 'Document 1 Updated'  # THIS CHANGE IS NOT PERSISTED!!

    This is not possible in a dictionary backed up by a database because updating a value does not
    trigger an update to the *dict* class which would then update the database.

    Instead, you must update the value in the database directly.

        d = DocumentsDict()
        d['doc1'] = Document(**{'id': 'doc1', 'name': 'Document 1'})
        doc = d['doc1']
        doc.name = 'Document 1 Updated'
        d['doc1'] = doc  # This triggers an update to the database
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.__dict__ = {}
        self.trackers = TrackersTable()
        self.documents = DocumentsDict()
        self.collection = self.trackers.collection

    def __getitem__(self, key):
        return self.trackers.get_tracker(key)

    def __setitem__(self, key, value):
        tracker = self.trackers.get_tracker(key)
        if tracker:
            self.trackers.update_tracker(value)
        else:
            self.trackers.create_tracker(value)

    def __delitem__(self, key):
        self.trackers.delete_tracker(key)

    def __contains__(self, key):
        return self.trackers.get_tracker(key) is not None

    def __iter__(self):
        return iter([tracker['id'] for tracker in self.trackers.get_all_trackers()])

    def __len__(self):
        return self.trackers.get_count()

    def __repr__(self):
        return f"{Database.database}.{COLLECTION}"

    def __str__(self):
        return f"{Database.database}.{COLLECTION}"

    def keys(self):
        trackers = self.trackers.get_all_trackers()
        return [tracker['id'] for tracker in trackers]
    
    def values(self):
        return self.trackers.get_all_trackers()

    def items(self):
        trackers = self.trackers.get_all_trackers()
        return [(tracker['id'], tracker) for tracker in trackers]
    
    def get(self, key, default=None):
        return self.trackers.get_tracker(key) or default

    def link_doc(self, tracker: Tracker, document: Document) -> bool:
        """
        Link a document to a tracker
        """
        return self.trackers.link_doc(tracker, document)
    
    def unlink_doc(self, tracker: Tracker, document_id: str) -> bool:
        """
        Unlink a document from a tracker
        """
        return self.trackers.unlink_doc(tracker, document_id)
    
    def is_linked(self, tracker: Tracker, document: Document) -> bool:
        """
        Check if a document is linked to a tracker
        """
        return self.trackers.is_in_tracker(tracker.id, document.id)

    def get_for_username(self, username: str) -> List[Tracker]:
        """
        Get all trackers for a username
        """
        return self.trackers.get_trackers_by_username(username)

class DuplicateTrackerError(Exception):
    """
    Exception for when a tracker already exists
    """
    def __init__(self, tracker_id: str):
        self.message = f"Tracker {tracker_id} already exists"
        super().__init__(self.message)

class UnauthorizedUserError(Exception):
    """
    Exception for when a user is not authorized to create a tracker
    """
    def __init__(self, username: str, client_reference: str):
        self.message = f"User {username} is not authorized to create trackers for client {client_reference}"
        super().__init__(self.message)
    
class TrackersTable(Database):
    """
    Class for interacting with the trackers table
    """
    def __init__(self) -> None:
        """
        Initialize the trackers table.
        """
        super().__init__()
        self.collection = self.conn[self.database][COLLECTION]
        self.documents = self.conn[self.database]['documents']

    def get(self, tracker_id: str, username: str) -> Tracker:
        """
        Get a tracker from the database

        Args:
            tracker_id (str): The tracker's ID.
            username (str): The user's username.

        Returns:
            Tracker: The Tracker object if it exists, None otherwise.

        Raises:
            UnauthorizedUserError: If the user is not authorized to access the tracker.
        """
        tracker_doc = self.collection.find_one({'id': tracker_id})
        tracker = Tracker(**tracker_doc) if tracker_doc else None
        if not tracker:
            return None

        # See if this user is authorized to create trackers for this client.
        # If not, raise an exception.
        if not CLIENTS_DB.is_authorized(tracker.client_id, username):
            raise UnauthorizedUserError(username, tracker.client_id)

        return tracker

    def create(self, tracker: Tracker, username: str) -> dict:
        """
        Create a tracker in the database

        Args:
            tracker (Tracker): The tracker object to create.
            username (str): The user's username.

        Returns:
            dict: The result of the insert operation.

        Raises:
            UnauthorizedUserError: If the user is not authorized to create a tracker.
        """
        # See if this user is authorized to create trackers for this client.
        # If not, raise an exception.
        if not CLIENTS_DB.is_authorized(tracker.client_id, username):
            raise UnauthorizedUserError(username, tracker.client_id)

        existing_tracker = self.get_tracker_by_id(tracker.id)
        if existing_tracker:
            if self.fail_silent:
                return self.insert_one_result(tracker.id)
            raise DuplicateTrackerError(tracker.id)
        
        return self.collection.insert_one(tracker.model_dump())

    def update(self, tracker: Tracker, username: str) -> dict:
        """
        Update a tracker in the database

        Args:
            tracker (Tracker): The tracker object to update.
            username (str): The user's username.

        Returns:
            dict: The result of the update operation.

        Raises:
            UnauthorizedUserError: If the user is not authorized to update the tracker.
        """
        # See if this user is authorized to update this tracker.
        if not CLIENTS_DB.is_authorized(tracker.client_id, username):
            raise UnauthorizedUserError(username, tracker.client_id)

        # Update the tracker in the database
        if 'documents' in tracker.model_dump():
            return self.collection.update_one(
                {'id': tracker.id},
                {'$set': {
                    'name': tracker.name,
                    'bates_pattern': tracker.bates_pattern,
                    'documents': tracker.documents,
                    'updated_username': username,
                    'updated_date': datetime.now(),
                    'version': str(uuid4())
                    }
                }
            )

        # If a client app invokes the update path, the Tracker object may not have the documents field.
        return self.collection.update_one(
            {'id': tracker.id},
            {'$set': {
                'name': tracker.name,
                'bates_pattern': tracker.bates_pattern,
                'updated_username': username,
                'updated_date': datetime.now(),
                'version': str(uuid4())
                }
            }
        )

    def delete(self, tracker_id: str, username: str) -> dict:
        """
        Delete a tracker from the database

        Args:
            tracker_id (str): The tracker's ID.
            username (str): The user's username.

        Returns:
            dict: The result of the delete operation.

        Raises:
            UnauthorizedUserError: If the user is not authorized to delete the tracker.
        """
        tracker: Tracker = self.get_tracker(tracker_id, username)
        if not tracker:
            return {'deleted_count': 0}
        # See if this user is authorized to update this tracker.
        if not CLIENTS_DB.is_authorized(tracker.client_id, username):
            raise UnauthorizedUserError(username, tracker.client_id)
        
        if tracker.added_username != username:
            raise UnauthorizedUserError(username, tracker.client_id)

        return self.collection.delete_one({'id': tracker_id})

    def get_all_trackers(self) -> list:
        """
        Get all trackers from the database

        Returns:
            list: A list of all trackers in the database.
        """
        return list(self.collection.find())

    def get_trackers_by_username(self, username: str) -> List[Tracker]:
        """
        Get all trackers for a username

        Args:
            username (str): The user's username.

        Returns:
            List[Tracker]: A list of all trackers for the user.
        """
        clients = CLIENTS_DB.get_clients(client_id='*', username=username)
        all_trackers = []
        for client in clients:
            trackers = self.collection.find({'client_id': client.id})
            all_trackers.extend([Tracker(**tracker) for tracker in trackers])
        return all_trackers
    
    def get_trackers_by_client_id(self, client_id: str, username: str) -> List[Tracker]:
        """
        Get all trackers for a client ID

        Args:
            client_id (str): The client's ID.
            username (str): The user's username.

        Returns:
            List[Tracker]: A list of all trackers for the client.

        Raises:
            UnauthorizedUserError: If the user is not authorized to access the trackers.
        """
        # See if this user is authorized to update this tracker.
        if not CLIENTS_DB.is_authorized(client_id, username):
            raise UnauthorizedUserError(username, client_id)
        trackers = self.collection.find({'client_id': client_id})
        return [Tracker(**tracker) for tracker in trackers]

    # See if a document is in a tracker
    def is_in_tracker(self, tracker_id: str, document_id: str) -> bool:
        """
        Check if a document is in a tracker

        Args:
            tracker_id (str): The tracker's ID.
            document_id (str): The document's ID.

        Returns:
            bool: True if the document is in the tracker, False otherwise.
        """
        tracker = self.get_tracker_by_id(tracker_id)
        return document_id in tracker.documents if tracker else False
    
    def get_trackers_linked_to_doc(self, doc_id: str) -> list:
        """
        Get all trackers linked to a document

        Args:
            doc_id (str): The document's ID.

        Returns:
            list: A list of all trackers linked to the document.
        """
        return list(self.collection.find({'documents': doc_id}))
    
    def delete_document_from_trackers(self, doc_id: str) -> None:
        """
        Delete a document from all trackers

        Args:
            doc_id (str): The document's ID.

        Returns:
            dict: The result of the delete operation.
        """
        trackers = self.get_trackers_linked_to_doc(doc_id)

        for tracker in trackers:
            self.unlink_doc(Tracker(**tracker), doc_id)
        
        return {'trackers': len(trackers)}

    def link_doc(self, tracker: Tracker, document: Document, username: str) -> bool:
        """
        Link a document to a tracker

        Args:
            tracker (Tracker): The tracker object.
            document (Document): The document object.
            username (str): The user's username.

        Returns:
            bool: True if the document was linked to the tracker, False otherwise.

        Raises:
            UnauthorizedUserError: If the user is not authorized to update the tracker.
        """
        existing_tracker: Tracker = self.get_tracker(tracker.id, username)
        if not existing_tracker:
            return False
        # See if this user is authorized to update this tracker.
        if not CLIENTS_DB.is_authorized(existing_tracker.client_id, username):
            raise UnauthorizedUserError(username, existing_tracker.client_id)

        if document.id in existing_tracker.documents:
            if self.fail_silent:
                return True
            raise Exception(f"Document {document.id} is already in tracker {tracker.id}")
        existing_tracker.documents.append(document.id)
        try:
            self.update_tracker(existing_tracker, username)
        except Exception as e:
            return False
        return True

    def unlink_doc(self, tracker: Tracker, document_id: str, username: str) -> bool:
        """
        Unlink a document from a tracker

        Args:
            tracker (Tracker): The tracker object.
            document_id (str): The document's ID.
            username (str): The user's username.

        Returns:
            bool: True if the document was unlinked from the tracker, False otherwise.

        Raises:
            UnauthorizedUserError: If the user is not authorized to update the tracker.        
        """
        existing_tracker: Tracker = self.get_tracker(tracker.id, username)
        if not existing_tracker:
            return False
        # See if this user is authorized to update this tracker.
        if not CLIENTS_DB.is_authorized(existing_tracker.client_id, username):
            raise UnauthorizedUserError(username, existing_tracker.client_id)
        if document_id not in existing_tracker.documents:
            if self.fail_silent:
                return True
            raise Exception(f"Document {document_id} is not in tracker {tracker.id}")
        existing_tracker.documents.remove(document_id)
        try:
            self.update_tracker(existing_tracker, username)
        except Exception as e:
            return False
        return True
    
    def get_compliance_matrix(self, tracker: Tracker, classification: str, username: str) -> dict:
        """
        Get a compliance matrix for a tracker

        Args:
            tracker (Tracker): The tracker object.
            classification (str): The classification to get the matrix for.
            username (str): The user's username.

        Returns:
            dict: The compliance matrix for the tracker.

        Raises:
            UnauthorizedUserError: If the user is not authorized to access the tracker.
        """
        # See if this user is authorized to update this tracker.
        if not CLIENTS_DB.is_authorized(tracker.client_id, username):
            raise UnauthorizedUserError(username, tracker.client_id)

        prompt_data = PromptData()
        classifications = prompt_data.compliance_classifications()
        class_matrix = {}
        sorted_classifications = sorted(classifications)

        for classification in sorted_classifications:
            # Fetch and organize documents
            selection = {
                'id': {'$in': tracker.documents},
                'classification': classification,
                'sub_classification': {
                    '$exists': True,
                    '$ne': '',  # Ensure it's not an empty string
                    '$ne': {},  # Ensure it's not an empty dictionary
                    '$ne': [],  # Ensure it's not an empty array if applicable
                    '$ne': None # Ensure it's not None
                }
            }

            projection = {
                'id': 1,
                'sub_classification': 1,
                'document_date': 1,
                'produced_date': 1,
                'beginning_bates': 1,
                'path': 1
            }
            cursor = self.documents.find(selection, projection).sort('document_date', 1)
            data = defaultdict(lambda: defaultdict(lambda: {calendar.month_name[m]: None for m in range(1, 13)}))
            metadata = {
                "key_fields": prompt_data.compliance_key_fields(classification),
                "doc_ids": []
            }
            
            for doc in cursor:
                date = doc.get('document_date', '')
                subclass = doc.get('sub_classification', {})
                try:
                    year, month, _ = map(int, date.split('-'))
                except ValueError:
                    continue  # skip document with invalid date string
                month_name = calendar.month_name[month]
                
                # key = f"{fi} - {acc}"
                key = prompt_data.make_compliance_key(classification, subclass)
                if key:
                    data[key][year][month_name] = {
                        'bates': doc.get('beginning_bates', "X"),
                        'path': doc.get('path', ""),
                        'id': doc.get('id', ""),
                        'date': doc.get('produced_date', ""),
                    }
                    if 'metadata' not in data[key]:
                        data[key]['metadata'] = {
                            "key_fields": prompt_data.compliance_key_fields(classification),
                            "doc_ids": []
                        }
                    data[key]['metadata']['doc_ids'].append(doc['id'])
            
            # Convert defaultdict to regular dict for Jinja compatibility
            final_data = {k: dict(v) for k, v in data.items()}
            if final_data:
                class_matrix[classification] = final_data
        return class_matrix

    def get_dataset(self, tracker: Tracker, dataset_name: str, username: str) -> TrackerDatasetResponse:
        """
        Get a dataset from a tracker

        Args:
            tracker (Tracker): The tracker object.
            dataset_name (str): The name of the dataset to get.
            username (str): The user's username.

        Returns:
            TrackerDatasetResponse: The dataset response object.

        Raises:
            UnauthorizedUserError: If the user is not authorized to access the tracker.
        """
        dataset_methods = {
            'TRANSFERS': self.get_transfers,
            'CASH_BACK_PURCHASES': self.get_cash_back_purchases,
            'DEPOSITS': self.get_deposits,
            'TRACKER_LIST': self.get_documents_for_tracker,
            #'CHECKS': self.get_checks,
            #'WIRE_TRANSFERS': self.get_wire_transfers,
            #'UNIQUE_ACCOUNTS': self.get_unique_accounts,
            #'MISSING_STATEMENTS': self.get_missing_statements,
            #'MISSING_PAGES': self.get_missing_pages
        }

        existing_tracker: Tracker = self.get_tracker(tracker.id, username)
        if not existing_tracker:
            return TrackerDatasetResponse(id=tracker.id, dataset_name=dataset_name, data=[])
        if not CLIENTS_DB.is_authorized(existing_tracker.client_id, username):
            raise UnauthorizedUserError(username, tracker.client_id)

        if dataset_name not in dataset_methods:
            return TrackerDatasetResponse(id=tracker.id, dataset_name=dataset_name, data=[])
        
        dataset: list = list(dataset_methods[dataset_name](tracker))
        return TrackerDatasetResponse(id=tracker.id, dataset_name=dataset_name, data=dataset)
    
    def get_documents_for_tracker(self, tracker: Tracker, username: str) -> list[dict]:
        """
        Get TRACKER_LIST dataset from a tracker

        Args:
            tracker (Tracker): The tracker object.
            username (str): The user's username.

        Returns:
            list[dict]: A list of documents for the tracker.

        Raises:
            UnauthorizedUserError: If the user is not authorized to access the tracker.
        """
        existing_tracker: Tracker = self.get_tracker(tracker.id, username)
        if not existing_tracker:
            return []
        if not CLIENTS_DB.is_authorized(existing_tracker.client_id, username):
            raise UnauthorizedUserError(username, tracker.client_id)
        docs = list(self.documents.find({'id':{'$in': tracker.documents}}, {'_id': 0}))
        return docs
    
    def get_deposits(self, tracker: Tracker, username: str) -> list[dict]:
        """
        Get DEPOSITS dataset from a tracker

        Args:
            tracker (Tracker): The tracker object.
            username (str): The user's username.

        Returns:
            list[dict]: A list of deposits for the tracker.

        Raises:
            UnauthorizedUserError: If the user is not authorized to access the tracker.
        """
        existing_tracker: Tracker = self.get_tracker(tracker.id, username)
        if not existing_tracker:
            return []
        if not CLIENTS_DB.is_authorized(existing_tracker.client_id, username):
            raise UnauthorizedUserError(username, tracker.client_id)

        initial_element_match = {
            "$match": {
                "id": {"$in": tracker.documents},
                "tables.transactions": {
                    "$elemMatch": {
                        "$and": [
                            {"Category": {"$eq": "Deposit"}},
                            {"Category": {"$exists": True}}
                        ]
                    }
                }
            }
        }

        unwound_element_match = {
            "$match": {
                "$and": [
                    {"tables.transactions.Category": {"$eq": "Deposit"}},
                    {"tables.transactions.Category": {"$exists": True}}
                ]
            }
        }

        return self.get_filtered_transactions(initial_element_match, unwound_element_match)
    
    def get_cash_back_purchases(self, tracker: Tracker, username: str) -> list[dict]:
        """
        Get CASH_BACK_PURCHASES dataset from a tracker

        Args:
            tracker (Tracker): The tracker object.
            username (str): The user's username.

        Returns:
            list[dict]: A list of cash back purchases for the tracker.

        Raises:
            UnauthorizedUserError: If the user is not authorized to access the tracker.
        """
        existing_tracker: Tracker = self.get_tracker(tracker.id, username)
        if not existing_tracker:
            return []
        if not CLIENTS_DB.is_authorized(existing_tracker.client_id, username):
            raise UnauthorizedUserError(username, tracker.client_id)

        initial_element_match = {
            "$match": {
                "id": {"$in": tracker.documents},
                "tables.transactions": {
                    "$elemMatch": {
                        "$and": [
                            {"Cash Back": {"$ne": ""}},
                            {"Cash Back": {"$exists": True}}
                        ]
                    }
                }
            }
        }

        unwound_element_match = {
            "$match": {
                "$and": [
                    {"tables.transactions.Cash Back": {"$ne": ""}},
                    {"tables.transactions.Cash Back": {"$exists": True}}
                ]
            }
        }

        return self.get_filtered_transactions(initial_element_match, unwound_element_match)
    
    def get_transfers(self, tracker: Tracker, username: str) -> list[dict]:
        """
        Get TRANSFERS dataset from a tracker

        Args:
            tracker (Tracker): The tracker object.
            username (str): The user's username.

        Returns:
            list[dict]: A list of transfers for the tracker.

        Raises:
            UnauthorizedUserError: If the user is not authorized to access the tracker.
        """
        existing_tracker: Tracker = self.get_tracker(tracker.id, username)
        if not existing_tracker:
            return []
        if not CLIENTS_DB.is_authorized(existing_tracker.client_id, username):
            raise UnauthorizedUserError(username, tracker.client_id)

        initial_element_match = {
            "$match": {
                "id": {"$in": tracker.documents},
                "tables.transactions": {
                    "$elemMatch": {
                        "$or": [
                            {"Transfer from": {"$ne": ""}},
                            {"Transfer to": {"$ne": ""}}
                        ],
                        "$and": [
                            {"Transfer from": {"$exists": True}},  # Ensure "Transfer from" exists
                            {"Transfer to": {"$exists": True}}  # Ensure "Transfer to" exists
                        ]
                    }
                }
            }
        }

        unwound_element_match = {
            "$match": {
                "$or": [
                    {"tables.transactions.Transfer from": {"$ne": ""}},
                    {"tables.transactions.Transfer to": {"$ne": ""}}
                ],
                "$and": [
                    {"tables.transactions.Transfer from": {"$exists": True}},
                    {"tables.transactions.Transfer to": {"$exists": True}}
                ]
            }
        }

        return self.get_filtered_transactions(initial_element_match, unwound_element_match)

    def get_filtered_transactions(self, initial_element_match: dict, unwound_element_match: dict, tracker_id: str, username: str) -> list[dict]:
        """
        Get TRANSFERS dataset from a tracker

        Args:
            initial_element_match (dict): The initial match for the aggregation pipeline.
            unwound_element_match (dict): The unwound match for the aggregation pipeline.
            tracker_id (str): The tracker's ID.
            username (str): The user's username.

        Returns:
            list[dict]: A list of transfers for the tracker.

        Raises:
            UnauthorizedUserError: If the user is not authorized to access the tracker.
        """
        existing_tracker: Tracker = self.get_tracker(tracker_id, username)
        if not existing_tracker:
            return []
        if not CLIENTS_DB.is_authorized(existing_tracker.client_id, username):
            raise UnauthorizedUserError(username, existing_tracker.client_id)

        extendedprops_collection = self.conn[self.database]['extendedprops']

        # MongoDB Aggregation Pipeline
        pipeline = [
            initial_element_match,
            {
                "$unwind": "$tables.transactions"
            },
            unwound_element_match,
            {
                "$lookup": {
                    "from": "documents",  # Specify the collection to join.
                    "localField": "id",   # Field from the input documents.
                    "foreignField": "id",  # Field from the documents of the "documents" collection.
                    "as": "document_details"  # Output array field with the joined documents.
                }
            },
            {
                "$unwind": "$document_details"  # Unwind the results of the lookup to merge document details
            },
            {
                "$project": {
                    "_id": 0,
                    "id": 1,
                    "transaction": "$tables.transactions",
                    "beginning_bates": "$document_details.beginning_bates",
                    "ending_bates": "$document_details.ending_bates",
                    "classification": "$document_details.classification",
                    "title": "$document_details.title",
                    "path": "$document_details.path",
                    "document_date": "$document_details.document_date"
                }
            }
        ]

        # Execute the aggregation pipeline
        transactions_with_transfer = extendedprops_collection.aggregate(pipeline)
        return transactions_with_transfer
