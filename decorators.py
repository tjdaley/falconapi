"""
decorators.py - Decorators
"""
from fastapi import Request
from functools import wraps
import os


def check_api_token(func):
    @wraps(func)
    async def wrapper(*args, request: Request, **kwargs):
        HEADER = os.getenv('API_TOKEN_HEADER', 'x-authorization').lower()
        TOKEN = os.getenv('API_TOKEN', 'falcon')
        auth_header = request.headers.get(HEADER)
        if auth_header and auth_header == TOKEN:
            return await func(*args, request, **kwargs)
        raise(Exception('Invalid API token'))
    return wrapper
