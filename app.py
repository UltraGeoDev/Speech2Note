"""Main app."""

import logging
import os
import threading
import warnings

import telebot  # type: ignore[import-untyped]

# kassa
from data.user_database import UserDatabase

# Importing custom modules
from modules.request_queue import Queue
from routes.about import AboutRoute
from routes.note import MainRoute
from routes.prices import PricesRoute
from routes.profile import ProfileRoute

# Importing route handlers
from routes.start import StartRoute
from routes.tokens import TokensRoute

# Disable warnings
warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(format="%(message_type)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


# Get environment variables
telegram_bot_token = os.environ.get("TELEGRAM_TOKEN", "")
supabase_url = os.environ.get("SUPABASE_URL", "")
supabase_key = os.environ.get("SUPABASE_KEY", "")
s2t_auth_data = os.environ.get("S2T_AUTH_DATA", "")
t2n_auth_data = os.environ.get("T2N_AUTH_DATA", "")
shop_provider = os.environ.get("SHOP_PROVIDER", "")

# Check if all required environment variables are provided
if not all(
    [
        telegram_bot_token,
        supabase_url,
        supabase_key,
        s2t_auth_data,
        t2n_auth_data,
        shop_provider,
    ],
):
    error_message = "Missing environment variables."
    logger.error(error_message, "server")
    raise ValueError(error_message)

# Create request queue
queue = Queue(timeout=10, logger=logger)

# Create user database instance
database = UserDatabase(supabase_url, supabase_key, logger)


# Create Telegram bot instance
bot = telebot.TeleBot(telegram_bot_token)


# Register route handlers
TokensRoute(
    bot=bot,
    logger=logger,
    user_database=database,
    provider_token=shop_provider,
)
StartRoute(bot=bot, logger=logger, user_database=database)
ProfileRoute(bot=bot, logger=logger, user_database=database)
AboutRoute(bot=bot, logger=logger)
PricesRoute(bot=bot, logger=logger)


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
    log_info = "App started."
    logger.info(log_info, extra={"message_type": "server"})

    # Start bot and queue threads
    bot_thread = threading.Thread(target=bot.infinity_polling)
    queue_thread = threading.Thread(target=queue.run)

    bot_thread.start()
    queue_thread.start()
