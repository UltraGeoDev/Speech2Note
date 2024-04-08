from models.whisper import Speech2TextClient
from modules.logger import CustomLogger
import telebot
import os

# create logger
logger = CustomLogger()

# get environment variables
api_key = os.environ.get("OPENAI_API_KEY", "")
telegram_bot_token = os.environ.get("TELEGRAM_TOKEN", "")

if api_key == "" or telegram_bot_token == "":
    logger.error("Missing environment variables.", "server")
    raise ValueError("Missing environment variables.")

# create bot
bot = telebot.TeleBot(telegram_bot_token)

# create client
whisper_client = Speech2TextClient(api_key=api_key, logger=logger)

if __name__ == "__main__":
    logger.info("App started.", "server")
    bot.infinity_polling()