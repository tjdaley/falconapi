"""
document.py - Description of a document
"""
from datetime import datetime
from optparse import Option
from typing import Optional, List, Union
from uuid import uuid4
from pydantic import BaseModel, Field, root_validator


class Document(BaseModel):
    """
    Document model

    NOTE: The POST method in the doucments router does NOT update every field. If you add
    a field to this class AND you want the end user to be able to update that value in that
    field, you must make a corresponding change to the documents router's POST method.
    """
    id: Optional[str] = str(uuid4())
    path: str
    filename: str
    type: str
    title: str
    create_date: str
    document_date: Optional[Union[str, datetime]]
    beginning_bates: Optional[str]
    ending_bates: Optional[str]
    page_count: Optional[int]
    client_reference: Optional[str]
    added_username: Optional[str]
    added_date: datetime = Field(default_factory=datetime.utcnow)
    updated_username: Optional[str]
    updated_date: datetime = Field(default_factory=datetime.utcnow)
    version: Optional[str] = str(uuid4())
    classification: Optional[str]
    sub_classification: Optional[dict]

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
                "classification": "Bank Document",
                "sub_classification": {
                    "category": "Banking",
                    "subcategory": "Checking Account"
                }
            }
        }


class PutExtendedDocumentProperties(BaseModel):
    """
    Extended Properties for a Document
    These are the properties that are unique to a class of documents or that are used
    in training the document classification models
    """

    id: str  # The id of the associated document, which much already be in the documents collection
    images: Optional[List[str]]
    text: Optional[str]
    clean_text: Optional[str]
    props: Optional[dict]
    version: Optional[str] = str(uuid4())
    job_id: Optional[str] = None
    extraction_type: Optional[str] = None
    job_status: Optional[str] = None
    pages: Optional[int]
    tables: Optional[dict]
    has_tables: Optional[bool] = False

    @root_validator(pre=True)
    def exclude_tables(cls, values):
        if not values.get("has_tables"):
            values["has_tables"] = values.get("tables") is not None
        return values


class ExtendedDocumentProperties(BaseModel):
    """
    Extended Properties for a Document

    ** F O R   R E T R I E V A L   O N L Y **

    These are the properties that are unique to a class of documents or that are used
    in training the document classification models
    """
    id: str         # The id of the associated document, which much already be in the documents collection
    images: Optional[List[str]]
    text: Optional[str]
    clean_text: Optional[str]
    props: Optional[dict]
    version: Optional[str] = str(uuid4())
    job_id: Optional[str] = None
    extraction_type: Optional[str] = None
    job_status: Optional[str] = None
    pages: Optional[int]
    tables: Optional[dict] = Field(
        None,
        alias="dict_tables",  # database field name is dict_tables, mapped to tables in the model
        exclude=True,
        description="Always None. Call the documents/tables/csv or documents/tables/json endpoint to get the tables for a document."
        )
    has_tables: Optional[bool] = False

    @root_validator(pre=True)
    def exclude_tables(cls, values):
        if not values.get('has_tables'):
            values['has_tables'] = values.get('dict_tables') is not None
            values.pop('dict_tables', None)
        return values
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "doc-1",
                "images": [],
                "text": "This is the [text] of the document!!",
                "clean_text": "this is the text of the document",
                "props": {
                    "prop1": "value1",
                    "prop2": "value2"
                },
                "version": "dkf9kfk9jk4kf8glk",
                "job_id": "60a5c7d4b8a8e1f0f1c1b5d1",
                "extraction_type": "ANALYSIS",
                "job_status": "COMPLETED",
                "pages": 9,
                "tables": None,
                "has_tables": True
            }
        }


class DocumentCsvTables(BaseModel):
    """
    Tables for a document
    """
    id: str  # The id of the associated document, which much already be in the extendedprops collection
    csv_tables: Optional[dict]
    version: Optional[str] = str(uuid4())

class DocumentObjTables(BaseModel):
    """
    Tables for a document
    """
    id: str  # The id of the associated document, which much already be in the extendedprops collection
    json_tables: Optional[dict] = Field(alias="dict_tables")
    version: Optional[str] = str(uuid4())

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "doc-1",
                "json_tables": {
                    "tables": [
                        {
                            "table_id": "table-1",
                            "column_count": 3,
                            "rows": [
                                [
                                    {
                                        "text": "Row 1 Column 1",
                                    },
                                    {
                                        "text": "Row 1 Column 2",
                                    },
                                    {
                                        "text": "Row 1 Column 3"
                                    }
                                ],
                                [
                                    {
                                        "text": "Row 2 Column 1",
                                    },
                                    {
                                        "text": "Row 2 Column 2",
                                    },
                                    {
                                        "text": "Row 2 Column 3"
                                    }
                                ]
                            ]
                        },
                        {
                            "table_id": "table-2",
                            "column_count": 2,
                            "rows": [
                                [
                                    {
                                        "text": "Row 1 Column 1",
                                    },
                                    {
                                        "text": "Row 1 Column 2",
                                    }
                                ],
                                [
                                    {
                                        "text": "Row 2 Column 1",
                                    },
                                    {
                                        "text": "Row 2 Column 2",
                                    }
                                ]
                            ]
                        }
                    ]
                },
                "version": "dkf9kfk9jk4kf8glk"
            }
        }


class CategorySubcategoryResponse(BaseModel):
    """
    Response for a category/subcategory pair
    """
    category: str
    subcategory: str
    count: Optional[int] = 0

    class Config:
        schema_extra = {
            "example": {
                "category": "category1",
                "subcategory": "subcategory1",
                "count": 1
            }
        }

class DocumentClassificationStatus(BaseModel):
    """
    Status of a document classification task
    """
    task_id: Optional[str]
    document_id: str
    status: str  ## {'QUEUED', 'PROCESSING', 'COMPLETED', 'FAILED'}
    message: Optional[str]
    classification: Optional[dict]

    class Config:
        schema_extra = {
            "example": {
                "task_id": "60a5c7d4b8a8e1f0f1c1b5d1 OR None if called synchronously",
                "document_id": "e7e4fb7c-4d54-44b6-88d6-50509ff677cc",
                "status": "QUEUED",
                "message": "Document classification task has been queued.",
                "classification": None
            }
        }
