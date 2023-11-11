"""
childsupport.py - Calculate child support
"""
from models.childsupport import ChildSupportRequest

# Updated for 2023 Tax Tables
TAX_TABLE_YEAR = 2023
FEDERAL_MINIMUM_WAGE = 7.25
SOCIAL_SECURITY_TAX_RATE = 0.062
SOCIAL_SECURITY_CAP = 160200.00
MEDICARE_TAX_RATE = 0.0145
TEXAS_NET_RESOURCES_LIMIT = 9200.00
FEDERAL_STANDARD_DEDUCTION = 13850.00

# Updated for 2023 Tax Tables
# https://www.nerdwallet.com/article/taxes/federal-income-tax-brackets
# [0] = upper limit of bracket
# [1] = tax rate
# [2] = tax on lower brackets
#
# So for a taxable income of $100,000:
#    Base tax = $16,290.00
#    Additional Tax = $100,000 - $95,375 * .24
#    Total Tax = Base Tax + Additional Tax
FEDERAL_INCOME_TAX_TABLE = [
	(11000, 0.10, 0.00),
	(44725, 0.12, 1100),
	(95375, 0.22, 5147.00),
	(182100, 0.24, 16290.00),
	(231250, 0.32, 37104.00),
	(578125, 0.35, 52832.00),
	(99999999999, 0.37, 174238.25),
]

TEXAS_CHILD_FACTORS = [
	[(1, 0, 0.20), (1, 1, 0.175), (1, 2, 0.16), (1, 3, 0.1475), (1, 4, 0.136), (1, 5, 0.1333), (1, 6, 0.1314), (1, 7, 0.13)],
	[(2, 0, 0.25), (2, 1, .225), (2, 2, .2063), (2,3,.19), (2,4,.1833), (2,5,.1786), (2,6,.175), (2,7, .1722)],
	[(3,0,.30), (3,1,.2738), (3,2,.252), (3,3,.24), (3,4,.2314), (3,5,.225), (3,6,.22), (3,7,.216)],
	[(4,0,.35), (4,1,.322), (4,2,.3033), (4,3,.29), (4,4,.28), (4,5,.2722), (4,6,.266), (4,7,.2609)],
	[(5,0,.40), (5,1,.3733), (5,2,.3543), (5,3,.34), (5,4,.3289), (5,5,.32), (5,6,.3127), (5,7,.3067)],
	[(6,0,.40), (6,1,.3771), (6,2,.36), (6,3,.3467), (6,4,.336), (6,5,.3273), (6,6,.32), (6,7,.3138)],
	[(7,0,.40), (7,1,.38), (7,2,.3644), (7,3,.352), (7,4,.3418), (7,5,.3333), (7,6,.3262), (7,7,.32)],
]

class TxChildSupportCalculator():
	"""
	Calculate Child Support in Texas.
	"""

	def calculate(self, request: ChildSupportRequest):
		"""
		Calculate child support
		"""
		monthly_wage_income = self.calculate_monthly_income(request.wage_income, request.wage_income_frequency)
		monthly_nonwage_income = self.calculate_monthly_income(request.nonwage_income, request.nonwage_income_frequency)
		social_security_tax = min(monthly_wage_income*12, SOCIAL_SECURITY_CAP) * SOCIAL_SECURITY_TAX_RATE
		medicare_tax = monthly_wage_income * MEDICARE_TAX_RATE
		taxable_income = monthly_nonwage_income + monthly_wage_income - social_security_tax - medicare_tax - FEDERAL_STANDARD_DEDUCTION
		federal_income_tax = self.calculate_federal_income_tax(taxable_income)
		net_monthly_resources = min(
			monthly_wage_income + monthly_nonwage_income - social_security_tax - medicare_tax - federal_income_tax - request.union_dues - request.health_insurance,
			TEXAS_NET_RESOURCES_LIMIT
		)
		factor = self.child_support_factor(request.number_of_children, request.other_children)
		monthly_child_support = net_monthly_resources * factor
		capped_flag = net_monthly_resources == TEXAS_NET_RESOURCES_LIMIT
		return {
			'net_monthly_resources': net_monthly_resources,
			'child_support': monthly_child_support,
			'capped_flag': capped_flag,
			'tax_table_version': f'{TAX_TABLE_YEAR}.1',
			'child_support_factor': factor,
		}

	def child_support_factor(self, number_of_children: int, number_of_other_children: int) -> float:
		"""
		Lookup the child support factor for the given number of children and other children
		
		Args:
			number_of_children (int): Number of children before the court
			number_of_other_children (int): Number of other children the obligor has the duty to support
		"""
		if number_of_children > 7:
			number_of_children = 7
		return TEXAS_CHILD_FACTORS[number_of_children-1][number_of_other_children][2]

	def calculate_federal_income_tax(self, taxable_income: float):
		"""
		Calculate federal income tax
		"""
		tax = 0.0
		for idx, bracket in enumerate(FEDERAL_INCOME_TAX_TABLE):
			if taxable_income <= bracket[0]:
				base_tax = bracket[2]
				if idx > 0:
					additional_tax = (taxable_income - FEDERAL_INCOME_TAX_TABLE[idx-1]) * bracket[1]
				else:
					additional_tax = 0.0
				tax = base_tax + additional_tax
				tax = bracket[2] + (taxable_income - bracket[2]) * bracket[1]
				break
		return round(tax, 2)

	def calculate_monthly_income(self, income: float, frequency: str):
		"""
		Calculate monthly income
		"""
		if frequency == 'weekly':
			return round(income * 52 / 12, 2)
		elif frequency == 'biweekly':
			return round(income * 26 / 12, 2)
		elif frequency == 'semimonthly':
			return round(income * 24 / 12, 2)
		elif frequency == 'monthly':
			return round(income, 2)
		else:
			raise ValueError(f"Invalid income frequency: {frequency}")