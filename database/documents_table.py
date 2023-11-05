"""
documents_table.py - Documents Table
"""
from typing import List
from database.db import Database
from models.document import Document
from models.tracker import Tracker

COLLECTION = 'documents'

class DocumentsDict(dict):
    """
    Dictionary of documents
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.documents = DocumentsTable()

    def __getitem__(self, key):
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
        return f"{Database.database}.{COLLECTION}"

    def __str__(self):
        return f"{Database.database}.{COLLECTION}"

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
    
    def get_categories_for_tracker(self, tracker) -> List[str]:
        """
        Get all categories of documents for a tracker
        """
        return self.documents.get_categories_for_tracker(tracker)
    
    def get_category_subcategory_pairs_for_tracker(self, tracker) -> List[str]:
        """
        Get all subcategories of documents for a tracker
        """
        return self.documents.get_category_subcategory_pairs_for_tracker(tracker)
    
    
class DocumentsTable(Database):
    """
    Class for interacting with the documents table
    """
    def __init__(self) -> None:
        """
        Initialize the documents table.
        """
        super().__init__()
        self.collection = self.conn[self.database][COLLECTION]
        self.xprops = self.conn[self.database]['extendedprops']

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
        fields = list(document.__fields_set__)
        fields.remove('id')
        values = document.dict()
        set_clause = {}
        for field in fields:
            set_clause[field] = values[field]
        return self.collection.update_one({'id': document.id}, {'$set': set_clause})

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
        document_doc = self.collection.find_one({'path': path})
        return Document(**document_doc) if document_doc else None

    def get_documents_for_tracker(self, tracker: Tracker) -> List[Document]:
        """
        Get all documents for a tracker
        """
        docs = list(self.collection.find({'id':{'$in': tracker.documents}}))
        return docs

    def get_count(self) -> int:
        """
        Get the number of documents in the database
        """
        return self.collection.count_documents({})
    
    def get_categories_for_tracker(self, tracker) -> List[str]:
        """
        Get all categories of documents for a tracker.

        I'm accessing the extendedprops collection directly here because I think
        I'm going to migrate the category and subcategory fields to the documents
        collection.
        """
        categories = self.xprops.distinct('classification', {'id':{'$in': tracker.documents}})
        return sorted(list(set([category for category in categories if category])))
    
    def get_category_subcategory_pairs_for_tracker(self, tracker) -> List[str]:
        """
        Get all subcategories of documents for a tracker.

        I'm accessing the extendedprops collection directly here because I think
        I'm going to migrate the category and subcategory fields to the documents
        collection.
        """
        subcategories = self.xprops.aggregate(
            [
                {'$match': {'id':{'$in': tracker.documents}}},
                {'$group': {
                    '_id': {'category': '$classification', 'subcategory': '$subclassification'},
                    'count': {'$sum': 1}
                    }
                },
            ]
        )
        result = [{'category': doc['_id']['category'], 'subcategory':doc['_id']['subcategory'], 'count': doc['count']} for doc in subcategories]
        result = sorted(result, key=lambda x: f"{x['category']}::{x['subcategory']}")
        print(result)
        return result
