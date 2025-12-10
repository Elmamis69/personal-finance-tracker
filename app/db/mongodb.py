from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

mongodb = MongoDB()

async def connect_to_mongodb():
    """Connect to MongoDB"""
    print("Connecting to MongoDB...")
    mongodb.client = AsyncIOMotorClient(settings.mongodb_url)
    mongodb.db = mongodb.client[settings.mongodb_db_name]
    print(f"Connected to MongoDB: {settings.mongodb_db_name}")

async def close_mongodb_connection():
    """Close MongoDB connection"""
    print("Closing MongoDB connection...")
    if mongodb.client:
        mongodb.client.close()
    print("MongoDB connection closed.")

def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return mongodb.db