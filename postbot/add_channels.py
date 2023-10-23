# Import the necessary modules
import asyncio.exceptions
from pyrogram.types import CallbackQuery, ChatMember
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChannelPrivate
from pyrogram import Client, filters
from postbot import bot
from postbot.database.db_channel import add_channel as cac, remove_channel, get_channel_info
from postbot.database.db_users import  add_channel as uac, remove_channel

@bot.on_callback_query(filters.regex(r'^add_channel$'))
async def add_channels(bot: Client, msg):
    user_id = msg.from_user.id
    bot_id = bot.me.id
    try:
        channel = await bot.ask(user_id,
                                "Please add me as **admin** with atleast 'Post Messages' and 'Edit message of others' rights to the desired channel "
                                "\n\nAfter that, forward a message from the channel. "
                                "\n\nCancel this process using /cancel. If their is no reply in 5 minutes, action will be auto cancelled.", timeout=300)
        while True:
            if channel.forward_from_chat:
                if channel.forward_from_chat.type.__str__() == "ChatType.CHANNEL":
                    channel_id = channel.forward_from_chat.id
                    try:
                        chat_member = await bot.get_chat_member(channel_id, bot_id)
                        chat_member_user = await bot.get_chat_member(channel_id, user_id)
                        if chat_member.privileges.can_post_messages and chat_member.privileges.can_edit_messages:
                            # Don't allow non-admins.
                            if chat_member_user.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                                success, info = get_channel_info(channel_id)
                                if success:
                                    try:
                                        admin_chat_member = await bot.get_chat_member(channel_id, info['admin_id'])
                                    except (ChatAdminRequired, UserNotParticipant, ChannelPrivate):
                                        await remove_channel(info['admin_id'], channel_id)
                                        admin_chat_member = None
                                else:
                                    admin_chat_member = None
                                # Already added channel and admin still admin.
                                if success and admin_chat_member and admin_chat_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                                    admin = await bot.get_users(info['admin_id'])
                                    text = f"This channel is already added by {admin.mention}"
                                    await channel.reply(text, quote=True)
                                else:
                                    await uac(user_id, channel_id)
                                    await cac(channel_id, user_id)
                                    await channel.reply("Thanks for choosing me. Now start managing this channel by customizing settings sent below.", quote=True)
                            else:
                                text = "I'm admin but you are not an admin there. I can't allow this."
                                await channel.reply(text, quote=True)
                            break
                        else:
                            text = "I'm admin but I don't have both of the necessary rights, 'Post Messages' and 'Edit message of others'. \n\nPlease try forwarding again or /cancel the process."
                            channel = await bot.ask(user_id, text, timeout=300, reply_to_message_id=channel.id)
                    except (ChatAdminRequired, UserNotParticipant, ChannelPrivate):
                        text = "I'm still not admin. Please try forwarding again or /cancel the process."
                        channel = await bot.ask(user_id, text, timeout=300, reply_to_message_id=channel.id)
                else:
                    text = 'This is not a channel message. Please try forwarding again  or /cancel the process.'
                    channel = await bot.ask(user_id, text, timeout=300, reply_to_message_id=channel.id)
            else:
                if channel.text.startswith('/'):
                    await channel.reply('Cancelled `Add Channel` Process !', quote=True)
                    break
                else:
                    text = 'Please forward a channel message or /cancel the process.'
                    channel = await bot.ask(user_id, text, timeout=300, reply_to_message_id=channel.id, filters=~filters.me)
    except asyncio.exceptions.TimeoutError:
        await msg.reply('Process has been automatically cancelled', quote=True)
