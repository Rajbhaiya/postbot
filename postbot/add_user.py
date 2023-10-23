from pyrogram import Client, filters
from pyrogram.types import Message

from .database.db_users import save_user, USERS_DB, get_user
from Config import OWNER_ID
from postbot import bot

@bot.on_message(~filters.service, group=1)
async def users_mongodb(_, msg: Message):
    if msg.from_user:
        user_id = msg.from_user.id
        find_user = await get_user(user_id)
        if not find_data:
            await save_user(user_id)

@bot.on_message(filters.user(OWNER_ID) & filters.command("stats"))
async def _stats(_, msg: Message):
    users_count = await USERS_DB.user.count_documents({})
    await msg.reply(f"Total Users: {users_count}", quote=True)
