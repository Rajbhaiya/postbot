from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from postbot.plugins.setting import channel_settings_callback
from postbot import bot
from postbot.database.db_channel import *
from postbot.database.db_users import *

# ... (other code and imports) ...

@bot.on_callback_query(filters.regex(r'^manage_channels$'))
async def manage_channels_callback(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    try:
        # Get the user's channels
        user = await get_user(user_id)
        if not user or not user.get('channels'):
            await callback_query.answer("No channels found in your list.")
            return

        buttons = []
        for channel_id in user['channels']:
            try:
                chat = await bot.get_chat(channel_id)
                # Add a button for each channel
                buttons.append([InlineKeyboardButton(chat.title, callback_data=f'channel_options_{channel_id}')])
            except ChannelInvalid:
                continue

        buttons.append([InlineKeyboardButton("Back", callback_data="start_data")])

        await callback_query.edit_message_text("Your channels:", reply_markup=InlineKeyboardMarkup(buttons))

    except Exception as e:
        # Handle any exceptions and log them
        print(f"Error in manage_channels_callback: {e}")
        await callback_query.answer("An error occurred. Please try again later.")

@bot.on_callback_query(filters.regex(r'^channel_options_\d+$'))
async def channel_options_callback(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[2])

    try:
        buttons = [
            [InlineKeyboardButton("Channel Settings", callback_data=f'channel_settings_{channel_id}')],
            [InlineKeyboardButton("Delete Channel", callback_data=f'delete_channel_{channel_id}')],
            [InlineKeyboardButton("Back", callback_data="manage_channels")]
        ]

        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="Your updated message content.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

        # Delete the original message
        await callback_query.message.delete()

    except Exception as e:
        # Handle any exceptions and log them
        print(f"Error in channel_options_callback: {e}")
        await callback_query.answer("An error occurred. Please try again later.")

@bot.on_callback_query(filters.regex(r'^delete_channel_\d+$'))
async def delete_channel_callback(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[2])

    # Remove the channel from the user's database
    user = await get_user(user_id)
    if user and user['channels'] and channel_id in user['channels']:  # Fix: Access 'channels' as a dictionary key
        await remove_channel(user_id, channel_id)  # Fix: Call the 'remove_channel' function

    # Notify the user
    await callback_query.answer("Channel deleted successfully.")

    # Go back to the "Manage Channels" menu
    await manage_channels_callback(bot, callback_query)
