"""
db.py - Database Access
"""
import os
from pymongo import MongoClient
import settings  # NOQA
from util.log_util import get_logger


class Database():
    """
    Class for connecting to our database
    """
    conn = None
    database = os.getenv('DATABASE_NAME', 'falcon')

    def __init__(self, fail_silent: bool = True) -> None:
        logger = get_logger('falconapi/db.py')
        db_url = os.getenv('DB_URL', 'mongodb://localhost:27017')
        if not Database.conn:
            Database.conn = MongoClient(db_url)
            logger.info("Connected to database at {}".format(db_url))
        self.fail_silent = fail_silent
    
    def insert_one_result(self, inserted_id: str = None) -> dict:
        """
        Return for a fail-silent Insert operation
        """
        return {
            'acknowledged': False,
            'inserted_id': inserted_id,
            'already_exists': True
        }

    def update_one_result(self) -> dict:
        """
        Return for a fail-silent Update operation
        """
        return {
            'acknowledged': False,
            'matched_count': 0,
            'modified_count': 0,
            'upserted_id': None,
            'raw_result': None
        }
    
    def delete_one_result(self) -> dict:
        """
        Return for a fail-silent Delete operation
        """
        return {
            'acknowledged': False,
            'deleted_count': 0
        }
