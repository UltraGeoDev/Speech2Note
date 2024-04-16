"""Tokens route module."""

from __future__ import annotations

from typing import TYPE_CHECKING

import telebot  # type: ignore[import-untyped]

if TYPE_CHECKING:
    from logging import Logger

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
                "Информация о боте /about\n"
                "---------------",
            )
            return

        button1 = telebot.types.InlineKeyboardButton(
            "💸 10 токенов = 30₽",
            callback_data="10_tokens",
        )
        button2 = telebot.types.InlineKeyboardButton(
            "💸 50 токенов = 150₽",
            callback_data="50_tokens",
        )
        button3 = telebot.types.InlineKeyboardButton(
            "💸 100 токенов = 290₽ (-3%)",
            callback_data="100_tokens",
        )
        button4 = telebot.types.InlineKeyboardButton(
            "💸 300 токенов = 830₽ (-7%)",
            callback_data="300_tokens",
        )
        button5 = telebot.types.InlineKeyboardButton(
            "💸 1000 токенов = 2700₽ (-10%)",
            callback_data="300_tokens",
        )

        keyboard = telebot.types.InlineKeyboardMarkup(
            [[button1], [button2], [button3], [button4], [button5]],
        )

        self.bot.send_message(
            message.chat.id,
            "**Меню приобретения токенов.**\nГлавное меню /start\nДоступные покупки:",  # noqa: RUF001
            reply_markup=keyboard,
            parse_mode="Markdown",
        )
