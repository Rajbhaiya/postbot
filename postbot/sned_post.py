from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from pyrogram.errors import UserNotParticipant
from postbot.database.db_channel import Channel
from postbot.database.db_users import Users

bot = Client("my_bot")

@bot.on_message(filters.text & filters.incoming & filters.private)
async def send_post_text_message(bot, message):
    user_id = message.from_user.id

    if (user_id, message.chat.id) not in bot.registered_callbacks:
        return

    # Save the text message as the post
    text = message.text
    user = Users.get(user_id)

    channel_id = message.chat.id
    channel = Channel.get(channel_id)
    media_url = None  # Media URL for the post (you can set it as needed)

    # Create and save the post
    if channel and channel_id not in user.channels:
        user.channels.append(channel_id)
        user.save()
    post = channel.add_post(text, media_url)

    bot.registered_callbacks.remove((user_id, channel_id))
    await message.reply("Your post has been saved.")

@bot.on_message((filters.document | filters.video | filters.audio | filters.photo) & filters.incoming & filters.private)
async def send_post_media_message(bot, message):
    user_id = message.from_user.id

    if (user_id, message.chat.id) not in bot.registered_callbacks:
        return

    # Save the media message as the post
    text = ""  # You can set a text description if needed
    user = Users.get(user_id)

    channel_id = message.chat.id
    channel = Channel.get(channel_id)

    # Determine media type and store the media URL as needed
    if message.photo:
        media_url = message.photo.file_id
    elif message.document:
        media_url = message.document.file_id
    elif message.video:
        media_url = message.video.file_id
    elif message.audio:
        media_url = message.audio.file_id
    else:
        media_url = None

    # Create and save the post
    if channel and channel_id not in user.channels:
        user.channels.append(channel_id)
        user.save()
    post = channel.add_post(text, media_url)

    bot.registered_callbacks.remove((user_id, channel_id))
    await message.reply("Your post with media has been saved.")

@bot.on_callback_query(filters.regex(r'^send_post_\d+$'))
async def send_post_callback(bot, callback_query):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[1])

    user = Users.get(user_id)
    if not user or channel_id not in user.channels:
        await callback_query.answer("You don't have permission to send posts to this channel.")
        return

    # Present the user with options to add emoji and link buttons to the post
    buttons = [
        [InlineKeyboardButton("Add Emoji", callback_data=f"add_emoji_{channel_id}")],
        [InlineKeyboardButton("Add Link Button", callback_data=f"add_link_button_{channel_id}")],
        [InlineKeyboardButton("Send Post", callback_data=f"send_post_final_{channel_id}")],
    ]

    await callback_query.edit_message_text("Options for your post:", reply_markup=InlineKeyboardMarkup(buttons))

@bot.on_callback_query(filters.regex(r'^add_emoji_\d+$'))
async def add_emoji_callback(bot, callback_query):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[2])

    # Create a list of emojis (you can replace these with the actual emojis you want)
    emojis = ["👍", "👌", "❤️", "😃", "🔥"]

    # Create a button for each emoji
    emoji_buttons = [
        [InlineKeyboardButton(emoji, callback_data=f"react_{channel_id}_{emoji}")] for emoji in emojis
    ]

    # Add a "Done" button to finish emoji selection
    done_button = [InlineKeyboardButton("Done", callback_data=f"done_emojis_{channel_id}")]

    # Present the user with emoji selection buttons
    buttons = emoji_buttons + [done_button]

    await callback_query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))

# Add your emoji reaction handling code here

@bot.on_callback_query(filters.regex(r'^done_emojis_\d+$'))
async def done_emojis_callback(bot, callback_query):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[2])

    # Implement logic to finalize emoji selection for the post
    # You can save the reactions and update the post

    await callback_query.answer("Emoji selection is complete.")
