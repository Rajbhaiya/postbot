# Import the necessary modules
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ChatMember
from pyrogram.errors import ChatAdminRequired, UserNotParticipant
from pyrogram import Client, filters
from postbot import bot
from postbot.database.db_channel import add_channel as cad
from postbot.database.db_users import add_channel as uad

# Define the add_channel function

@bot.on_callback_query(filters.regex(r'^add_channel$'))
async def add_channels(bot: Client, msg):
    user_id = msg.from_user.id
    bot_id = bot.me.id

    try:
        channel = await bot.ask(user_id,
            "Please forward a message from the channel you want to add. "
            "After forwarding, I will check and complete the process. "
            "Cancel this process using /cancel. If there's no reply in 5 minutes, the action will be auto-canceled.",
            timeout=300
        )

        while True:
            if channel.forward_from_chat:
                if channel.forward_from_chat.type == "ChatType.CHANNEL":
                    channel_id = channel.forward_from_chat.id

                    # Check the admin status of the bot in the channel
                    bot_admin = await check_bot_admin_status(bot, channel_id)

                    if bot_admin:
                        user_admin = await check_user_admin_status(bot, channel_id, user_id)

                        if user_admin:
                            # Check if the user has necessary rights
                            user_rights = await check_user_rights(bot, channel_id, user_id)

                            if user_rights:
                                # Add the channel to db_channel
                                await cad(channel_id, user_id)

                                # Add the channel to db_users
                                await uad(user_id, channel_id)

                                # Continue with further customization
                                await channel.reply("Thanks for choosing me. Now start managing this channel by customizing settings sent below.", quote=True)

                                # Add other logic for channel customization as needed

                            else:
                                text = "You are an admin in the channel, but you don't have the necessary rights ('Post Messages' and 'Edit message of others')."
                                await channel.reply(text, quote=True)
                        else:
                            text = "You are not an admin or owner in the channel you want to add."
                            await channel.reply(text, quote=True)
                    else:
                        text = "Bot is not an admin in the channel."
                        await channel.reply(text, quote=True)
                    break
                else:
                    text = 'This is not a channel message. Please try forwarding again or /cancel the process.'
                    channel = await bot.ask(user_id, text, timeout=300, reply_to_message_id=channel.id)
            else:
                if channel.text.startswith('/'):
                    await channel.reply('Cancelled `Add Channel` Process!', quote=True)
                    break
                else:
                    text = 'Please forward a channel message or /cancel the process.'
                    channel = await bot.ask(user_id, text, timeout=300, reply_to_message_id=channel.id, filters=~filters.me)
    except asyncio.exceptions.TimeoutError:
        await msg.reply('Process has been automatically cancelled', quote=True)
