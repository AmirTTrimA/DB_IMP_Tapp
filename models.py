from datetime import datetime
from pydantic import BaseModel, EmailStr
from beanie import Document, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId


class Tweet(Document):  # Inherit from Document
    id: ObjectId = None
    content: str
    created_at: datetime = None  # Will be set in the constructor
    author_id: str = "default_author"

    def __init__(self, **data):
        super().__init__(**data)
        if self.created_at is None:
            self.created_at = datetime.now()  # Set current time if not provided


class User(Document):  # Inherit from Document
    username: str
    email: EmailStr
    hashed_password: str
    created_at: datetime = datetime.now()


class UserInDB(User):
    id: str
