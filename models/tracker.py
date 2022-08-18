"""
tracker.py - Tracker that contains a list of documents
"""
from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class Tracker(BaseModel):
    """
    Tracker model
    """
    id: Optional[str] = str(uuid4())
    name: str
    client_reference: Optional[str]
    bates_pattern: Optional[str]
    documents: Optional[List[str]] = []  # List of document paths for this tracker.
    added_username: Optional[str]
    added_date: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_username: Optional[str]
    updated_date: Optional[datetime] = Field(default_factory=datetime.utcnow)
    auth_usernames: Optional[List[str]] = [] # List of usernames that can access this tracker.
    version: Optional[str] = str(uuid4())

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "tracker-1",
                "name": "Client 20304 - Our Production",
                "username": "my@email.com",
                "client_reference": "DALTHO01A",
                "bates_pattern": "TJD \\d{6}",
            }
        }

class TrackerUpdate(BaseModel):
    """
    Tracker Update model

    NOTE: This model must not have a docuemnts field.
    """
    id: str
    name: Optional[str]
    username: Optional[str]
    client_reference: Optional[str]
    bates_pattern: Optional[str]
    added_username: Optional[str]
    added_date: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_username: Optional[str]
    updated_date: Optional[datetime] = Field(default_factory=datetime.utcnow)
    auth_usernames: Optional[List[str]] = [] # List of usernames that can access this tracker.
    version: Optional[str] = str(uuid4())

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "tracker-1",
                "name": "New Tracker Name",
            }
        }
