"""
db.py - Database Access
"""
import os
from pymongo import MongoClient
import settings  # NOQA


class Database():
    """
    Class for connecting to our database
    """
    conn = None

    def __init__(self) -> None:
        db_url = os.getenv('DB_URL', 'mongodb://localhost:27017')
        if not Database.conn:
            Database.conn = MongoClient(db_url)
            print("Connected to database at {}".format(db_url))
