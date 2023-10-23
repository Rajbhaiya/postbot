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


@bot.on_message((filters.document | filters.video | filters.audio | filters.photo) & filters.incoming & filters.private)
async def send_post_media_message(bot, message: Message):
    user_id = message.from_user.id

    if (user_id, message.chat.id) not in bot.registered_callbacks:
        return

    # Ask the user to send text for the post
    await message.reply("Please send the text for your post or /skip to post without text.")
    text_message = await bot.listen(user_id, timeout=300)
    text = text_message.text if text_message.text else ""

    user = await get_user(user_id)
    if not user:
        await callback_query.answer("User not found.")
        return

    user_channels = await get_channels(user_id)

    if not user_channels:
        await callback_query.answer("You haven't added any channels yet.")
        return

    # Create a list of buttons for each channel the user has added
    buttons = [
        [
            InlineKeyboardButton(channel.name, callback_data=f"select_channel_{channel.id}")
        ] for channel in user_channels
    ]

    buttons.append([InlineKeyboardButton("Cancel", callback_data="cancel_send_post")])

    await message.reply("Select a channel to send the post:", reply_markup=InlineKeyboardMarkup(buttons))

@bot.on_callback_query(filters.regex(r'^send_post_final_\d+$'))
async def send_post_final_callback(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[1])

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
async def send_post_callback(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    user = await get_user(user_id)
    if not user:
        await callback_query.answer("User not found.")
        return

    user_channel = await get_channels(user_id)

    if not user_channel:
        await callback_query.answer("You haven't added any channels yet.")
        return

    # Create a list of buttons for each channel the user has added
    buttons = [
        [
            InlineKeyboardButton(channel.name, callback_data=f"select_channel_{channel.id}")
        ] for channel in users.channels
    ]

    buttons.append([InlineKeyboardButton("Cancel", callback_data="cancel_send_post")])

    await callback_query.edit_message_text("Select a channel to send the post:", reply_markup=InlineKeyboardMarkup(buttons))

@bot.on_callback_query(filters.regex(r'^select_channel_\d+$'))
async def select_channel_callback(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[1])

    # Store the selected channel ID in the user's session
    await bot.set_collection(user_id, "selected_channel", channel_id)

    # Ask the user to send the media for the post
    await callback_query.message.reply("Please send the media for the post.")

@bot.on_callback_query(filters.regex(r'^cancel_send_post$'))
async def cancel_send_post_callback(bot, callback_query: CallbackQuery):
    # Clear the selected channel and temporary data from the user's session
    await bot.set_collection(callback_query.from_user.id, "selected_channel", None)
    await bot.set_collection(callback_query.from_user.id, "post_text", None)
    await bot.set_collection(callback_query.from_user.id, "media_url", None)
    await callback_query.message.delete()
                                           
@bot.on_callback_query(filters.regex(r'^add_emoji_\d+$'))
async def add_emoji_callback(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[2])

    # Prompt the user to send emojis and store them temporarily
    await bot.send_message(user_id, "Please send the emojis separated by commas (e.g., 😀, 😂, 😍)")

    # Wait for the user to send the emojis
    emojis_message = await bot.listen(user_id, timeout=300)

    if emojis_message.text:
        # Split the user's input into emojis
        emoji_texts = emojis_message.text.split(',')
        emojis = [emoji.strip() for emoji in emoji_texts]

        # Store the emojis temporarily
        temp_emojis[channel_id] = emojis

        # Create a button for each emoji
        emoji_buttons = [
            [InlineKeyboardButton(emoji, callback_data=f'react_{channel_id}_{emoji}')] for emoji in emojis
        ]

        # Add a "Done" button to finish emoji selection
        delete_emoji = [InlineKeyboardButton("Delete Emoji", callback_data=f'cancel_emoji_{channel_id}')]

        # Present the user with emoji selection buttons
        buttons = emoji_buttons + delete_emoji

        await callback_query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))

        await callback_query.answer("Emojis added successfully.")

    else:
        await callback_query.answer("Emoji selection canceled.")

    await callback_query.answer("Emoji selection canceled.")
@bot.on_callback_query(filters.regex(r'^cancel_emoji_\d+$'))
async def cancel_emoji_selection(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[2])

    # Remove the stored emojis from temp_emojis for this channel
    if channel_id in temp_emojis:
        del temp_emojis[channel_id]

    await callback_query.answer("Emoji selection canceled.")

reactions = {}

# Callback function to handle adding reactions
@bot.on_callback_query(filters.regex(r'^react_\d+_.+$'))
async def react_callback(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id, emoji = callback_query.data.split('_')[1:]

    # Define a unique identifier for the post (e.g., post_id)
    post_id = generate_unique_post_id()
    post = channel.add_post(text, media_url)
    post.unique_id = post_id  # Store the unique post_id

    # Check if the post is in the reactions dictionary
    if (channel_id, post_id) in reactions:
        post_reactions = reactions[(channel_id, post_id)]
    else:
        post_reactions = {}

    # Check if the emoji has already been reacted by the user
    if user_id in post_reactions:
        await callback_query.answer("You've already reacted with this emoji.")
        return

    # Add the user's reaction to the post_reactions dictionary
    post_reactions[user_id] = emoji
    reactions[(channel_id, post_id)] = post_reactions

    # You can store the reactions in your database or process them as needed
    # For example, let's say you have a Post and Reaction model:
    # You can create a Reaction object and link it to the corresponding post.
    reaction = Reaction(post_id, user_id, emoji)
    await reaction.save()  # Save the reaction in your database

    await callback_query.answer(f"You reacted with {emoji}")

@bot.on_callback_query(filters.regex(r'^add_link_button_\d+$'))
async def add_link_button_callback(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[2])

    # Implement the logic to handle adding link buttons
    instructions = "Please send the link buttons using the specified format. " \
                   "A button should have a text and a URL separated by '-'.\n" \
                   "Example: 'Google - google.com'\n\n" \
                   "For multiple buttons in a single row, use '|'. Write them in one line.\n" \
                   "Example: 'Google - google.com | Telegram - telegram.org'\n\n" \
                   "For multiple rows, write them in different lines.\n" \
                   "Example:\n" \
                   "Google - google.com\n" \
                   "Telegram - telegram.org\n" \
                   "Change - change.org\n" \
                   "Wikipedia - wikipedia.org'\n\n" \
                   "Now please send the buttons in this format or /cancel the process."

    await bot.send_message(user_id, instructions)

    # Wait for the user to send the link buttons
    link_buttons_message = await bot.listen(user_id, timeout=300)

    if link_buttons_message.text:
        # Split the user's input into individual link buttons
        link_buttons_texts = link_buttons_message.text.split('|')
        link_buttons = [button.strip() for button in link_buttons_texts]

        # Store the link buttons temporarily
        temp_buttons[channel_id] = link_buttons
        
        delete_url = [InlineKeyboardButton("Delete URL", callback_data=f'delete_buttons_{channel_id}')]

        # Present the user with emoji selection buttons
        buttons = emoji_buttons + links_buttons + delete_emoji + delete_url

        await callback_query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))        

        await callback_query.answer("Link buttons added successfully.")
    else:
        await callback_query.answer("No link buttons provided.")

@bot.on_callback_query(filters.regex(r'^delete_buttons_\d+$'))
async def delete_buttons_callback(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[2])

    # Implement code to delete buttons for the specific channel
    delete_temp_buttons(channel_id)

    await callback_query.answer("Buttons deleted successfully.")
