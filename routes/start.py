import telebot  # type: ignore
from modules.logger import CustomLogger
from data.user_database import UserDatabase


class StartRoute:
    """
    Class that handles '/start' command requests.

    Attributes:
        bot (telebot.TeleBot): The Telegram bot instance.
        logger (CustomLogger): The logger instance.
        database (UserDatabase): The user database instance.
    """

    def __init__(  # type: ignore
        self, bot: telebot.TeleBot, logger: CustomLogger, user_database: UserDatabase
    ) -> None:
        """
        Initializes the StartRoute instance.

        Args:
            bot (telebot.TeleBot): The Telegram bot instance.
            logger (CustomLogger): The logger instance.
            user_database (UserDatabase): The user database instance.
        """
        self.bot = bot
        self.logger = logger
        self.database = user_database

        # Handler for the '/start' command
        @bot.message_handler(commands=["start"])
        def start(message: telebot.types.Message) -> None:  # type: ignore
            """
            Handler method for the '/start' command.

            Args:
                message (telebot.types.Message): The message object.
            """
            self.__start(message)

        # Log route initialization
        self.logger.info("Start route initialized.", "server")

    def __start(self, message: telebot.types.Message) -> None:  # type: ignore
        """
        Handle start requests.

        Args:
            message (telebot.types.Message): The message object received from the user.

        Returns:
            None
        """

        code, user = self.database.get_user(message.chat.id)

        # If the user is not found in the database
        if code != 200 or user is None:
            self.database.new_user(message.chat.id, message.from_user.username)
            self.bot.send_message(
                message.chat.id,
                f"Привет, {message.from_user.username}!\n"
                + "---------------\n"
                + "Я бот, который поможет тебе создать полноценный конспект из аудио!"
                + "Пришли мне аудиофайл, и я помогу тебе создать конспект из него!\n"
                + "---------------\n"
                + "Посмотреть профиль /profile\n"
                + "Получить токены /tokens\n"
                + "Посмотреть цены /prices\n"
                + "Информация о боте /about\n"
                + "---------------",
            )
            return

        self.bot.send_message(
            message.chat.id,
            f"С возвращением, {user.name}!\n"
            + "---------------\n"
            + "Пришли мне аудиофайл, и я помогу тебе создать полноценный конспект из него!\n"
            + "---------------\n"
            + "Посмотреть профиль /profile\n"
            + "Получить токены /tokens\n"
            + "Посмотреть цены /prices\n"
            + "Информация о боте /about\n"
            + "---------------",
        )
