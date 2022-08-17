"""
audit.py - Audit Record Model
"""
from datetime import datetime
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field

class Audit(BaseModel):
    """
    Audit Record Model
    """
    id: Optional[str] = str(uuid4())
    description: str
    username: str
    admin_user: bool
    table: str
    record_id: str
    old_data: Optional[str] = None
    new_data: Optional[str] = None
    event_date: datetime = Field(default_factory=datetime.utcnow)
    success: bool
    message: Optional[str] = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "audit-1",
                "username": "test_user@test.com",
                "admin_user": False,
                "action": "create",
                "table": "tracker",
                "record_id": "tracker-1",
                "new_data": "{\"name\": \"Client 20304 - Our Production\"}"
            }
        }