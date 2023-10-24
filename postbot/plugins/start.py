from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from postbot.plugins.add_channels import *
from postbot.plugins.manage_channel import *
from postbot.plugins.send_post import *
from postbot import bot

@Client.on_message(filters.command('start') & filters.private)
async def start_command(bot, message: Message):
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
    await message.reply("Welcome to Postbot!\nPlease choose an action:", reply_markup=keyboard)
