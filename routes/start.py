"""Start route module."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

    import telebot  # type: ignore[import-untyped]

    from data.user_database import UserDatabase


class StartRoute:
    """Class that handles '/start' command requests.

    Attributes
    ----------
        bot (telebot.TeleBot): The Telegram bot instance.
        logger (CustomLogger): The logger instance.
        database (UserDatabase): The user database instance.

    """

    def __init__(  # type: ignore[no-any-unimported]
        self: StartRoute,
        bot: telebot.TeleBot,
        logger: Logger,
        user_database: UserDatabase,
    ) -> None:
        """Initializes the StartRoute instance.

        Args:
        ----
            bot (telebot.TeleBot): The Telegram bot instance.
            logger (CustomLogger): The logger instance.
            user_database (UserDatabase): The user database instance.

        """  # noqa: D401
        self.bot = bot
        self.logger = logger
        self.database = user_database

        # Handler for the '/start' command
        @bot.message_handler(commands=["start"])
        def start(message: telebot.types.Message) -> None:  # type: ignore[no-any-unimported]
            """Start command.

            Args:
            ----
                message (telebot.types.Message): The message object.

            """
            self.__start(message)

        # Log route initialization
        self.logger.info("Start route initialized.", extra={"message_type": "server"})

    def __start(self: StartRoute, message: telebot.types.Message) -> None:  # type: ignore[no-any-unimported]
        """Handle start requests.

        Args:
        ----
            message (telebot.types.Message): The message object received from the user.

        Returns:
        -------
            None

        """
        code, user = self.database.get_user(message.chat.id)
        ok_code = 200

        # If the user is not found in the database
        if code != ok_code or user is None:
            self.database.new_user(message.chat.id, message.from_user.username)
            self.bot.send_message(
                message.chat.id,
                f"Привет, {message.from_user.username}!\n"
                "Перед использованием рекомендуем заранее ознакомиться c ценами /prices.\n"  # noqa: E501
                "---------------\n"
                "Я бот, который поможет тебе создать полноценный конспект из аудио!"
                "Пришли мне голосовое сообщение, и я помогу тебе создать конспект из него!\n"  # noqa: E501
                "---------------\n"
                "Посмотреть профиль /profile\n"
                "Получить токены /tokens\n"
                "Информация о боте /about\n"
                "Посмотреть цены /prices\n"
                "---------------",
            )
            return

        self.bot.send_message(
            message.chat.id,
            f"C возвращением, {user.name}!\n"
            "Перед использованием рекомендуем заранее ознакомиться c ценами /prices.\n"
            "---------------\n"
            "Пришли мне голосовое сообщение, и я помогу тебе создать полноценный конспект из него!\n"  # noqa: E501
            "---------------\n"
            "Посмотреть профиль /profile\n"
            "Получить токены /tokens\n"
            "Информация o боте /about\n"
            "Посмотреть цены /prices\n"
            "---------------",
        )
