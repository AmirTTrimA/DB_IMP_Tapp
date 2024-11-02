from fastapi import FastAPI, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi import Depends, HTTPException
from fastapi import APIRouter
from pymongo import ASCENDING
from passlib.context import CryptContext
from bson import ObjectId
from database import init, get_db
from models import Tweet, User
from auth import router as auth_router
import logging
from datetime import datetime

app = FastAPI()
router = APIRouter()


@app.on_event("startup")
async def startup():
    await init()


app.include_router(auth_router)


@app.get("/", response_class=HTMLResponse)
async def read_root(db=Depends(get_db)):
    tweets = await db.tweets.find().to_list()
    return f"""
    <html>
        <head>
            <title>Twitter Clone</title>
        </head>
        <body>
            <h1>Twitter Clone</h1>
            <form action="/tweet" method="post">
                <textarea name="content" required></textarea>
                <button type="submit">Tweet</button>
            </form>
            <ul>
                {"".join(f"<li>{tweet['content']}</li>" for tweet in tweets)}
            </ul>
        </body>
    </html>
    """


@router.post("/tweets")
async def create_tweet(tweet: Tweet):
    new_tweet = Tweet(content=tweet.content, author_id=tweet.author_id)
    await new_tweet.insert()
    return {"id": str(new_tweet.id), "message": "Tweet created!"}



templates = Jinja2Templates(directory="templates")


@app.get("/tweets", response_class=HTMLResponse)
async def read_tweets(request: Request, skip: int = 0, limit: int = 10):
    tweets = await Tweet.find().skip(skip).limit(limit).to_list()
    return templates.TemplateResponse(
        "tweets.html", {"request": request, "tweets": tweets}
    )

@router.get("/tweets/{tweet_id}")
async def get_tweet(tweet_id: str):
    tweet = await Tweet.get(ObjectId(tweet_id))
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")
    return tweet



@router.get("/tweets/stats")
async def get_tweet_stats():
    pipeline = [
        {"$group": {"_id": "$author_id", "tweet_count": {"$sum": 1}}},
        {"$sort": {"tweet_count": -1}},
    ]
    stats = await Tweet.aggregate(pipeline).to_list()
    return stats


@router.get("/tweets")
async def get_tweets(skip: int = 0, limit: int = 10):
    tweets = await Tweet.find().skip(skip).limit(limit).to_list()
    return tweets


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register")
async def register(user: User):
    existing_user = await User.find_one(User.username == user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    user.hashed_password = pwd_context.hash(user.hashed_password)
    await user.insert()
    return {"msg": "User registered successfully!"}


@router.post("/login")
async def login(user: User):
    user_db = await User.find_one(User.username == user.username)
    if not user_db or not pwd_context.verify(
        user.hashed_password, user_db.hashed_password
    ):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"msg": "Login successful!"}


logging.basicConfig(level=logging.INFO)
