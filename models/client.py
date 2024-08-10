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
    created_by: str
    authorized_users: Optional[list] = []
    enabled: Optional[bool] = True
    version: Optional[str] = str(uuid4())
    cause_number: Optional[str] = None
    us_state: Optional[str] = None
    county: Optional[str] = None
    court_name: Optional[str] = None
    court_type: Optional[str] = None
    matter_type: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "asdflk7jksd234fjk",
                "name": "Daley, Thomas J.",
                "billing_number": "BR549",
                "cause_number": "123456789",
                "us_state": "TX",
                "county": "Dallas",
                "court_name": "256th Judicial District Court",
                "court_type": "District",
                "matter_type": "DIVC",
                "created_by": "test_user@test.com",
                "authorized_users": [
                    "test_user@test.com"
                ],
                "enabled": True,
                "version": "asdflkjasdflkjasdf",
            }
        }

class Clients(BaseModel):
    clients: list[Client]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "clients": [
                    {
                        "id": "asdflk7jksd234fjk",
                        "name": "Daley, Thomas J.",
                        "billing_number": "BR549",
                        "created_by": "test_user@test.com",
                        "authorized_users": [
                            "test_user@test.com"
                        ],
                        "enabled": True,
                        "version": "asdflkjasdflkjasdf",
                    }
                ]
            }
        }
