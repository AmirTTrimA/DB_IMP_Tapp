from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from models import User, Tweet  # Import all models you want to register

database = None


async def init():
    global database
    try:
        client = AsyncIOMotorClient("mongodb://localhost:27017/")
        database = client["t_clone"]
        await init_beanie(
            database, document_models=[User, Tweet]
        )  # Register all models
    except Exception as e:
        print(f"Error initializing database: {e}")


async def get_db():
    if database is None:
        raise Exception("Database not initialized")
    return database
