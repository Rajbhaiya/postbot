from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChannelPrivate
from __main__ import bot
from postbot.datababe.db_channel import *
from postbot.datababe.db_users import *


@bot.on_callback_query(filters.regex(r'^add_channel_\d+$'))
async def add_channel_callback(bot, callback_query):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split('_')[2])

    try:
        bot_chat_member = await bot.get_chat_member(channel_id, bot.me.id)

        if bot_chat_member.status == "administrator":
            forward_message = await bot.ask(user_id,
                "Please forward a message from the channel you want to add. "
                "After forwarding, I will check and complete the process. "
                "You can also cancel this process using /cancel.",
                timeout=300
            )

            if forward_message.forward_from_chat.type == "channel":
                channel_to_add_id = forward_message.forward_from_chat.id

                try:
                    channel_member = await bot.get_chat_member(channel_to_add_id, user_id)
                    if channel_member.status == "administrator":

                        # Database Logic - Check if the channel is already in the user's list
                        user = Users.get(user_id)
                        if user:
                            if channel_id in user.channels:
                                await forward_message.reply("Channel is already added in bot.")
                            else:
                                user.add_channel(channel_id)
                                await forward_message.reply("Channel added successfully!")
                        else:
                            user = Users(user_id)
                            user.add_channel(channel_id)
                            await forward_message.reply("Channel added successfully!")
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
    except BadRequest as e:
        await bot.send_message(user_id, f"Error: {e}")
