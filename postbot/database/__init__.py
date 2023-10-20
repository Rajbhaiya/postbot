from pymongo import MongoClient
from pymongo.database import Database
from Config import MONGODB_URI, MONGODB_NAME

def start_mongodb() -> Database:
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DATABASE_NAME]
    return db

MONGODB_DB = start_mongodb()
