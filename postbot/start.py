from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .add_channel import add_channel_callback
from .manage_channel import manage_channels_callback
from .send_post import send_post_callback
from app import bot

@bot.on_message(filters.command("start"))
async def start(bot, message):
    # Define the keyboard with three buttons
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Add Channel", callback_data="add_channel"),
                InlineKeyboardButton("Manage Channel", callback_data="manage_channels"),
            ],
            [InlineKeyboardButton("Send Post", callback_data="send_post")],
        ]
    )

    # Send a welcome message with the keyboard
    await message.reply("Welcome to your bot!\nPlease choose an action:", reply_markup=keyboard)
