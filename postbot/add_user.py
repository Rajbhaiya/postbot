from pyrogram import Client, filters
from pyrogram.types import Message

from .database.db_users import Users, USERS_MONGODB_DB
from Config import OWNER_ID
from postbot import bot

@bot.on_message(~filters.service, group=1)
async def users_mongodb(_, msg: Message):
    if msg.from_user:
        user_id = msg.from_user.id
        # Check if the user exists in the database
        user_data = await USERS_MONGODB_DB.find_one({"_id": user_id})
        if not user_data:
            # If the user doesn't exist, insert a new document
            await USERS_MONGODB_DB.insert_one({"_id": user_id})
        # No need to close the session

@bot.on_message(filters.user(OWNER_ID) & filters.command("stats"))
async def _stats(_, msg: Message):
    users_count = await USERS_MONGODB_DB.count_documents({})
    await msg.reply(f"Total Users: {users_count}", quote=True)
