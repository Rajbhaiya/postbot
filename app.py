from Config import *

from pyromod import listen
from pyrogram import Client, idle
from pyrogram.errors import ApiIdInvalid, ApiIdPublishedFlood, AccessTokenInvalid

from Config import LOGGER



bot = Client(
    "bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="postbot"),
)


# Run Bot
if __name__ == "__main__":
    try:
        bot.start()
    except (ApiIdInvalid, ApiIdPublishedFlood):
        raise Exception("Your API_ID/API_HASH is not valid.")
    except AccessTokenInvalid:
        raise Exception("Your BOT_TOKEN is not valid.")
    uname = bot.me.username
    LOGGER.info(f"Started Successfully!")
    idle()
    bot.stop()
    LOGGER.info("Bot stopped. Alvida!")
