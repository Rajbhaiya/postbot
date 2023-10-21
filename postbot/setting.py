from pyrogram import emoji, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from postbot.database.db_channel import *
from app import bot


@bot.on_callback_query(filters.regex(r'^channel_settings_\d+$'))
async def channel_settings_callback(bot, callback_query):
    channel_id = int(callback_query.data.split('_')[2])

    text, markup, sticker_id = await channel_settings(channel_id, bot)

    if text:
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(markup), quote=True)
    else:
        await callback_query.message.delete()

@bot.on_callback_query(filters.regex(r'^edit_emojis_\d+$'))
async def edit_emojis_callback(bot, callback_query):
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

@bot.on_callback_query(filters.regex(r'^edit_sticker_\d+$'))
async def edit_sticker_callback(bot, callback_query):
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
