from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChannelPrivate
from __main__ import bot
from postbot.datababe.db_channel import *
from postbot.datababe.db_users import *

# Define the add_channel function (as shown in the previous response)

# Add a new callback function to manage and delete channels
@bot.on_callback_query(filters.regex(r'^manage_channels$'))
async def manage_channels_callback(bot, callback_query):
    user_id = callback_query.from_user.id
    status, channels = await get_channels(user_id)

    if status:
        text = "Below are your channels. You can manage them by deleting a channel from the list."
        buttons = []

        for channel in channels:
            try:
                chat = await bot.get_chat(channel)
                buttons.append([InlineKeyboardButton(f"🗑 Delete {chat.title}", callback_data=f'delete_channel_{channel}')])
            except ChannelInvalid:
                continue

        buttons.append([InlineKeyboardButton("Back", callback_data="start")])

        await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await callback_query.answer("No Channels Found. Add a channel using the provided button.")

# Add a new callback function to delete a channel
@bot.on_callback_query(filters.regex(r'^delete_channel_\d+$'))
async def delete_channel_callback(bot, callback_query):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[2])
    
    # Database Logic - Remove the channel from the user's list
    user = Users.get(user_id)
    
    if user and channel_id in user.channels:
        user.remove_channel(channel_id)
        await callback_query.answer("Channel deleted successfully.")
    else:
        await callback_query.answer("Channel not found in the database.")

@bot.on_callback_query(filters.regex(r'^add_channel_\d+$'))
async def add_channel_callback(bot, callback_query):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[2])

    # Call the add_channel function
    await add_channel(user_id, channel_id)
    await callback_query.answer("Processing your request...")  

