"""
users_table.py - Users Table
"""
from database.db import Database
from models.user import User

COLLECTION = 'users'

class UsersTable(Database):
    """
    Class for interacting with the users table
    """
    def __init__(self) -> None:
        super().__init__()
        self.collection = self.conn[self.database][COLLECTION]

    def get_user(self, username: str) -> User:
        """
        Get a user from the database
        """
        user_doc = self.collection.find_one({'username': username})
        return User(**user_doc) if user_doc else None

    def create_user(self, user: User) -> dict:
        """
        Create a user in the database
        """
        existing_user = self.get_user_by_username(user.username)
        if existing_user:
            if self.fail_silent:
                return self.insert_one_result(user.username)
            raise Exception(f"User {user.username} already exists")
        return self.collection.insert_one(user.dict())

    def update_user(self, user: User) -> dict:
        """
        Update a user in the database
        """
        return self.collection.update_one(
            {'username': user.username},
            {'$set': {
                'password': user.password,
                'email': user.email,
                'full_name': user.full_name,
                'disabled': user.disabled,
                'admin': user.admin,
                'token': user.token
                }
            }
        )
    
    def update_password(self, user_id: str, password_hash: str) -> dict:
        """
        Update a user's password in the database
        """
        return self.collection.update_one(
            {'id': user_id},
            {'$set': {'password': password_hash}}
        )

    def delete_user(self, username: str) -> dict:
        """
        Delete a user from the database
        """
        return self.collection.delete_one({'username': username})

    def get_all_users(self) -> list:
        """
        Get all users from the database
        """
        return list(self.collection.find())

    def get_user_by_id(self, user_id: str) -> User:
        """
        Get a user from the database by id
        """
        user_doc = self.collection.find_one({'id': user_id})
        return User(**user_doc) if user_doc else None

    def get_user_by_username(self, username: str) -> User:
        """
        Get a user from the database by username
        """
        user_doc = self.collection.find_one({'username': username})
        return User(**user_doc) if user_doc else None

    def get_user_by_email(self, email: str) -> User:
        """
        Get a user from the database by email
        """
        user_doc = self.collection.find_one({'email': email})
        return User(**user_doc) if user_doc else None

    def get_user_by_full_name(self, full_name: str) -> User:
        """
        Get a user from the database by full name
        """
        user_doc = self.collection.find_one({'full_name': full_name})
        return User(**user_doc) if user_doc else None
    
    def get_user_by_token(self, token: str) -> User:
        """
        Get a user from the database by token
        """
        user_doc = self.collection.find_one({'token': token})
        return User(**user_doc) if user_doc else None
