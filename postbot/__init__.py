from Config import *
from pyromod import listen
from pyrogram import Client 
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, plugins=dict(root="postbot.plugins"))
