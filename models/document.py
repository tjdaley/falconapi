"""
document.py - Description of a document
"""
from datetime import datetime
from typing import Optional, List
from uuid import uuid4
from pydantic import BaseModel, Field


class Document(BaseModel):
    """
    Document model
    """
    id: Optional[str] = str(uuid4())
    path: str
    filename: str
    type: str
    title: str
    create_date: str
    document_date: Optional[str]
    beginning_bates: Optional[str]
    ending_bates: Optional[str]
    page_count: Optional[int]
    client_reference: Optional[str]
    added_username: Optional[str]
    added_date: datetime = Field(default_factory=datetime.utcnow)
    updated_username: Optional[str]
    updated_date: datetime = Field(default_factory=datetime.utcnow)
    version: Optional[str] = str(uuid4())

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "doc-1",
                "path": "C:\\Users\\my\\Documents\\Client 20304 - Our Production\\20304-OurProduction.pdf",
                "filename": "20304-OurProduction.pdf",
                "type": "application/pdf",
                "title": "20304-OurProduction",
                "create_date": "2020-04-01",
                "document_date": "2020-04-01",
                "beginning_bates": "TJD000001",
                "ending_bates": "TJD000009",
                "page_count": "9",
                "client_reference": "DALTHO01A",
            }
        }

class ExtendedDocumentProperties(BaseModel):
    """
    Extended Properties for a Document
    These are the properties that are unique to a class of documents or that are used
    in training the document classification models
    """
    id: str         # The id of the associated document, which much already be in the documents collection
    images: Optional[List[str]]
    text: Optional[str]
    props: Optional[dict]
    version: Optional[str] = str(uuid4())
