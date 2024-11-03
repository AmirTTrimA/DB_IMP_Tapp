# models.py
from datetime import datetime
from bson import ObjectId


class User:
    def __init__(self, username, email, password):
        self.user_id = None  # Add this line to track user ID
        self.username = username
        self.email = email
        self.password = password  # Hash this
        self.created_at = datetime.now()
        self.last_active = datetime.now()
        self.bio = ""
        self.profile_picture = ""
        self.followers = []
        self.following = []
        self.is_active = True


class Tweet:
    def __init__(
        self, user_id, content, hashtags=None, mentions=None, visibility="public"
    ):
        self.user_id = user_id  # This will be an ObjectId
        self.content = content
        self.created_at = datetime.now()
        self.likes = []
        self.retweets = []
        self.comments = []
        self.media = []
        self.hashtags = hashtags if hashtags is not None else []
        self.mentions = mentions if mentions is not None else []
        self.visibility = visibility
