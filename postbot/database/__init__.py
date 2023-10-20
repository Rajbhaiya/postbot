import asyncio
import pymongo
import logging
from pymongo.errors import ServerSelectionTimeoutError
from motor import motor_asyncio
from config import *

mongodb_client = pymongo.MongoClient(DB_URL, 27017)
motor = motor_asyncio.AsyncIOMotorClient(DB_URL, 27017)
db = mongodb_client["kagut"]

try:
    asyncio.get_event_loop().run_until_complete(motor.server_info())
except ServerSelectionTimeoutError:
    sys.exit(logging.critical("Can't connect to mongodb! Exiting..."))
