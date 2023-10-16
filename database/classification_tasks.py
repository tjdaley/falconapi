"""
classification_tasks.py - Classification Tasks Table
"""
from enum import Enum
from database.db import Database
from bson.objectid import ObjectId

COLLECTION = 'classification_tasks'

class ClassificationStatus(Enum):
    """
    Enumeration of possible classification statuses
    """
    QUEUED = 'QUEUED'
    PROCESSING = 'PROCESSING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'

class ClassificationTasksTable(Database):
    def __init__(self):
        super().__init__()
        self.tasks = self.conn[self.database][COLLECTION]

    def get(self, task_id: str):
        """
        Retrieve a classification task by its ID.
        """
        return self.tasks.find_one({'_id': ObjectId(task_id)})
    
    def add(self, doc_id: str) -> str:
        """
        Add a classification task to the database.
        """
        classification_task = {
            'document_id': doc_id,
            'status': ClassificationStatus.QUEUED.value,
            'classification': None
        }
        return str(self.tasks.insert_one(classification_task).inserted_id)
    
    def update(self, task_id: str, status: ClassificationStatus, message: str, classification: dict = None) -> str:
        """
        Update a classification task in the database.
        """
        self.tasks.update_one({'_id': ObjectId(task_id)}, {'$set': {'status': status.value, 'classification': classification, 'message': message}})
