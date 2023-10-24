from pyrogram import emoji, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from postbot.database.db_channel import *
from postbot import bot


@bot.on_callback_query(filters.regex(r'^channel_settings.*'))
async def channel_settings_callback(bot, callback_query: CallbackQuery):
    channel_id = int(callback_query.data.split('_')[2])
    chat_id = callback_query.message.chat.id

    # Fetch the channel information from the Telegram API
    chat = await bot.get_chat(channel_id)
    channel_title = chat.title

    buttons = [
        [InlineKeyboardButton("Edit Sticker", callback_data=f'edit_sticker_{channel_id}')],
        [InlineKeyboardButton("Delete Sticker", callback_data=f'delete_sticker_{channel_id}')],
        [InlineKeyboardButton("Edit Emoji", callback_data=f'edit_emojis_{channel_id}')],
        [InlineKeyboardButton("Delete Emoji", callback_data=f'delete_emojis_{channel_id}')],
        [InlineKeyboardButton("Back", callback_data="manage_channels")]
    ]

    await bot.send_message(chat_id, text=f"**Setting For {channel_title}**", reply_markup=buttons)
    await callback_query.message.delete()

@bot.on_callback_query(filters.regex(r'^edit_emojis.*'))
async def edit_emojis_callback(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[2])

    # Fetch the current emojis from the database
    success, info = await get_channel_info(channel_id)
    emojis = info.get('emojis', [])

    text = f"Current Emojis: {', '.join(emojis)}\n\n"
    text += "Send the new emojis separated by commas (e.g., 😀, 😂, 😍)."

    # Ask the user to send the new emojis
    new_emojis_message = await bot.ask(user_id, text, timeout=300)

    if new_emojis_message.text:
        new_emojis = [emoji.strip() for emoji in new_emojis_message.text.split(",")]
        await add_emojis(channel_id, new_emojis)
        await callback_query.answer("Emojis updated successfully!")
    else:
        await callback_query.answer("Invalid input. Please send emojis separated by commas.")

@bot.on_callback_query(filters.regex(r'^edit_sticker.*'))
async def edit_sticker_callback(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[2])

    text = "Please send the sticker you want to set for this channel."

    # Ask the user to send the sticker
    sticker_message = await bot.ask(user_id, text, timeout=300)

    if sticker_message.sticker:
        sticker_id = sticker_message.sticker.file_id
        await set_sticker(channel_id, sticker_id)
        await callback_query.answer("Sticker set successfully!")
    else:
        await callback_query.answer("Invalid input. Please send a sticker.")

@bot.on_callback_query(filters.regex(r'^delete_sticker.*'))
async def delete_sticker_callback(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[2])

    # Remove the sticker from the channel
    await remove_sticker(channel_id)

    # Provide a callback answer
    await callback_query.answer("Sticker deleted successfully!")

@bot.on_callback_query(filters.regex(r'^delete_emojis.*'))
async def delete_emojis_callback(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[2])

    # Remove the emojis from the channel
    await remove_emojis(channel_id)

    # Provide a callback answer
    await callback_query.answer("Emojis deleted successfully!")
