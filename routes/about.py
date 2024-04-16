"""About route module."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

    import telebot  # type: ignore[import-not-found]


class AboutRoute:
    """Route handler for the '/about' command."""

    def __init__(self: AboutRoute, bot: telebot.TeleBot, logger: Logger) -> None:  # type: ignore[no-any-unimported]
        """Create the AboutRoute instance.

        Args:
        ----
            bot (telebot.TeleBot): The Telegram bot instance.
            logger (CustomLogger): The logger instance.

        """
        self.bot = bot
        self.logger = logger

        # Handler for the '/about' command
        @bot.message_handler(commands=["about"])
        def about(message: telebot.types.Message) -> None:  # type: ignore[no-any-unimported]
            """About command.

            Args:
            ----
                message (telebot.types.Message): The message object.

            """
            self.__about(message)

        # Log route initialization
        self.logger.info("About route initialized.", extra={"message_type": "server"})

    def __about(self: AboutRoute, message: telebot.types.Message) -> None:  # type: ignore[no-any-unimported]
        """About command.

        Args:
        ----
            message (telebot.types.Message): The message object.

        """
        # Sending information message
        self.bot.send_message(
            message.chat.id,
            "Бот *Speech2Note* поможет тебе создать конспект из аудиофайла.\n"
            "Репозиторий: [Speech2Note](https://github.com/Ultrageopro1966/Speech2Note)\n"
            "Нейросети: [GigaChat](https://developers.sber.ru/)\n"
            "База данных: [Supabase](https://supabase.io/)\n"
            "Разработчик: @UltraGeoDev\n"
            "По всем вопросам можешь смело писать на почту dev@ultrageopro.ru\n"
            "----------------\n"
            "Пришли мне аудиофайл, и я помогу тебе создать конспект из него.\n"
            "---------------\n"
            "Посмотреть профиль /profile\n"
            "Получить токены /tokens\n"
            "Посмотреть цены /prices\n"
            "Информация о боте /about\n"  # noqa: RUF001
            "---------------",
            parse_mode="Markdown",
        )
