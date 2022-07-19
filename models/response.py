"""
response.py - Falcon API response
"""
from pydantic import BaseModel


class Response(BaseModel):
    """
    Response model
    """
    message: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "message": "Falcon API Copyright (c) 2022, Thomas J. Daley, Esq. - Version 1.0.0"
            }
        }