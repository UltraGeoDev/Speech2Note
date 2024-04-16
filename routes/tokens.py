"""Tokens route module."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

    import telebot  # type: ignore[import-not-found]

    from data.user_database import UserDatabase


class TokensRoute:
    """Route handling user requests related to tokens."""

    def __init__(  # type: ignore[no-any-unimported]
        self: TokensRoute,
        bot: telebot.TeleBot,
        logger: Logger,
        user_database: UserDatabase,
    ) -> None:
        """Create TokensRoute.

        Args:
        ----
            bot (telebot.TeleBot): The telebot instance.
            logger (CustomLogger): The logger instance.
            user_database (UserDatabase): The user database instance.

        """
        self.bot = bot
        self.logger = logger
        self.database = user_database

        @bot.message_handler(commands=["tokens"])
        def tokens(message: telebot.types.Message) -> None:  # type: ignore[no-any-unimported]
            """Tokens command.

            Args:
            ----
                message (telebot.types.Message): The message object received from the user.

            Returns:
            -------
                None

            """  # noqa: E501
            self.__tokens(message)

        self.logger.info("Tokens route initialized.", extra={"message_type": "server"})

    def __tokens(self: TokensRoute, message: telebot.types.Message) -> None:  # type: ignore[no-any-unimported]
        """Handle /tokens command.

        Args:
        ----
            message (telebot.types.Message): The message object received from the user.

        Returns:
        -------
            None

        """
        code, user = self.database.get_user(message.chat.id)
        ok_code = 200

        if code != ok_code:
            self.bot.send_message(
                message.chat.id,
                "Произошла ошибка. Попробуйте ещё раз позже.\nМы уже работаем над этим.",  # noqa: RUF001, E501
            )

        if user is None:
            self.database.new_user(message.chat.id, message.from_user.username)
            self.bot.send_message(
                message.chat.id,
                f"Привет, {message.from_user.username}!\n"
                "---------------\n"
                "Ты не можешь получить токены, потому что ты не был зарегистрирован.\n"
                "Но у меня хорошие новости! Я уже тебя зарагестрировал!\n"
                "Пришли мне аудиофайл, и я помогу тебе создать конспект из него.\n"
                "---------------\n"
                "Посмотреть профиль /profile\n"
                "Получить токены /tokens\n"
                "Посмотреть цены /prices\n"
                "Информация о боте /about\n"
                "---------------",
            )
            return

        self.bot.send_message(
            message.chat.id,
            "На данном этапе разработки бота дополнительные токены можно получить только написав разработчику бота на почту:\n"  # noqa: E501, RUF001
            "dev@ultrageopro.ru\n"
            "---------------\n"
            "Приносим извинения за доставленные неудобства.\n"
            "Пришли мне аудиофайл, и я помогу тебе создать конспект из него.\n"
            "---------------\n"
            "Посмотреть профиль /profile\n"
            "Посмотреть цены /prices\n"
            "Информация о боте /about\n"  # noqa: RUF001
            "---------------",
        )
