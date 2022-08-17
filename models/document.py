"""
document.py - Description of a document
"""
from datetime import datetime
from typing import Optional
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

class TaxIncomeForm(BaseModel):
    """
    Tax form model
    """
    document: Document
    document_type: str = "tax_income_form"
    tax_year: Optional[str]
    issuer_name: Optional[str]
    tax_payer_name: Optional[str]
    form_name: Optional[str]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "doc-1",
                "path": "C:\\Users\\my\\Documents\\Client 20304 - Our Production\\2020.12.31 - Acme, Inc. W-2.pdf",
                "filename": "2020.12.31 - Acme, Inc. W-2.pdf",
                "type": "application/pdf",
                "title": "Acme, Inc. W-2",
                "create_date": "2021-02-28",
                "document_date": "2020-12-31",
                "beginning_bates": "TJD000001",
                "ending_bates": "TJD000001",
                "page_count": "1",
                "client_reference": "DALTHO01A",
                "document_type": "tax_income_form",
                "tax_year": "2020",
                "issuer_name": "Acme, Inc.",
                "tax_payer_name": "John Doe",
                "form_name": "W-2",
            }
        }

class TaxReturn(Document):
    """
    Tax Return model
    """
    document_type: str = "tax_return"
    tax_year: Optional[str]
    tax_period: Optional[str]
    filer_name: Optional[str]
    return_type: Optional[str]
    filed_date: Optional[str]
    authority: Optional[str]
    form_name: Optional[str]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "doc-1",
                "path": "C:\\Users\\my\\Documents\\Client 20304 - Our Production\\2021.12.31 - US 1040 Return.pdf",
                "filename": "2021.12.31 - US 1040 Return.pdf",
                "type": "application/pdf",
                "title": "US 1040 Return",
                "create_date": "2022-04-15",
                "document_date": "2021-12-31",
                "beginning_bates": "TJD000001",
                "ending_bates": "TJD000009",
                "page_count": "9",
                "client_reference": "DALTHO01A",
                "document_type": "tax_return",
                "tax_year": "2021",
                "filer_name": "John Doe",
                "return_type": "1040",
                "filed_date": "2022-04-15",
                "authority": "US",
                "form_name": "1040",
            }
        }

class AccountStatement(Document):
    """
    Account Statement model
    """
    doc_type: str = "account_statement"
    institution: Optional[str] = None
    account_number: Optional[str] = None
    description: Optional[str] = None
    holder_name: Optional[str] = None
    fbo_name: Optional[str] = None
    account_type: Optional[str] = None # TODO: add enum
    account_currency: str = 'USD'
    account_balance: Optional[float] = None
    account_balance_date: Optional[str] = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "doc-1",
                "path": "C:\\Users\\my\\Documents\\Client 20304 - Our Production\\2022.08.22 - BOA x1735 Statement.pdf",
                "filename": "2022.08.22 - BOA x1735 Statement.pdf",
                "type": "application/pdf",
                "title": "BOA x1735 Statement",
                "create_date": "2020-04-01",
                "document_date": "2020-04-01",
                "beginning_bates": "TJD000001",
                "ending_bates": "TJD000009",
                "page_count": "9",
                "client_reference": "DALTHO01A",
                "doc_type": "account_statement",
                "institution": "BOA",
                "account_number": "x1735",
                "description": "BOA x1735 Statement",
                "holder_name": "John Doe",
                "fbo_name": "John Doe, Jr.",
                "account_type": "Checking",
                "account_currency": "USD",
                "account_balance": 100.00,
                "account_balance_date": "2020-04-01",
            }
        }
