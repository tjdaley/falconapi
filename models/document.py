"""
document.py - Description of a document
"""
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel


class Document(BaseModel):
    """
    Document model
    """
    id: Optional[str] = str(uuid4())
    tracker_id: str
    path: str
    filename: str
    title: str
    create_date: str
    document_date: Optional[str]
    beginning_bates: Optional[str]
    ending_bates: Optional[str]
    page_count: Optional[int]
    bates_pattern: Optional[str]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "doc-1",
                "tracker_id": "tracker-1",
                "path": "C:\\Users\\my\\Documents\\Client 20304 - Our Production\\20304-OurProduction.pdf",
                "filename": "20304-OurProduction.pdf",
                "title": "20304-OurProduction",
                "create_date": "2020-04-01",
                "document_date": "2020-04-01",
                "beginning_bates": "TJD000001",
                "ending_bates": "TJD000009",
                "page_count": "9",
                "bates_pattern": "TJD\d{6}"
            }
        }