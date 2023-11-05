"""
extendedprops_table.py - Extended Properties Table
"""

from database.documents_table import COLLECTION
from database.db import Database
from models.document import ExtendedDocumentProperties


COLLECTION = 'extendedprops'

class ExtendedPropertiesDict(dict):
    """
    Dictionary of extended properties
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extendedprops = ExtendedPropertiesTable()

    def __getitem__(self, key):
        return self.extendedprops.get(key)

    def __setitem__(self, key, value):
        doc = self.extendedprops.get(key)
        if doc:
            self.extendedprops.update(value)
        else:
            self.extendedprops.create(value)

    def __delitem__(self, key):
        self.extendedprops.delete(key)

    def __contains__(self, key):
        return self.extendedprops.get(key) is not None

    def __iter__(self):
        return iter([doc['id'] for doc in self.extendedprops.get_all()])

    def __len__(self):
        return self.extendedprops.count()

    def __repr__(self):
        return f"{Database.database}.{COLLECTION}"

    def __str__(self):
        return f"{Database.database}.{COLLECTION}"

    def keys(self):
        docs = self.extendedprops.get_all()
        return [doc['id'] for doc in docs]
    
    def values(self):
        return self.extendedprops.get_all()

    def items(self):
        docs = self.extendedprops.get_all()
        return [(doc['id'], doc) for doc in docs]
    
    def get(self, key, default=None):
        return self.extendedprops.get(key) or default

class ExtendedPropertiesTable(Database):
    """
    Extended Properties Table
    """
    def __init__(self):
        super().__init__()
        self.collection = self.conn[self.database][COLLECTION]

    def get(self, id):
        """
        Get extended properties by id
        """
        return self.collection.find_one({'id': id})

    def get_all(self):
        """
        Get all extended properties
        """
        return self.collection.find()

    def count(self):
        """
        Get extended properties count
        """
        return self.collection.count_documents({})

    def create(self, extendedprops):
        """
        Create extended properties
        """
        return self.collection.insert_one(extendedprops.dict())

    def update(self, extendedprops: ExtendedDocumentProperties):
        """
        Update extended properties
        """
        d = extendedprops.dict()
        id = d.get('id')
        return self.collection.replace_one({'id': id}, d)

    def delete(self, id):
        """
        Delete extended properties
        """
        return self.collection.delete_one({'id': id})
