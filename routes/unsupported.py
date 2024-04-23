"""Unsupported message route module."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

    import telebot  # type: ignore[import-untyped]


class UnsupportedRoute:
    """Route handling user requests that are not supported."""

    def __init__(self: UnsupportedRoute, bot: telebot.TeleBot, logger: Logger) -> None:  # type: ignore[no-any-unimported]
        """Create the UnsupportedRoute instance.

        Args:
        ----
            bot (telebot.TeleBot): The Telegram bot instance.
            logger (CustomLogger): The logger instance.

        """
        self.bot = bot
        self.logger = logger

        @bot.message_handler(
            content_types=[
                "photo",
                "video",
                "text",
                "location",
                "contact",
                "sticker",
            ],
        )
        def unsupported(message: telebot.types.Message) -> None:  # type: ignore[no-any-unimported]
            """Unsupported message handler.

            Args:
            ----
                message (telebot.types.Message): The message object.

            """
            self.__unsupported(message)

        # Log route initialization
        self.logger.info(
            "Unsupported route initialized.",
            extra={"message_type": "server"},
        )

    def __unsupported(self: UnsupportedRoute, message: telebot.types.Message) -> None:  # type: ignore[no-any-unimported]
        """Unsupported message handler.

        Args:
        ----
            message (telebot.types.Message): The message object.

        """
        self.bot.send_message(
            message.chat.id,
            "Извини, но я не понимаю, что делать c этим сообщением.\n"
            "Возможно, формат этого сообщения пока не поддерживается.\n"
            "Главное меню: /start",
        )
