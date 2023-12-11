"""
realproperty.py - Models for a real property information request and response
"""

from pydantic import BaseModel, Field, validator


class RealPropertyInfoRequest(BaseModel):
	address: str = Field(..., example="123 Main Street")
	city: str = Field(..., example="Anytown")
	state: str = Field(..., example="TX")
	zip_code: str = Field(..., example="75072")

class RealPropertyInfoResponse(BaseModel):
	attom_id: int = Field(..., example=50801352)
	tax_id: str = Field(..., example="R-3281-00F-0160-1")
	address: str = Field(..., example="123 MAIN STREET, ANYTOWN, TX 75072")
	county: str = Field(..., example="Collin")
	occupied_by: str = Field(..., example="OWNER OCCUPIED")
	last_sale_date: str = Field(..., example="1999-12-21")
	last_sale_amount: int = Field(..., example=158000)
	assessed_value: int = Field(..., example=498109)
	county_market_value: int = Field(..., example=498109)
	tax_year: str = Field(..., example="2022")
	tax_amount: float = Field(..., example=7016.58)
	owners: str = Field(..., example="THOMAS J DALEY, AVA P DALEY")
	approximate_value_midpoint: int = Field(..., example=515908)
	approximate_value_high: int = Field(..., example=521067)
	approximate_value_low: int = Field(..., example=510748)
	equity_amount: int = Field(..., example=445790)
