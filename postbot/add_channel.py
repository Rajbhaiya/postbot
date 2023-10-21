from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChannelPrivate
from main import bot
from postbot.database.db_channel import *
from postbot.database.db_users import *

# Define the add_channel function

async def add_channel(user_id, channel_id):
    try:
        # Check if the bot is an admin in the channel
        bot_chat_member = await bot.get_chat_member(channel_id, bot.me.id)

        if bot_chat_member.status == "administrator":
            # Ask the user to forward a message from the desired channel
            forward_message = await bot.ask(user_id,
                "Please forward a message from the channel you want to add. "
                "After forwarding, I will check and complete the process. "
                "You can also cancel this process using /cancel.",
                timeout=300
            )

            if forward_message.forward_from_chat.type == "channel":
                # The forwarded message is from a channel
                channel_to_add_id = forward_message.forward_from_chat.id

                try:
                    channel_member = await bot.get_chat_member(channel_to_add_id, user_id)
                    if channel_member.status == "administrator":
                        # The user is an admin in the channel they want to add

                        # Database Logic - Check if the channel is already in the user's list
                        user = Users.get(user_id)
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
                except UserNotParticipant:
                    await forward_message.reply("You are not a member of the channel you want to add.")
                except ChatAdminRequired:
                    await forward_message.reply("Bot is not an admin in the channel.")
            else:
                await forward_message.reply("Please forward a message from a channel.")
        else:
            await forward_message.reply("Bot is not an admin in the channel.")
    except ChatAdminRequired:
        await forward_message.reply("Bot is not an admin in the channel.")

# Add this function to your code

@bot.on_callback_query(filters.regex(r'^add_channel_\d+$'))
async def add_channel_callback(bot, callback_query):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[2])

    # Call the add_channel function
    await add_channel(user_id, channel_id)
    await callback_query.answer("Processing your request...")  # Notify the user that the request is being processed
