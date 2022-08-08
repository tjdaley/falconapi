"""
tracker.py - Tracker that contains a list of documents
"""
from typing import List, Optional
from uuid import uuid4
from pydantic import BaseModel


class Tracker(BaseModel):
    """
    Tracker model
    """
    id: Optional[str] = str(uuid4())
    name: str
    username: str
    client_reference: Optional[str]
    documents: Optional[List[str]] = []  # List of document paths for this tracker.

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "tracker-1",
                "name": "Client 20304 - Our Production",
                "username": "my@email.com",
                "client_reference": "DALTHO01A",
                "documents": []
            }
        }
