from pyromod import listen
import pyrogram
from pyrogram import Client, idle
from pyrogram.errors import ApiIdInvalid, ApiIdPublishedFlood, AccessTokenInvalid
from Config import LOGGER
import logging
from postbot import bot, start, add_channels, manage_channel, send_post, setting, add_user

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the desired log level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create a logger for Pyrogram
pyrogram_logger = logging.getLogger('pyrogram')
pyrogram_logger.setLevel(logging.INFO)  # Set the log level for Pyrogram

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
