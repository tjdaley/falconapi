"""
childsupport.py - Calculate child support
"""
from collections import namedtuple
from models.childsupport import ChildSupportRequest

# Named tuple for holding tax bracket information
TaxBracket = namedtuple('TaxBracket', ['lower_limit', 'upper_limit', 'tax_rate', 'tax_on_lower_brackets'])

# Updated for 2023 Tax Tables
TAX_TABLE_YEAR = 2023
FEDERAL_MINIMUM_WAGE = 7.25
SOCIAL_SECURITY_TAX_RATE = 0.062
SOCIAL_SECURITY_CAP = 160200.00
MEDICARE_TAX_RATE = 0.0145
TEXAS_NET_RESOURCES_LIMIT = 9200.00
FEDERAL_STANDARD_DEDUCTION = 13850.00

# Percentage of self-employed person's employment income that is
# subject to payroll taxes.
SELF_EMPLOYMENT_TAXABLE_INCOME = 1.0 - (SOCIAL_SECURITY_TAX_RATE + MEDICARE_TAX_RATE)

# Updated for 2023 Tax Tables
# https://www.nerdwallet.com/article/taxes/federal-income-tax-brackets
# [0] = upper limit of bracket
# [1] = tax rate
# [2] = tax on lower brackets
#
# So for a taxable income of $100,000:
#    Base tax = $5,147.00
#    Additional Tax = ($100,000 - $95,375) * .24
#    Total Tax = Base Tax + Additional Tax
FEDERAL_INCOME_TAX_TABLE = [
	TaxBracket(0.00, 11000.00, 0.10, 0.00),
	TaxBracket(11001.00, 44725.00, 0.12, 1100),
	TaxBracket(44726.00, 95375.00, 0.22, 5147.00),
	TaxBracket(95376.00, 182100.00, 0.24, 16290.00),
	TaxBracket(182101.00, 231250.00, 0.32, 37104.00),
	TaxBracket(231251.00, 578125.00, 0.35, 52832.00),
	TaxBracket(578126.00, 99999999999.00, 0.37, 174238.25),
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
		if request.mininum_wage:
			request.wage_income = FEDERAL_MINIMUM_WAGE * 40.00
			request.wage_income_frequency = 'weekly'

		if request.self_employed:
			income_adjustment = SELF_EMPLOYMENT_TAXABLE_INCOME
			tax_rate_adjustment = 2.0
		else:
			income_adjustment = 1.0
			tax_rate_adjustment = 1.0

		annual_wage_income = self.calculate_annual_income(request.wage_income, request.wage_income_frequency)
		annual_nonwage_income = self.calculate_annual_income(request.nonwage_income, request.nonwage_income_frequency)
		annual_social_security_tax = min(annual_wage_income * income_adjustment, SOCIAL_SECURITY_CAP) * SOCIAL_SECURITY_TAX_RATE * tax_rate_adjustment
		annual_medicare_tax = annual_wage_income * income_adjustment * MEDICARE_TAX_RATE * tax_rate_adjustment
		annual_taxable_income = annual_nonwage_income + annual_wage_income - FEDERAL_STANDARD_DEDUCTION
		federal_income_tax = self.calculate_federal_income_tax(annual_taxable_income)
		annual_net_resources = min(
			annual_wage_income + annual_nonwage_income - annual_social_security_tax - annual_medicare_tax - federal_income_tax - request.union_dues * 12 - request.health_insurance * 12,
			TEXAS_NET_RESOURCES_LIMIT * 12
		)
		factor = self.child_support_factor(request.number_of_children, request.other_children)
		annual_child_support = annual_net_resources * factor
		capped_flag = (annual_net_resources * 12) == TEXAS_NET_RESOURCES_LIMIT

		return {
			'net_monthly_resources': round(annual_net_resources / 12.0, 2),
			'child_support': round(annual_child_support / 12.0, 2),
			'capped_flag': capped_flag,
			'tax_table_version': f'{TAX_TABLE_YEAR}.2',
			'child_support_factor': factor,
			'monthly_wage_income': annual_wage_income / 12.0,
			'monthly_nonwage_income': round(annual_nonwage_income / 12.0, 2),
			'social_security_tax': round(annual_social_security_tax / 12.0, 2),
			'medicare_tax': round(annual_medicare_tax / 12.0, 2),
			'federal_income_tax': round(federal_income_tax / 12.0, 2),
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
			if taxable_income >= bracket.lower_limit and taxable_income <= bracket.upper_limit:
				marginal_income = taxable_income - bracket.lower_limit + 1  # Add 1 so that we're taxing all of the income in the bracket
				additional_tax = marginal_income * bracket.tax_rate
				tax = bracket.tax_on_lower_brackets + additional_tax
				break
		return round(tax, 2)

	def calculate_annual_income(self, income: float, frequency: str):
		"""
		Calculate monthly income
		"""
		if frequency == 'weekly':
			return round(income * 52, 2)
		elif frequency == 'biweekly':
			return round(income * 26, 2)
		elif frequency == 'semimonthly':
			return round(income * 24, 2)
		elif frequency == 'monthly':
			return round(income * 12, 2)
		elif frequency in ['annually', 'yearly']:
			return round(income, 2)
		else:
			raise ValueError(f"Invalid income frequency: {frequency}")