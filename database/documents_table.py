"""
documents_table.py - Documents Table
"""
from typing import List
from database.db import Database
from models.document import Document
from models.tracker import Tracker

DATABASE = 'falcon'
COLLECTION = 'documents'

class DocumentsDict(dict):
    """
    Dictionary of documents
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.documents = DocumentsTable()

    def __getitem__(self, key):
        print(f"Getting document {key} of type {type(key)}")
        return self.documents.get_document(key)

    def __setitem__(self, key, value):
        doc = self.documents.get_document(key)
        if doc:
            self.documents.update_document(value)
        else:
            self.documents.create_document(value)

    def __delitem__(self, key):
        self.documents.delete_document(key)

    def __contains__(self, key):
        return self.documents.get_document(key) is not None

    def __iter__(self):
        return iter([doc['id'] for doc in self.documents.get_all_documents()])

    def __len__(self):
        return self.documents.get_count()

    def __repr__(self):
        return f"{DATABASE}.{COLLECTION}"

    def __str__(self):
        return f"{DATABASE}.{COLLECTION}"

    def keys(self):
        docs = self.documents.get_all_documents()
        return [doc['id'] for doc in docs]
    
    def values(self):
        return self.documents.get_all_documents()

    def items(self):
        docs = self.documents.get_all_documents()
        return [(doc['id'], doc) for doc in docs]
    
    def get(self, key, default=None):
        return self.documents.get_document(key) or default
    
    def get_by_path(self, path: str) -> Document:
        """
        Get document by path
        """
        return self.documents.get_document_by_path(path)

    def get_for_tracker(self, tracker: Tracker) -> List[Document]:
        """
        Get all documents for a tracker
        """
        return self.documents.get_documents_for_tracker(tracker)
    
class DocumentsTable(Database):
    """
    Class for interacting with the documents table
    """
    def __init__(self) -> None:
        """
        Initialize the documents table.
        """
        super().__init__()
        self.collection = self.conn[DATABASE][COLLECTION]

    def get_document(self, id: str) -> Document:
        """
        Get a document from the database
        """
        document_doc = self.collection.find_one({'id': id})
        return Document(**document_doc) if document_doc else None

    def create_document(self, document: Document) -> dict:
        """
        Create a document in the database
        """
        existing_document = self.get_document_by_id(document.id)
        if existing_document:
            if self.fail_silent:
                return self.insert_one_result(document.id)
            raise Exception(f"Document {document.id} already exists")
        return self.collection.insert_one(document.dict())

    def update_document(self, document: Document) -> dict:
        """
        Update a document in the database

        Every field in the document will be updated.

        Args:
            document (Document): The document to update
        """
        return self.collection.update_one(
            {'id': document.id},
            {'$set': {
                'path': document.path,
                'filename': document.filename,
                'type': document.type,
                'title': document.title,
                'create_date': document.create_date,
                'document_date': document.document_date,
                'beginning_bates': document.beginning_bates,
                'ending_bates': document.ending_bates,
                'page_count': document.page_count,
                'bates_pattern': document.bates_pattern,
                'added_username': document.added_username
                }
            }
        )

    def delete_document(self, id: str) -> dict:
        """
        Delete a document from the database

        Args:
            id: The id of the document to delete

        TODO: Delete the document from the filesystem
        TODO: Delete the document from all trackers
        """
        return self.collection.delete_one({'id': id})

    def get_all_documents(self) -> list:
        """
        Get all documents from the database
        """
        return list(self.collection.find())

    def get_document_by_id(self, id: str) -> Document:
        """
        Get a document from the database
        """
        return self.collection.find_one({'id': id})

    def get_document_by_path(self, path: str) -> Document:
        """
        Get a document from the database
        """
        return self.collection.find_one({'path': path})

    def get_documents_for_tracker(self, tracker: Tracker) -> List[Document]:
        """
        Get all documents for a tracker
        """
        docs = []
        for doc_id in tracker.documents:
            docs.append(self.get_document(doc_id))
        return docs

    def get_count(self) -> int:
        """
        Get the number of documents in the database
        """
        return self.collection.count_documents({})
