from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from postbot.database.db_channel import Channel
from postbot.database.db_reaction import Reaction
temp_emojis = {}
temp_buttons = {}

# When a user adds emojis to a channel, store them in the dictionary
def add_emojis(channel_id, emojis):
    temp_emojis[channel_id] = emojis

# When a user decides to delete emojis, remove them from the dictionary
def delete_emojis(channel_id):
    if channel_id in temp_emojis:
        del temp_emojis[channel_id]

# When a post is sent successfully, clear the emojis and buttons for that channel
def clear_data(channel_id):
    delete_emojis(channel_id)
    delete_buttons(channel_id)


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

@bot.on_callback_query(filters.regex(r'^send_post_final_\d+$'))
async def send_post_final_callback(bot, callback_query):
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

    await callback_query.edit_message_text("Options for your post:", reply_markup=InlineKeyboardMarkup(buttons)
                                           
@bot.on_callback_query(filters.regex(r'^add_emoji_\d+$'))
async def add_emoji_callback(bot, callback_query):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[2])

    # Create a list of emojis (you can replace these with the actual emojis you want)
    emojis = ["👍", "👌", "❤️", "😃", "🔥"]

    # Create a button for each emoji
    emoji_buttons = [
        [InlineKeyboardButton(emoji, callback_data=f'react_{channel_id}_{emoji}')] for emoji in emojis
    ]

    # Add a "Done" button to finish emoji selection
    done_button = [InlineKeyboardButton("Done", callback_data=f'done_{channel_id}')]

    # Present the user with emoji selection buttons
    buttons = emoji_buttons + [done_button]

    await callback_query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))

@bot.on_callback_query(filters.regex(r'^react_\d+_.+$'))
async def react_callback(bot, callback_query):
    user_id = callback_query.from_user.id
    channel_id, emoji = callback_query.data.split('_')[1:]

    # Implement logic to count reactions to posts based on emoji
    # You can update the post and store the reaction data in your database

    # Let's assume you have a Reaction class to handle this
    reaction = Reaction(channel_id, emoji)
    reaction.add_reaction(user_id)  # Add the user's reaction

    await callback_query.answer(f"You reacted with {emoji}")

@bot.on_callback_query(filters.regex(r'^done_\d+$'))
async def done_callback(bot, callback_query):
    user_id = callback_query.from_user.id

    # Implement logic to finalize emoji selection for the post
    # You can save the reactions and update the post

    await callback_query.answer("Emoji selection is complete.")

@bot.on_callback_query(filters.regex(r'^add_link_\d+$'))
async def add_link_callback(bot, callback_query):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[2])

    instructions = ("**Buttons Format:** \n\n"
                    "A button should have a text and a URL separated by '`-`'. \ntext - link\n"
                    "Example: \n`Google - google.com` \n\n"
                    "For multiple buttons in a single row, use '`|`'. Write them in one line!!. \ntext1 - link1 | text2 - link2\n"
                    "Example: \n`Google - google.com | Telegram - telegram.org`. \n"
                    "For multiple rows, write them in different lines. \ntext1 - link1\ntext2 - link2\n"
                    "Example: \n`Google - google.com \n"
                    "Telegram - telegram.org | Change - change.org \n"
                    "Wikipedia - wikipedia.org` \n\n\n"
                    "Now Please **send the buttons** in this format or /cancel the process. \n\n")

    await bot.send_message(user_id, instructions)
