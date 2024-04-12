import telebot  # type: ignore
from modules.logger import CustomLogger


class AboutRoute:
    """
    Route handler for the '/about' command.
    """

    def __init__(self, bot: telebot.TeleBot, logger: CustomLogger) -> None:  # type: ignore
        """
        Initializes the AboutRoute instance.

        Args:
            bot (telebot.TeleBot): The Telegram bot instance.
            logger (CustomLogger): The logger instance.
        """
        self.bot = bot
        self.logger = logger

        # Handler for the '/about' command
        @bot.message_handler(commands=["about"])
        def about(message: telebot.types.Message) -> None:  # type: ignore
            """
            Handler method for the '/about' command.

            Args:
                message (telebot.types.Message): The message object.
            """
            self.__about(message)

        # Log route initialization
        self.logger.info("About route initialized.", "server")

    def __about(self, message: telebot.types.Message) -> None:  # type: ignore
        """
        Sends information about the bot to the user who triggered the '/about' command.

        Args:
            message (telebot.types.Message): The message object.
        """
        # Sending information message
        self.bot.send_message(
            message.chat.id,
            "Бот *Speech2Note* поможет тебе создать конспект из аудиофайла.\n"
            + "Репозиторий: [Speech2Note](https://github.com/Ultrageopro1966/Speech2Note)\n"
            + "Нейросети: [GigaChat](https://developers.sber.ru/)\n"
            + "База данных: [Supabase](https://supabase.io/)\n"
            + "Разработчик: @UltraGeoDev\n"
            + "По всем вопросам можешь смело писать на почту dev@ultrageopro.ru\n"
            + "----------------\n"
            + "Пришли мне аудиофайл, и я помогу тебе создать конспект из него.\n"
            + "---------------\n"
            + "Посмотреть профиль /profile\n"
            + "Получить токены /tokens\n"
            + "Посмотреть цены /prices\n"
            + "Информация о боте /about\n"
            + "---------------",
            parse_mode="Markdown",
        )
