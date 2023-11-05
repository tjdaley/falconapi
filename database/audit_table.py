"""
audit_table.py - Audit Table
"""
from database.db import Database
from models.audit import Audit


COLLECTION = 'auditlog'


class AuditTable(Database):
    """
    Audit Table
    """
    def __init__(self) -> None:
        """
        Initialize the documents table.
        """
        super().__init__()
        self.collection = self.conn[self.database][COLLECTION]

    def create_event(self, audit_event: Audit) -> dict:
        """
        Create a document in the database
        """
        r = self.collection.insert_one(audit_event.dict())
        return r
