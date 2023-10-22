from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from .add_channels import *
from .manage_channel import *
from .send_post import *
from postbot import bot

@bot.on_message(filters.command("start"))
async def start(bot, message:Message):
    # Define the keyboard with three buttons
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Add Channel", callback_data="add_channel"),
                InlineKeyboardButton("Manage Channel", callback_data="manage_channels"),
            ],
            [InlineKeyboardButton("Send Post", callback_data="send_post_1")],
        ]
    )

    # Send a welcome message with the keyboard
    await message.reply("Welcome to your bot!\nPlease choose an action:", reply_markup=keyboard)
