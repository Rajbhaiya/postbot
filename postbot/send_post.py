from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from postbot.database.db_channel import Channel
from postbot.database.db_reaction import Reaction
from postbot import bot

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

@bot.on_callback_query(filters.regex(r'^send_post_final_\d+$'))
async def send_post_final_callback(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[1])

    # Collect the data that you've gathered in previous steps
    # Replace these variables with the actual data you've collected
    text = "Your post text here"
    media_url = "Your media URL here"
    emoji = "Selected emoji here"
    link_buttons = ["Button 1 - URL 1", "Button 2 - URL 2"]  # Replace with actual buttons

    # Retrieve the stored emojis and buttons for this channel
    if channel_id in temp_emojis and channel_id in temp_buttons:
        emojis = temp_emojis[channel_id]
        link_buttons = temp_buttons[channel_id]

        # Construct the post message with emojis and buttons
        post_message = text
        if media_url:
            post_message += f"\n{media_url}"

        # Add emojis to the post
        if emoji:
            post_message += f"\n{emoji}"

        # Add link buttons to the post
        if link_buttons:
            post_message += "\n\nLinks:\n"
            post_message += "\n".join(link_buttons)

        try:
            # Send the post to the selected channel
            # Replace `channel_id` with the actual channel where you want to send the post
            await bot.send_message(channel_id, post_message)

            # Clear the emojis and buttons for this channel
            clear_data(channel_id)

            await callback_query.answer("Post sent successfully.")
        except Exception as e:
            # Handle any exceptions that may occur during the message sending process
            await callback_query.answer(f"Failed to send the post: {str(e)}")
    else:
        await callback_query.answer("No emojis or buttons found for this channel.")

@bot.on_callback_query(filters.regex(r'^send_post_\d+$'))
async def send_post_callback(bot, callback_query: CallbackQuery):
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
async def add_emoji_callback(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[2])

    # Create a list to store emojis
    emojis = []

    # Prompt the user to send emojis and store them temporarily
    await bot.send_message(user_id, "Please send the emojis separated by commas (e.g., 😀, 😂, 😍)")

    # Wait for the user to send the emojis
    emojis_message = await bot.listen(user_id, timeout=300)

    if emojis_message.text:
        # Split the user's input into emojis
        emoji_texts = emojis_message.text.split(',')
        emojis = [emoji.strip() for emoji in emoji_texts]

        # Store the emojis temporarily
        add_emojis(channel_id, emojis)

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

    await callback_query.answer("Emoji selection canceled.")
@bot.on_callback_query(filters.regex(r'^cancel_emoji_\d+$'))
async def cancel_emoji_selection(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[2])

    # Remove the stored emojis from temp_emojis for this channel
    if channel_id in temp_emojis:
        del temp_emojis[channel_id]

    await callback_query.answer("Emoji selection canceled.")

@bot.on_callback_query(filters.regex(r'^react_\d+_.+$'))
async def react_callback(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id, emoji = callback_query.data.split('_')[1:]

    # Create an instance of the Reaction class for the specific channel and emoji
    reaction = Reaction(channel_id, emoji)

    # Use the Reaction class to add the user's reaction
    reaction.add_reaction(user_id)

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
