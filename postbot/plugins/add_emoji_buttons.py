from postbot import bot
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from .send_post import *


@bot.on_callback_query(filters.regex(r'^add_emoji.*'))
async def add_emoji_callback(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[2])
    user_channel = selected_channel.get(user_id)
    selected_channel[user_id] = channel_id

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

        # Create a list of buttons for each emoji
        emoji_buttons = [InlineKeyboardButton(emoji, callback_data=f'react_{channel_id}_{emoji}') for emoji in emojis]

        # Check if link buttons are already added
        link_buttons = temp_buttons.get(channel_id, [])

        # Add a "Done" button to finish emoji selection
        delete_emoji = [InlineKeyboardButton("Delete Emoji", callback_data=f'cancel_emoji_{channel_id}')]

        # Present the user with emoji selection buttons and other buttons
        buttons = [
            emoji_buttons + ([delete_emojis] if link_buttons else []),
            [InlineKeyboardButton("Add Link", callback_data=f"add_link_button_{user_channel}")],
            [InlineKeyboardButton("Send Post", callback_data=f"send_post_final_{user_channel}")],
            [InlineKeyboardButton("Cancel", callback_data="cancel_send_post")]
        ]
        await bot.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

        await callback_query.answer("Emojis added successfully.")

    else:
        await callback_query.answer("Emoji selection canceled.")

@bot.on_callback_query(filters.regex(r'^cancel_emoji.*'))
async def cancel_emoji_selection(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[2])
    user_channel = selected_channel.get(user_id)
    selected_channel[user_id] = channel_id

    # Remove the stored emojis from temp_emojis for this channel
    if channel_id in temp_emojis:
        del temp_emojis[channel_id]

    # Check if link buttons are already added
    link_buttons = temp_buttons.get(channel_id, [])

    if link_buttons:
        # If link buttons are added, include them along with other options
        buttons = [
            [InlineKeyboardButton("Add Emoji", callback_data=f"add_emoji_{user_channel}")],
            link_buttons + [delete_url],
            [InlineKeyboardButton("Send Post", callback_data=f"send_post_final_{user_channel}")],
            [InlineKeyboardButton("Cancel", callback_data="cancel_send_post")]
        ]
    else:
        # If no link buttons are added, display "Add Link" along with other options
        buttons = [
            [InlineKeyboardButton("Add Emoji", callback_data=f"add_emoji_{user_channel}")],
            [InlineKeyboardButton("Add Link", callback_data=f"add_link_button_{user_channel}")],
            [InlineKeyboardButton("Send Post", callback_data=f"send_post_final_{user_channel}")],
            [InlineKeyboardButton("Cancel", callback_data="cancel_send_post")]
        ]

        await bot.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        await callback_query.answer("Emoji selection canceled.")

@bot.on_callback_query(filters.regex(r'^add_link_button.*'))
async def add_link_button_callback(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[3])
    user_channel = selected_channel.get(user_id)
    selected_channel[user_id] = channel_id

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

        # Create a list of options
        buttons = [
            [InlineKeyboardButton("Add Emoji", callback_data=f"add_emoji_{user_channel}")],
            [link_buttons],
            [delete_url],
            [InlineKeyboardButton("Send Post", callback_data=f"send_post_final_{user_channel}")],
            [InlineKeyboardButton("Cancel", callback_data="cancel_send_post")]
        ]

        # If emoji buttons are added, include them
        if channel_id in temp_emojis:
            buttons = [
                [emoji_buttons],
                [link_buttons],
                [delete_emoji],
                [delete_url],
                [InlineKeyboardButton("Send Post", callback_data=f"send_post_final_{user_channel}")],
                [InlineKeyboardButton("Cancel", callback_data="cancel_send_post")]
            ]

        await bot.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        await callback_query.answer("Link buttons added successfully.")
    else:
        await callback_query.answer("No link buttons provided.")

@bot.on_callback_query(filters.regex(r'^delete_buttons.*'))
async def delete_buttons_callback(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[2])
    user_channel = selected_channel.get(user_id)
    selected_channel[user_id] = channel_id

    if channel_id in temp_emojis:
        # Emoji buttons have been added, so display them along with other options
        buttons = [
            emoji_buttons + [delete_emoji],
            [InlineKeyboardButton("Add Link", callback_data=f"add_link_button_{user_channel}")],
            [InlineKeyboardButton("Send Post", callback_data=f"send_post_final_{user_channel}")],
            [InlineKeyboardButton("Cancel", callback_data="cancel_send_post")]
        ]
    else:
        # Emoji buttons haven't been added, so display "Add Emoji" buttons
        buttons = [
            [InlineKeyboardButton("Add Emoji", callback_data=f"add_emoji_{user_channel}")],
            [InlineKeyboardButton("Add Link", callback_data=f"add_link_button_{user_channel}")],
            [InlineKeyboardButton("Send Post", callback_data=f"send_post_final_{user_channel}")],
            [InlineKeyboardButton("Cancel", callback_data="cancel_send_post")]
        ]

    # Implement code to delete buttons for the specific channel
    delete_temp_buttons(channel_id)
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    await callback_query.answer("Buttons deleted successfully.")


# Callback function to handle adding reactions
@bot.on_callback_query(filters.regex(r'^react.*'))
async def react_callback(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[1:])
    user_channel = selected_channel.get(user_id)

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
