# database.py
from pymongo import MongoClient
from models import User, Tweet
from datetime import datetime
from bson import ObjectId

client = MongoClient('mongodb://localhost:27017/')
db = client['t_clone']
users_collection = db['users']
tweets_collection = db['tweets']

def save_user(user):
    user_data = {
        'username': user.username,
        'email': user.email,
        'password': user.password,  # Hash this before saving
        'created_at': user.created_at,
        'last_active': user.last_active,
        'bio': user.bio,
        'profile_picture': user.profile_picture,
        'followers': user.followers,
        'following': user.following,
        'is_active': user.is_active
    }
    user_id = users_collection.insert_one(user_data).inserted_id
    return user_id  # Return the ObjectId of the new user

def save_tweet(tweet):
    tweet_data = {
        'user_id': tweet.user_id,
        'content': tweet.content,
        'created_at': tweet.created_at,
        'likes': tweet.likes,
        'retweets': tweet.retweets,
        'comments': tweet.comments,
        'media': tweet.media,
        'hashtags': tweet.hashtags,
        'mentions': tweet.mentions,
        'visibility': tweet.visibility
    }
    tweets_collection.insert_one(tweet_data)

def get_all_tweets():
    return list(tweets_collection.find())
