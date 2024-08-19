"""
discovery_requests.py - Models for discovery requests
"""
from typing import Optional, List, Union
from uuid import uuid4
from pydantic import BaseModel

class DiscoveryRequest(BaseModel):
    id: Optional[str] = str(uuid4())
    client_id: str
    discovery_type: str
    service_date: str
    due_date: Optional[str] = None
    party_name: str
    request_number: int
    request_text: str
    lookback_date: Optional[str] = None
    interpretations: Optional[List[str]] = []
    privileges: Optional[List[str]] = []
    objections: Optional[List[str]] = []
    response: Optional[str] = None
    responsive_classifications: Optional[List[str]] = []
    version: Optional[str] = str(uuid4())

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "asdflk7jksd234fjk",
                "client_id": "uuid-1234",
                "discovery_type": "PRODUCTION.INTERROGATORIES.DISCLOSURES.ADMISSIONS",
                "service_date": "2024-08-03",
                "due_date": "2024-09-02",
                "party_name": "John Q. Doe",
                "request_number": 1,
                "request_text": "All documents related to the case",
                "lookback_date": "2019-01-01",
                "interpretations": ["Interpretation 1", "Interpretation 2"],
                "privileges": ["Privilege 1", "Privilege 2"],
                "objections": ["Objection 1", "Objection 2"],
                "response": "Response to the request",
                "responsive_classifications": ["Classification 1", "Classification 2"],
                "version": "asdflk7jksd234fjk"
            }
        }

class DiscoveryRequests(BaseModel):
    requests: list[DiscoveryRequest]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "requests": [
                    {
                        "id": "asdflk7jksd234fjk",
                        "client_id": "uuid-1234",
                        "discovery_type": "PRODUCTION.INTERROGATORIES.DISCLOSURES.ADMISSIONS",
                        "service_date": "2024-08-03",
                        "due_date": "2024-09-02",
                        "party_name": "John Q. Doe",
                        "request_number": 1,
                        "request_text": "All documents related to the case",
                        "lookback_date": "2019-01-01",
                    },
                    {
                        "id": "asdflk7jksd234fjk",
                        "client_id": "uuid-1234",
                        "discovery_type": "PRODUCTION.INTERROGATORIES.DISCLOSURES.ADMISSIONS",
                        "service_date": "2024-08-03",
                        "due_date": "2024-09-02",
                        "party_name": "John Q. Doe",
                        "request_number": 2,
                        "request_text": "All bank statements related to the case",
                        "lookback_date": "2019-01-01",
                    }
                ]
            }
        }

#
# This represents a service document, not an individual request. The service document is a summary of all requests served to a client.
#
class ServedRequest(BaseModel):
    id: str
    client_id: str
    discovery_type: str
    service_date: str
    due_date: Optional[str] = None
    party_name: str
    request_count: int
    response_count: Optional[int] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "asdflk7jksd234fjk",
                "client_id": "uuid-1234",
                "discovery_type": "PRODUCTION.INTERROGATORIES.DISCLOSURES.ADMISSIONS",
                "service_date": "2024-08-03",
                "due_date": "2024-09-02",
                "party_name": "John Q. Doe",
                "request_count": 25,
                "response_count": 10
            }
        }

class ServedRequests(BaseModel):
    requests: list[ServedRequest]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "requests": [
                    {
                        "id": "asdflk7jksd234fjk",
                        "client_id": "uuid-1234",
                        "discovery_type": "PRODUCTION.INTERROGATORIES.DISCLOSURES.ADMISSIONS",
                        "service_date": "2024-08-03",
                        "due_date": "2024-09-02",
                        "party_name": "John Q. Doe",
                        "request_count": 25,
                    },
                    {
                        "id": "asdflk7jksd234fjl",
                        "client_id": "uuid-1234",
                        "discovery_type": "PRODUCTION.INTERROGATORIES.DISCLOSURES.ADMISSIONS",
                        "service_date": "2024-09-01",
                        "due_date": "2024-09-30",
                        "party_name": "John Q. Doe",
                        "request_count": 32,
                    }
                ]
            }
        }
