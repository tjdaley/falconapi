"""
utility.py - A collection of utility functions
"""

from datetime import datetime
from os import environ
import requests

from fastapi import HTTPException, status


class Utilities():
    """
    Utility functions
    """
    # method to calculate the number of months between two dates
    @staticmethod
    def months_between(start_date: datetime, end_date: datetime) -> int:
        """
        Calculate the number of months between two dates

        Args:
            start_date (datetime): Start date
            end_date (datetime): End date

        Returns:
            int: Number of months between start and end dates
        """
        return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

    # method to retrieve property details using requests and an api key from a remote endpoint
    @staticmethod
    def get_property_details(address: str, city: str, state: str, zip_code: str) -> dict:
        """
        Retrieve property details using requests and an api key from a remote endpoint

        Args:
            address (str): Street address
            city (str): City
            state (str): State
            zip_code (str): Zip code

        Returns:
            dict: Property details
        """
        endpoint = '/property/basicprofile'

        params = {
            'address1': address,
            'address2': f'{city}, {state} {zip_code}',
        }
        property_data = query_attomdata(params, endpoint)
        property_description = parse_basic_property_data(property_data)

        endpoint = '/valuation/homeequity'
        equity_data = query_attomdata(params, endpoint)
        if not equity_data:
            return property_description
        valuation_data = parse_home_equity_data(equity_data)
        result = {**property_description, **valuation_data}
        return result

def parse_basic_property_data(property_data: dict) -> dict:
    """
    Parse property data

    Args:
        property_data (dict): Property data

    Returns:
        dict: Property description
    """
    property = property_data['property'][0]
    last_sale_data = property.get('sale', {}).get('saleAmountData', {})
    last_sale_date = last_sale_data.get('saleRecDate', 'n/a')
    last_sale_amount = last_sale_data.get('saleAmt', 0)

    assessment = property.get('assessment', {})
    assessed_value = assessment.get('assessed', {}).get('assdTtlValue', 0)
    county_market_value = assessment.get('market', {}).get('mktTtlValue', 0)
    tax_year = str(int(assessment.get('tax', {}).get('taxYear', 0)))
    tax_amount = assessment.get('tax', {}).get('taxAmt', 0)

    owner = assessment.get('owner', {})
    owners = []
    for owner_number in range(1, 4):
        owner_name_fn = owner.get(f'owner{owner_number}', {}).get('firstNameAndMi', '')
        owner_name_ln = owner.get(f'owner{owner_number}', {}).get('lastName', '')
        if owner_name_fn and owner_name_ln:
            owners.append(f'{owner_name_fn} {owner_name_ln}'.strip())
    owners = ', '.join(owners)
    return {
        'attom_id': property['identifier']['attomId'],
        'tax_id': property['identifier']['apn'],
        'address': property['address']['oneLine'],
        'county': property['area']['countrySecSubd'],
        'occupied_by': property['summary']['absenteeInd'],
        'last_sale_date': last_sale_date,
        'last_sale_amount': last_sale_amount,
        'assessed_value': assessed_value,
        'county_market_value': county_market_value,
        'tax_year': tax_year,
        'tax_amount': tax_amount,
        'owners': owners,
    }

def parse_home_equity_data(equity_data: dict) -> dict:
    """
    Parse home equity data

    Args:
        equity_data (dict): Home equity data

    Returns:
        dict: Home equity data
    """
    property = equity_data.get('property')
    if property is None:
        print("No property data found")
        print(equity_data)
        return {
            'approximate_value_midpoint': 0,
            'approximate_value_high': 0,
            'approximate_value_low': 0,
            'equity_amount': 0,
        }
    property = property[0]
    avm_data = property.get('avm', {})
    avm_amount = avm_data.get('amount', {})
    avm_value = avm_amount.get('value', 0)
    avm_high = avm_amount.get('high', 0)
    avm_low = avm_amount.get('low', 0)
    equity_data = property.get('homeEquity', {})
    equity_amount = equity_data.get('estimatedAvailableEquity', 0)

    return {
        'approximate_value_midpoint': avm_value,
        'approximate_value_high': avm_high,
        'approximate_value_low': avm_low,
        'equity_amount': equity_amount,
    }


def query_attomdata(parameters: dict, endpoint: str) -> dict:
    """
    Retrieve property details using requests and an api key from a remote endpoint

    Args:
        parameters (dict): Parameters to pass to the endpoint
        endpoint (str): Endpoint to call

    Returns:
        dict: Property details
    """
    api_key = environ.get('ATTOMDATA_API_KEY')
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ATTOMDATA_API_KEY not set in environment",
        )

    host = environ.get('ATTOMDATA_HOST')
    if host is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ATTOMDATA_HOST not set in environment",
        )
    headers = {
        'accept': 'application/json',
        'apikey': api_key,
    }

    property_data = {}

    try:
        # Send a GET request to retrieve property details
        response = requests.get(host + endpoint, headers=headers, params=parameters)

        if response.status_code == 200:
            # Parse the JSON response
            property_data = response.json()
        elif response.status_code == 400:
            print("Bad request")
            print("URL:", response.url)
            print("Response:", response.json())
        else:
            print(f"Request failed with status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")

    return property_data
