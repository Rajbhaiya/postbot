from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from postbot.database.db_channel import *
from postbot.database.db_reaction import *
from postbot.database.db_users import *
import uuid
import time

from postbot import bot

def generate_unique_post_id():
    # Use a timestamp to ensure uniqueness
    timestamp = int(time.time() * 1000)  # Convert to milliseconds
    # Generate a random UUID (Universally Unique Identifier)
    unique_id = str(uuid.uuid4())
    # Combine timestamp and unique_id to create a unique post_id
    post_id = f"{timestamp}_{unique_id}"
    return post_id

temp_emojis = {}
temp_buttons = {}
reactions = {}

# When a user adds emojis to a channel, store them in the dictionary
def add_emojis(channel_id, emojis):
    if channel_id in temp_emojis:
        temp_emojis[channel_id].extend(emojis)
    else:
        temp_emojis[channel_id] = emojis

# When a user decides to delete emojis, remove them from the dictionary
def delete_emojis(channel_id):
    if channel_id in temp_emojis:
        del temp_emojis[channel_id]

def delete_temp_buttons(channel_id):
    if channel_id in temp_buttons:
        del temp_buttons[channel_id]

# When a post is sent successfully, clear the emojis and buttons for that channel
def clear_data(channel_id):
    delete_emojis(channel_id)
    delete_buttons(channel_id)

selected_channel = {}

@bot.on_callback_query(filters.regex(r'^select_channel.*'))
async def select_channel_callback(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[2])

    # Store the selected channel ID in the dictionary
    selected_channel[user_id] = channel_id

    await callback_query.message.reply("Please send the text for your post or /skip to post without text.")

@bot.on_message((filters.document|filters.video|filters.audio|filters.photo) & filters.incoming & filters.private)
async def send_post_text_or_media(bot, message: Message):
    user_id = message.from_user.id

    # Retrieve the selected channel from the dictionary
    user_channel = selected_channel.get(user_id)

    if not user_channel:
        return

    user_input = message.text if message.text else ""

    # Remove the selected channel from the dictionary
    if user_id in selected_channel:
        del selected_channel[user_id]

    # Create a list of buttons for emojis and links
    buttons = [
        [InlineKeyboardButton("Add Emoji", callback_data=f"add_emoji_{user_channel}")],
        [InlineKeyboardButton("Add Link", callback_data=f"add_link_button_{user_channel}")],
        [InlineKeyboardButton("Send Post", callback_data=f"send_post_final_{user_channel}")],
        [InlineKeyboardButton("Cancel", callback_data="cancel_send_post")]
    ]

    await message.reply(f"Your post content:\n\n{user_input}", reply_markup=InlineKeyboardMarkup(buttons))


@bot.on_callback_query(filters.regex(r'^send_post_final.*'))
async def send_post_final_callback(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[3])
    user_channel = selected_channel.get(user_id)
    selected_channel[user_id] = channel_id
    

    # Collect the data that you've gathered in previous steps
    text = await bot.get_collection(user_id, "post_text")
    media_url = await bot.get_collection(user_id, "media_url")
    emojis = temp_emojis.get(channel_id, [])
    link_buttons = temp_buttons.get(channel_id, [])

    # Construct the post message
    post_message = text
    if media_url:
        post_message += f"\n{media_url}"

    # Add emojis to the post
    if emojis:
        post_message += "\nEmojis: " + ", ".join(emojis)

    # Add link buttons to the post
    if link_buttons:
        post_message += "\n\nLinks:\n" + "\n".join(link_buttons)

    try:
        # Send the post to the selected channel
        await bot.send_message(channel_id, post_message)

        # Clear the temporary data for this channel
        clear_data(channel_id)

        await callback_query.answer("Post sent successfully.")
    except Exception as e:
        await callback_query.answer(f"Failed to send the post: {str(e)}")

@bot.on_callback_query(filters.regex(r'^send_post$'))
async def send_post(bot, callback_query: CallbackQuery):
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
                buttons.append([InlineKeyboardButton(chat.title, callback_data=f'select_channel_{channel_id}')])
            except ChannelInvalid:
                continue

        buttons.append([InlineKeyboardButton("Cancel", callback_data="cancel_send_post")])

        await callback_query.edit_message_text("Select a channel where you want send post:", reply_markup=InlineKeyboardMarkup(buttons))

    except Exception as e:
        # Handle any exceptions and log them
        print(f"Error in send_post: {e}")
        await callback_query.answer("An error occurred. Please try again later.")

@bot.on_callback_query(filters.regex(r'^cancel_send_post$'))
async def cancel_send_post_callback(bot, callback_query: CallbackQuery):
    # Clear the selected channel and temporary data from the user's session
    await bot.set_collection(callback_query.from_user.id, "selected_channel", None)
    await bot.set_collection(callback_query.from_user.id, "post_text", None)
    await bot.set_collection(callback_query.from_user.id, "media_url", None)
    await callback_query.message.delete()
