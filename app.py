import telebot  # type: ignore
import os
import threading
import sys
import logging

# Importing custom modules
from modules.logger import CustomLogger
from data.user_database import UserDatabase
from modules.request_queue import Queue
from modules.request import Request

# Importing route handlers
from routes.start import StartRoute
from routes.profile import ProfileRoute
from routes.prices import PricesRoute
from routes.tokens import TokensRoute
from routes.about import AboutRoute
from routes.note import MainRoute

import warnings

# Disable warnings
warnings.filterwarnings("ignore")

# Create logger
logger = CustomLogger()


# Get environment variables
telegram_bot_token = os.environ.get("TELEGRAM_TOKEN", "")
supabase_url = os.environ.get("SUPABASE_URL", "")
supabase_key = os.environ.get("SUPABASE_KEY", "")
s2t_auth_data = os.environ.get("S2T_AUTH_DATA", "")
t2n_auth_data = os.environ.get("T2N_AUTH_DATA", "")

# Check if all required environment variables are provided
if not all(
    [telegram_bot_token, supabase_url, supabase_key, s2t_auth_data, t2n_auth_data]
):
    logger.error("Missing environment variables.", "server")
    raise ValueError("Missing environment variables.")

# Create request queue
queue = Queue(timeout=10, logger=logger)

# Create user database instance
database = UserDatabase(supabase_url, supabase_key, logger)

# Create Telegram bot instance
bot = telebot.TeleBot(telegram_bot_token)

# Register route handlers
StartRoute(bot=bot, logger=logger, user_database=database)
ProfileRoute(bot=bot, logger=logger, user_database=database)
TokensRoute(bot=bot, logger=logger, user_database=database)
PricesRoute(bot=bot, logger=logger)
AboutRoute(bot=bot, logger=logger)

# Create main route handler instance
main_route = MainRoute(
    bot=bot,
    s2t_auth_data=s2t_auth_data,
    t2n_auth_data=t2n_auth_data,
    user_database=database,
    logger=logger,
    request_queue=queue,
)

# Set queue processing function
queue.processing_function = main_route.process_request

if __name__ == "__main__":
    # Log app start
    logger.info("App started.", "server")

    # Start bot and queue threads
    bot_thread = threading.Thread(target=bot.infinity_polling)
    queue_thread = threading.Thread(target=queue.run)

    bot_thread.start()
    queue_thread.start()
