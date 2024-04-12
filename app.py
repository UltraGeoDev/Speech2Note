import telebot  # type: ignore
import os
import threading
import sys

from modules.logger import CustomLogger
from data.user_database import UserDatabase
from modules.request_queue import Queue
from modules.request import Request

from routes.start import StartRoute
from routes.profile import ProfileRoute
from routes.prices import PricesRoute
from routes.tokens import TokensRoute
from routes.about import AboutRoute
from routes.note import MainRoute

import warnings

# disable warnings
warnings.filterwarnings("ignore")

# create logger
logger = CustomLogger()

# get environment variables
telegram_bot_token = os.environ.get("TELEGRAM_TOKEN", "")
supabase_url = os.environ.get("SUPABASE_URL", "")
supabase_key = os.environ.get("SUPABASE_KEY", "")
s2t_auth_data = os.environ.get("S2T_AUTH_DATA", "")
t2n_auth_data = os.environ.get("T2N_AUTH_DATA", "")


if not all(
    [telegram_bot_token, supabase_url, supabase_key, s2t_auth_data, t2n_auth_data]
):
    logger.error("Missing environment variables.", "server")
    raise ValueError("Missing environment variables.")

# create queue
queue = Queue(timeout=10, logger=logger, processing_function=lambda x: x)

# create supabase client
database = UserDatabase(supabase_url, supabase_key, logger)

# create bot
bot = telebot.TeleBot(telegram_bot_token)


# register routes
StartRoute(bot=bot, logger=logger, user_database=database)
ProfileRoute(bot=bot, logger=logger, user_database=database)
TokensRoute(bot=bot, logger=logger, user_database=database)
PricesRoute(bot=bot, logger=logger)
AboutRoute(bot=bot, logger=logger)

# create main route
main_route = MainRoute(
    bot=bot,
    s2t_auth_data=s2t_auth_data,
    t2n_auth_data=t2n_auth_data,
    user_database=database,
    logger=logger,
    request_queue=queue,
)


def processing_function(item: Request) -> None:
    main_route.process_request(item)


# set queue processing function
queue.processing_function = processing_function

if __name__ == "__main__":
    logger.info("App started.", "server")
    bot_thread = threading.Thread(target=bot.infinity_polling)
    queue_thread = threading.Thread(target=queue.run)

    bot_thread.start()
    queue_thread.start()
