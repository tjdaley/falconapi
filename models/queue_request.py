"""
queue_request.py - Pydantic model for QueueRequest
"""

from typing import Optional, Dict
from uuid import uuid4
from pydantic import BaseModel, Field, validator


class QueueRequest(BaseModel):
    request_id: Optional[str] = str(uuid4())
    task: str
    payload: Dict
    username: str
    ttl: Optional[int] = 4

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "request_id": "gjdf894nfkbjf8943hjn:2024040100000000",
                "task": "classify",
                "payload": {
                    "doc_id": "doc-1",
                    "model": "default",
                },
                "username": "user1@test.com",
                "ttl": 4
            }
        }

    # validators
    @validator('task')
    def task_must_be_in_list(cls, v):
        valid_tasks = ['classify', 'summarize', 'transactions', 'page_audit', 'normalize_vendors', 'stop']
        if v not in valid_tasks:
            raise ValueError(f'Task must be one of {valid_tasks}')
        return v
    
    @validator('payload')
    def payload_content_must_be_valid(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Payload must be a dictionary')
        valid_models = ['default', 'openai', 'claude', 'google']
        if 'model' not in v:
            raise ValueError('Payload must contain a model')
        if v['model'] not in valid_models:
            raise ValueError(f'Model must be one of {valid_models}')
        if 'doc_id' not in v:
            raise ValueError('Payload must contain a doc_id')
        return v

    @validator('username')
    def username_must_be_email(cls, v):
        if '@' not in v:
            raise ValueError('Username must be an email address')
        return v
    
    @validator('ttl')
    def ttl_must_be_positive(cls, v):
        if v < 1:
            raise ValueError('TTL must be a positive integer')
        if v > 10:
            raise ValueError('TTL must be less than 10')
        return v