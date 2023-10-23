import asyncio
import time
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
from Config import DB_URL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create a logger for your application
logger = logging.getLogger('postbot')

# Create an AsyncIOMotorClient instance
motor = AsyncIOMotorClient(DB_URL, 27017)

try:
    # Access the database using the motor client
    db = motor["postbot"]
    logger.info("Connected to the MongoDB database.")
except ServerSelectionTimeoutError:
    logger.error("Failed to connect to the MongoDB database.")
