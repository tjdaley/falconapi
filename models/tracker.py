"""
tracker.py - Tracker that contains a list of documents
"""
from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field, validator


DATASET_NAMES = [
	'TRANSFERS',
	'CASH_BACK_PURCHASES',
	'DEPOSITS',
	'CHECKS',
	'WIRE_TRANSFERS',
	'UNIQUE_ACCOUNTS',
	'MISSING_STATEMENTS',
	'MISSING_PAGES'
]

class Tracker(BaseModel):
	"""
	Tracker model
	"""
	id: Optional[str] = str(uuid4())
	name: str
	client_reference: Optional[str]
	bates_pattern: Optional[str]
	documents: Optional[List[str]] = []  # List of document paths for this tracker.
	added_username: Optional[str]
	added_date: Optional[datetime] = Field(default_factory=datetime.utcnow)
	updated_username: Optional[str]
	updated_date: Optional[datetime] = Field(default_factory=datetime.utcnow)
	auth_usernames: Optional[List[str]] = [] # List of usernames that can access this tracker.
	version: Optional[str] = str(uuid4())

	class Config:
		orm_mode = True
		schema_extra = {
			"example": {
				"id": "tracker-1",
				"name": "Client 20304 - Our Production",
				"username": "my@email.com",
				"client_reference": "DALTHO01A",
				"bates_pattern": "TJD \\d{6}",
			}
		}

class TrackerUpdate(BaseModel):
	"""
	Tracker Update model

	NOTE: This model must not have a docuemnts field.
	"""
	id: str
	name: Optional[str]
	username: Optional[str]
	client_reference: Optional[str]
	bates_pattern: Optional[str]
	added_username: Optional[str]
	added_date: Optional[datetime] = Field(default_factory=datetime.utcnow)
	updated_username: Optional[str]
	updated_date: Optional[datetime] = Field(default_factory=datetime.utcnow)
	auth_usernames: Optional[List[str]] = [] # List of usernames that can access this tracker.
	version: Optional[str] = str(uuid4())

	class Config:
		orm_mode = True
		schema_extra = {
			"example": {
				"id": "tracker-1",
				"name": "New Tracker Name",
			}
		}

class TrackerDatasetRequest(BaseModel):
	"""
	Tracker Dataset Request model
	"""
	id: str
	dataset_name: str

	class Config:
		orm_mode = True
		schema_extra = {
			"example": {
				"id": "tracker-1",
				"dataset_name": "TRANSFERS",
			}
		}

	# validators
	@validator('dataset_id')
	def dataset_name_must_be_in_list(cls, v):
		if v not in DATASET_NAMES:
			raise ValueError(f'Dataset name must be one of {DATASET_NAMES}')
		return v
	
class TrackerDatasetResponse(BaseModel):
	"""
	Tracker Dataset Response model
	"""
	id: str
	dataset_name: str
	data: List[dict]

	class Config:
		orm_mode = True
		schema_extra = {
			"example": {
				"id": "tracker-1",
				"dataset_name": "TRANSFERS",
				"data": [
					{
						"date": "2023-11-05",
						"amount": 100.00,
						"source": "Bank of America",
						"destination": "Chase Bank",
						"memo": "Payment for services rendered"
					}
				]
			}
		}
