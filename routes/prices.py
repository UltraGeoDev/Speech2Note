"""Prices route module."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

    import telebot  # type: ignore[import-untyped]


class PricesRoute:
    """Prices route class."""

    def __init__(self: PricesRoute, bot: telebot.TeleBot, logger: Logger) -> None:  # type: ignore[no-any-unimported]
        """Initialize the PricesRoute instance.

        Args:
        ----
            bot (telebot.TeleBot): The Telegram bot instance.
            logger (CustomLogger): The logger instance.

        """
        self.bot = bot
        self.logger = logger

        # Handler for the '/prices' command
        @bot.message_handler(commands=["prices"])
        def prices(message: telebot.types.Message) -> None:  # type: ignore[no-any-unimported]
            """Handle method for the '/prices' command.

            Args:
            ----
                message (telebot.types.Message): The message object.

            """
            self.__prices(message)

        # Log route initialization
        self.logger.info("Prices route initialized.", extra={"message_type": "server"})

    def __prices(self: PricesRoute, message: telebot.types.Message) -> None:  # type: ignore[no-any-unimported]
        """Send the prices information to the user.

        Args:
        ----
            message (telebot.types.Message): The message object.

        """
        self.bot.send_message(
            message.chat.id,
            "Цены на генерацию конспектов по длине голосового сообщения/аудиофайла:\n"
            "---------------\n"
            "1 токен = 3 рубля\n"
            "---------------\n"
            "<1 min - 1 токен\n"
            "1-5 min - 5 токенов\n"
            "5-10 min - 10 токенов\n"
            "10-20 min - 15 токенов\n"
            "20-40 min - 25 токенов\n"
            ">40 min - 50 токенов\n"
            "Длина записи должна быть не больше часа!\n"
            "---------------\n"
            "Чтобы создать конспект, пришли мне головое сообщение\n"
            "---------------\n"
            "Посмотреть профиль /profile\n"
            "Посмотреть цены /prices\n"
            "Получить токены /tokens\n"
            "Информация o боте /about\n"
            "---------------",
        )
