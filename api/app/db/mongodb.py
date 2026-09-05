"""MongoDB Connection Management."""
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDBManager:
    client: AsyncIOMotorClient = None
    db = None

db_manager = MongoDBManager()

async def connect_to_mongo():
    if getattr(settings, "MONGODB_URI", None):
        db_manager.client = AsyncIOMotorClient(settings.MONGODB_URI)
        db_manager.db = db_manager.client[getattr(settings, "MONGODB_DATABASE", "sift")]
        # Test connection
        await db_manager.client.admin.command('ping')
        print(f"Connected to MongoDB database: {db_manager.db.name}")

async def close_mongo_connection():
    if db_manager.client:
        db_manager.client.close()
        print("MongoDB connection closed.")

def get_mongo_db():
    return db_manager.db
