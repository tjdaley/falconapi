"""
client.py - User model
"""
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel

class Client(BaseModel):
    id: Optional[str] = str(uuid4())
    name: str
    billing_number: str
    created_by: Optional[bool] = False
    enabled: Optional[bool] = True
    version: Optional[str] = str(uuid4())

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "asdflk7jksd234fjk",
                "name": "Daley, Thomas J.",
                "billing_number": "BR549",
                "created_by": "test_user@test.com",
                "enabled": True,
                "version": "asdflkjasdflkjasdf",
            }
        }
