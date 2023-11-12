"""
childsupport.py - Models for a child support calcualtion request and response
"""

from pydantic import BaseModel, Field, validator


INCOME_FREQUENCY = ['weekly', 'biweekly', 'semimonthly', 'monthly', 'annually']
INCOME_FREQUENCY_CHOICES = ', '.join(INCOME_FREQUENCY[:-1]) + ', or ' + INCOME_FREQUENCY[-1]


class ChildSupportRequest(BaseModel):
	number_of_children: int = Field(..., example=2)
	other_children: int = Field(..., example=0)
	wage_income: float = Field(..., example=1000.00)
	wage_income_frequency: str = Field(..., example="weekly")
	nonwage_income: float = Field(..., example=0.00)
	nonwage_income_frequency: str = Field(..., example="weekly")
	self_employed: bool = Field(..., example=False)
	union_dues: float = Field(..., example=0.00)
	health_insurance: float = Field(..., example=0.00)
	mininum_wage: bool = Field(..., example=False)

	# validators
	@validator('number_of_children')
	def number_of_children_must_be_gt_zero(cls, v):
		if v < 1:
			raise ValueError('Number of children must greater than zero')
		return v
	
	@validator('other_children')
	def other_children_must_be_positive(cls, v):
		if v < 0:
			raise ValueError('Other children must be positive')
		return v
	
	@validator('wage_income')
	def wage_income_must_be_positive(cls, v):
		if v < 0:
			raise ValueError('Wage income must be positive')
		return v
	
	@validator('nonwage_income')
	def nonwage_income_must_be_positive(cls, v):
		if v < 0:
			raise ValueError('Non-wage income must be positive')
		return v
	
	@validator('union_dues')
	def union_dues_must_be_positive(cls, v):
		if v < 0:
			raise ValueError('Union dues must be positive')
		return v
	
	@validator('health_insurance')
	def health_insurance_must_be_positive(cls, v):
		if v < 0:
			raise ValueError('Health insurance must be positive')
		return v
	
	@validator('wage_income_frequency')
	def wage_income_frequency_must_be_valid(cls, v):
		if v not in INCOME_FREQUENCY:
			raise ValueError(f'Wage income frequency must be one of {INCOME_FREQUENCY_CHOICES}')
		return v
	
	@validator('nonwage_income_frequency')
	def nonwage_income_frequency_must_be_valid(cls, v):
		if v not in INCOME_FREQUENCY:
			raise ValueError(f'Non-wage income frequency must be one of {INCOME_FREQUENCY_CHOICES}')
		return v
	
	@validator('self_employed')
	def self_employed_must_be_boolean(cls, v):
		if not isinstance(v, bool):
			raise ValueError('Self employed must be a boolean')
		return v
	
	@validator('mininum_wage')
	def mininum_wage_must_be_boolean(cls, v):
		if not isinstance(v, bool):
			raise ValueError('Minimum wage must be a boolean')
		return v

class ChildSupportResponse(BaseModel):
	net_monthly_resources: float = Field(..., example=1000.00)
	child_support: float = Field(..., example=0.00)
	capped_flag: bool = Field(..., example=False)
	tax_table_version: str = Field(..., example="2023.1")
	child_support_factor: float = Field(..., example=0.25)
	monthly_wage_income: float = Field(..., example=1000.00)
	monthly_nonwage_income: float = Field(..., example=0.00)
	social_security_tax: float = Field(..., example=0.00)
	medicare_tax: float = Field(..., example=0.00)
	federal_income_tax: float = Field(..., example=0.00)

