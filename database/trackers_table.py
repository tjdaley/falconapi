"""
trackers_table.py - Trackers Table
"""
from collections import defaultdict
import calendar
from typing import List

from database.db import Database
from models.tracker import Tracker
from models.document import Document
from database.documents_table import DocumentsDict
from models.tracker import TrackerDatasetResponse
from doc_classifier.openai_prompt_data import PromptData

COLLECTION = 'trackers'

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

    def get_tracker(self, id: str) -> Tracker:
        """
        Get a tracker from the database
        """
        tracker_doc = self.collection.find_one({'id': id})
        return Tracker(**tracker_doc) if tracker_doc else None

    def get_tracker_by_id(self, id: str) -> Tracker:
        """
        Get a tracker from the database
        """
        tracker_doc = self.collection.find_one({'id': id})
        return Tracker(**tracker_doc) if tracker_doc else None

    def create_tracker(self, tracker: Tracker) -> dict:
        """
        Create a tracker in the database
        """
        existing_tracker = self.get_tracker_by_id(tracker.id)
        if existing_tracker:
            if self.fail_silent:
                return self.insert_one_result(tracker.id)
            raise Exception(f"Tracker {tracker.id} already exists")
        print(f"Creating tracker {tracker.id}")
        return self.collection.insert_one(tracker.dict())

    def update_tracker(self, tracker: Tracker) -> dict:
        """
        Update a tracker in the database
        """

        # Update the tracker in the database
        if 'documents' in tracker.dict():
            return self.collection.update_one(
                {'id': tracker.id},
                {'$set': {
                    'name': tracker.name,
                    'client_reference': tracker.client_reference,
                    'documents': tracker.documents,
                    'added_username': tracker.added_username,
                    'added_date': tracker.added_date,
                    'updated_username': tracker.updated_username,
                    'updated_date': tracker.updated_date,
                    'auth_usernames': tracker.auth_usernames,
                    }
                }
            )

        # If a client app invokes the update path, the Tracker object will not have the documents field.
        return self.collection.update_one(
            {'id': tracker.id},
            {'$set': {
                'name': tracker.name,
                'client_reference': tracker.client_reference,
                'added_username': tracker.added_username,
                'added_date': tracker.added_date,
                'updated_username': tracker.updated_username,
                'updated_date': tracker.updated_date,
                'auth_usernames': tracker.auth_usernames,
                }
            }
        )

    def delete_tracker(self, id: str) -> dict:
        """
        Delete a tracker from the database
        """
        return self.collection.delete_one({'id': id})

    def get_all_trackers(self) -> list:
        """
        Get all trackers from the database
        """
        return list(self.collection.find())

    def get_trackers_by_username(self, username: str) -> List[Tracker]:
        """
        Get all trackers for a username
        """
        tracker_docs = self.collection.find({'auth_usernames': username})
        return [Tracker(**tracker_doc) for tracker_doc in tracker_docs]

    # See if a document is in a tracker
    def is_in_tracker(self, tracker_id: str, document_id: str) -> bool:
        """
        Check if a document is in a tracker
        """
        tracker = self.get_tracker_by_id(tracker_id)
        return document_id in tracker.documents if tracker else False
    
    def get_trackers_linked_to_doc(self, doc_id: str) -> list:
        """
        Get all trackers linked to a document
        """
        return list(self.collection.find({'documents': doc_id}))
    
    def delete_document_from_trackers(self, doc_id: str) -> None:
        """
        Delete a document from all trackers
        """
        trackers = self.get_trackers_linked_to_doc(doc_id)

        for tracker in trackers:
            self.unlink_doc(Tracker(**tracker), doc_id)
        
        return {'trackers': len(trackers)}

    def link_doc(self, tracker: Tracker, document: Document) -> bool:
        """
        Link a document to a tracker
        """
        existing_tracker = self.get_tracker_by_id(tracker.id)
        if document.id in existing_tracker.documents:
            if self.fail_silent:
                return self.update_one_result()
            raise Exception(f"Document {document.id} is already in tracker {tracker.id}")
        existing_tracker.documents.append(document.id)
        return self.update_tracker(existing_tracker)

    def unlink_doc(self, tracker: Tracker, document_id: str) -> bool:
        """
        Unlink a document from a tracker
        """
        existing_tracker = self.get_tracker_by_id(tracker.id)
        if document_id not in existing_tracker.documents:
            if self.fail_silent:
                return self.update_one_result()
            raise Exception(f"Document {document_id} is not in tracker {tracker.id}")
        existing_tracker.documents.remove(document_id)
        return self.update_tracker(existing_tracker)
    
    def get_count(self) -> int:
        """
        Get the number of trackers in the database
        """
        return self.collection.count_documents({})
    
    def get_compliance_matrix(self, tracker: Tracker, classification: str) -> dict:
        """
        Get a compliance matrix for a tracker
        """
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
            subclass = {
                "key_fields": prompt_data.compliance_key_fields(classification),
                "doc_ids": []
            }
            
            for doc in cursor:
                date = doc.get('document_date', '')
                subclass = doc.get('sub_classification', {})
                year, month, _ = map(int, date.split('-'))
                month_name = calendar.month_name[month]
                
                # key = f"{fi} - {acc}"
                key = prompt_data.make_compliance_key(classification, subclass)
                if key:
                    subclass["doc_ids"].append(doc['id'])
                    data[key][year][month_name] = {
                        'bates': doc.get('beginning_bates', "X"),
                        'path': doc.get('path', ""),
                        'id': doc.get('id', ""),
                        'date': doc.get('produced_date', ""),
                    }
            
            # Convert defaultdict to regular dict for Jinja compatibility
            data[key][0] = subclass
            final_data = {k: dict(v) for k, v in data.items()}
            if final_data:
                class_matrix[classification] = final_data
        return class_matrix

    def get_dataset(self, tracker: Tracker, dataset_name: str) -> TrackerDatasetResponse:
        """
        Get a dataset from a tracker
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

        if dataset_name not in dataset_methods:
            return {}  # Error has already been raised...this is just a belt with the suspenders.
        
        dataset: list = list(dataset_methods[dataset_name](tracker))
        return TrackerDatasetResponse(id=tracker.id, dataset_name=dataset_name, data=dataset)
    
    def get_documents_for_tracker(self, tracker: Tracker) -> list[dict]:
        """
        Get TRACKER_LIST dataset from a tracker
        """
        docs = list(self.documents.find({'id':{'$in': tracker.documents}}, {'_id': 0}))
        return docs
    
    def get_deposits(self, tracker: Tracker) -> list[dict]:
        """
        Get DEPOSITS dataset from a tracker
        """
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
    
    def get_cash_back_purchases(self, tracker: Tracker) -> list[dict]:
        """
        Get CASH_BACK_PURCHASES dataset from a tracker
        """
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
    
    def get_transfers(self, tracker: Tracker) -> list[dict]:
        """
        Get TRANSFERS dataset from a tracker
        """
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

    def get_filtered_transactions(self, initial_element_match, unwound_element_match) -> list[dict]:
        """
        Get TRANSFERS dataset from a tracker
        """

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
