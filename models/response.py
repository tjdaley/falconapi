"""
response.py - Falcon API response
"""
from typing import Optional
from pydantic import BaseModel


class Response(BaseModel):
    """
    Response model - For Responses that do NOT contain an ID field.
    """
    message: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "message": "Falcon API Copyright (c) 2022, Thomas J. Daley, Esq. - Version 1.0.0"
            }
        }

class ResponseAndId(BaseModel):
    """
    Response model - For Responses that contain an ID field.
    """
    message: str
    id: Optional[str]
    version: Optional[str]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "message": "Document added",
                "id": "2876ce60-0f93-4548-8c2f-ac1014dd8697"
            }
        }
