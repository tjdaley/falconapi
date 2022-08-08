"""
trackers_table.py - Trackers Table
"""
from database.db import Database
from typing import List, Optional
from models.tracker import Tracker
from models.document import Document
from database.documents_table import DocumentsDict

DATABASE = 'falcon'
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
        print(f"Getting tracker {key} of type {type(key)}")
        return self.trackers.get_tracker(key)

    def __setitem__(self, key, value):
        print(f"Setting {key} to {value}")
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
        return f"{DATABASE}.{COLLECTION}"

    def __str__(self):
        return f"{DATABASE}.{COLLECTION}"

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
        self.collection = self.conn[DATABASE][COLLECTION]

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
        return self.collection.update_one(
            {'id': tracker.id},
            {'$set': {
                'name': tracker.name,
                'username': tracker.username,
                'client_reference': tracker.client_reference,
                'documents': tracker.documents
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
        tracker_docs = self.collection.find({'username': username})
        return [Tracker(**tracker_doc) for tracker_doc in tracker_docs]

    # See if a document is in a tracker
    def is_in_tracker(self, tracker_id: str, document_id: str) -> bool:
        """
        Check if a document is in a tracker
        """
        tracker = self.get_tracker_by_id(tracker_id)
        return document_id in tracker.documents if tracker else False

    def link_doc(self, tracker: Tracker, document: Document) -> bool:
        """
        Link a document to a tracker
        """
        tracker = self.get_tracker_by_id(tracker.id)
        if document.id in tracker.documents:
            if self.fail_silent:
                return self.update_one_result()
            raise Exception(f"Document {document.id} is already in tracker {tracker.id}")
        tracker.documents.append(document.id)
        return self.update_tracker(tracker)

    def unlink_doc(self, tracker: Tracker, document_id: str) -> bool:
        """
        Unlink a document from a tracker
        """
        tracker = self.get_tracker_by_id(tracker.id)
        if document_id not in tracker.documents:
            if self.fail_silent:
                return self.update_one_result()
            raise Exception(f"Document {document_id} is not in tracker {tracker.id}")
        tracker.documents.remove(document_id)
        return self.update_tracker(tracker)
    
    def get_count(self) -> int:
        """
        Get the number of trackers in the database
        """
        return self.collection.count_documents({})