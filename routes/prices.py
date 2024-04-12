import telebot  # type: ignore
from modules.logger import CustomLogger


class PricesRoute:

    def __init__(self, bot: telebot.TeleBot, logger: CustomLogger) -> None:  # type: ignore
        """
        Initializes the PricesRoute instance.

        Args:
            bot (telebot.TeleBot): The Telegram bot instance.
            logger (CustomLogger): The logger instance.
        """
        self.bot = bot
        self.logger = logger

        # Handler for the '/prices' command
        @bot.message_handler(commands=["prices"])
        def prices(message: telebot.types.Message) -> None:  # type: ignore
            """
            Handler method for the '/prices' command.

            Args:
                message (telebot.types.Message): The message object.
            """
            self.__prices(message)

        # Log route initialization
        self.logger.info("Prices route initialized.", "server")

    def __prices(self, message: telebot.types.Message) -> None:  # type: ignore
        """Send the prices information to the user.

        Args:
            message (telebot.types.Message): The message object.
        """
        self.bot.send_message(
            message.chat.id,
            "Цены на генерацию конспектов по длине аудиофайла:\n"
            + "---------------\n"
            + "1 токен = 3 рубля\n"
            + "---------------\n"
            + "<1 min - 1 токен\n"
            + "1-5 min - 5 токенов\n"
            + "5-10 min - 10 токенов\n"
            + "10-20 min - 15 токенов\n"
            + "20-40 min - 25 токенов\n"
            + ">40 min - 50 токенов\n"
            + "---------------\n"
            + "Чтобы создать конспект, пришли мне аудиофайл\n"
            + "Посмотреть профиль /profile\n"
            + "Получить токены /tokens\n"
            + "Информация о боте /about\n"
            + "---------------",
        )
