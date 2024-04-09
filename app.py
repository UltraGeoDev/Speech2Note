from models.whisper import Speech2TextClient
from modules.logger import CustomLogger
from data.user_database import UserDatabase
import telebot  # type: ignore
import os

from routes.start import StartRoute

# create logger
logger = CustomLogger()

# get environment variables
api_key = os.environ.get("OPENAI_API_KEY", "")
telegram_bot_token = os.environ.get("TELEGRAM_TOKEN", "")
supabase_url = os.environ.get("SUPABASE_URL", "")
supabase_key = os.environ.get("SUPABASE_KEY", "")

if not all([api_key, telegram_bot_token, supabase_url, supabase_key]):
    logger.error("Missing environment variables.", "server")
    raise ValueError("Missing environment variables.")

# create supabase client
database = UserDatabase(supabase_url, supabase_key, logger)

# create bot
bot = telebot.TeleBot(telegram_bot_token)

# create speech2text client
whisper_client = Speech2TextClient(api_key=api_key, logger=logger)


# register routes
StartRoute(bot=bot, logger=logger, user_database=database)

if __name__ == "__main__":
    logger.info("App started.", "server")
    bot.infinity_polling()
