from models.whisper import Speech2TextClient
from modules.logger import CustomLogger
import telebot  # type: ignore
import os

# create logger
logger = CustomLogger()

# get environment variables
api_key = os.environ.get(
    "OPENAI_API_KEY", "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"
)
telegram_bot_token = os.environ.get(
    "TELEGRAM_TOKEN", "7025545038:AAE8erqS3PKGEG-t0orCQxm84h6yaA0DRw4"
)

if api_key is None or telegram_bot_token is None:
    logger.error("Missing environment variables.", "server")
    raise ValueError("Missing environment variables.")

# create bot
bot = telebot.TeleBot(telegram_bot_token)

# create client
whisper_client = Speech2TextClient(api_key=api_key, logger=logger)

if __name__ == "__main__":
    logger.info("App started.", "server")
    bot.infinity_polling()
