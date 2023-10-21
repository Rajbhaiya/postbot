from Config import *

from pyromod import listen
from pyrogram import Client, idle
from pyrogram.errors import ApiIdInvalid, ApiIdPublishedFlood, AccessTokenInvalid

from Config import LOGGER



bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


# Run Bot
if __name__ == "__main__":
    try:
        bot.start()
    except (ApiIdInvalid, ApiIdPublishedFlood):
        raise Exception("Your API_ID/API_HASH is not valid.")
    except AccessTokenInvalid:
        raise Exception("Your BOT_TOKEN is not valid.")
    uname = bot.me.username
    LOGGER.info(f"@{uname} Started Successfully!")
    idle()
    bot.stop()
    LOGGER.info("Bot stopped. Alvida!")
