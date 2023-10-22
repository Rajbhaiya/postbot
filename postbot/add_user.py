from pyrogram import Client, filters
from pyrogram.types import Message

from .database.db_users import Users, num_users
from .database import SESSION
from Config import OWNER_ID

@Client.on_message(~filters.service, group=1)
async def users_mongodb(_, msg: Message):
    if msg.from_user:
        user_id = msg.from_user.id
        # Check if the user exists in the database
        user_data = users_collection.find_one({"_id": user_id})
        if not user_data:
            # If the user doesn't exist, insert a new document
            users_collection.insert_one({"_id": user_id})
        # No need to close the session

@Client.on_message(filters.user(OWNER_ID) & filters.command("stats"))
async def _stats(_, msg: Message):
    # Get the total number of users from the database
    users_count = users_collection.count_documents({})
    await msg.reply(f"Total Users: {users_count}", quote=True)
