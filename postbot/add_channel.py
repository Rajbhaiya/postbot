# Import the necessary modules
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ChatMember
from pyrogram.errors import ChatAdminRequired, UserNotParticipant
from pyrogram import Client, filters
from postbot import bot
from postbot.database.db_channel import *
from postbot.database.db_users import Users

# Define the add_channel function

@bot.on_callback_query(filters.regex(r'^add_channel$'))
async def add_channel_callback(bot, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    print("add_channel_callback function triggered")
    try:
        # Ask the user to forward a message from the desired channel
        forward_message = await bot.ask(user_id,
            "Please forward a message from the channel you want to add. "
            "After forwarding, I will check and complete the process.",
            timeout=300
        )

        if forward_message.forward_from_chat.type == "channel":
            print(f"Message forwarded from a channel. Chat ID: {forward_message.forward_from_chat.id}")
            # The forwarded message is from a channel
            channel_id = forward_message.forward_from_chat.id

            try:
                # Check if the bot is an admin in the channel
                bot_chat_member = await bot.get_chat_member(channel_id, bot.me.id)

                if bot_chat_member.status == "administrator":
                    # The bot is an admin in the channel

                    channel_member = await bot.get_chat_member(channel_id, user_id)
                    if channel_member.status == "administrator":
                        # The user is an admin in the channel they want to add

                        # Database Logic - Check if the channel is already in the user's list
                        user = await Users.get(user_id)
                        if user:
                            if channel_id in user.channels:
                                await forward_message.reply("Channel is already added.")
                            else:
                                # Channel is not in the user's list, add it
                                user.add_channel(channel_id)
                                await forward_message.reply("Channel added successfully!")
                        else:
                            user = Users(user_id)
                            user.add_channel(channel_id)
                            await forward_message.reply("Channel added successfully!")

                        # You can also send additional messages or perform other actions here
                    else:
                        await forward_message.reply("You are not an admin in the channel you want to add.")
                else:
                    await forward_message.reply("Bot is not an admin in the channel.")
            except ChatAdminRequired:
                await forward_message.reply("Bot is not an admin in the channel.")
        else:
            await forward_message.reply("Please forward a message from a channel.")
    except Exception as e:
        print(f"Error in add_channel_callback: {e}")
