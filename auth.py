import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from models import User, UserInDB
from database import init

router = APIRouter()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


@router.post("/register")
async def register(user: User):
    existing_user = await UserInDB.find_one(UserInDB.username == user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    user.hashed_password = hash_password(user.hashed_password)
    await user.insert()
    return {"msg": "User registered successfully!"}


@router.post("/login")
async def login(user: User):
    user_db = await UserInDB.find_one(UserInDB.username == user.username)
    if not user_db or not verify_password(user.password, user_db.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"msg": "Login successful!"}
