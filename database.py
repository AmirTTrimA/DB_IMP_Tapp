# database.py
from pymongo import MongoClient
from dotenv import load_dotenv
import os

os.environ.pop('DB_Config', None)
os.environ.pop('DB', None)

load_dotenv()  # Load environment variables from .env file

client = MongoClient(os.getenv('DB_Config'))
print(os.getenv('DB_Config'))
# client = MongoClient(config('DB_Config_local'))
db = client[os.getenv('DB')]
# db = client[config('DB_local')]
users_collection = db['Users']
# users_collection = db['users']
tweets_collection = db['Tweets']
# tweets_collection = db['tweets']

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
