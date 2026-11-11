from pymongo import MongoClient
from pymongo.database import Database
from app.config import settings

client: MongoClient = MongoClient(settings.MONGO_URI)
db: Database = client[settings.DB_NAME]

def get_database() -> Database:
    return db

def get_books_collection():
    return db["books"]

def get_users_collection():
    return db["users"]

