"""
tracker.py - Tracker that contains a list of documents
"""
from typing import Dict, Optional
from uuid import uuid4
from pydantic import BaseModel
from models.document import Document


class Tracker(BaseModel):
    """
    Tracker model
    """
    id: Optional[str] = str(uuid4())
    name: str
    username: str
    documents: Optional[Dict[str, Document]] = {}

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "tracker-1",
                "name": "Client 20304 - Our Production",
                "user_name": "my@email.com",
                "documents": {}
            }
        }
