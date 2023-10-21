import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
from Config import DB_URL

# Create an AsyncIOMotorClient instance
motor = AsyncIOMotorClient(DB_URL, 27017)

# Access the database using the motor client
db = motor["postbot"]
