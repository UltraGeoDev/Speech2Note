import telebot  # type: ignore
from modules.logger import CustomLogger


class AboutRoute:

    def __init__(self, bot: telebot.TeleBot, logger: CustomLogger) -> None:  # type: ignore
        self.bot = bot
        self.logger = logger

        @bot.message_handler(commands=["about"])
        def about(message: telebot.types.Message) -> None:  # type: ignore
            self.__about(message)

        self.logger.info("About route initialized.", "server")

    def __about(self, message: telebot.types.Message) -> None:  # type: ignore

        self.bot.send_message(
            message.chat.id,
            "Бот *Speech2Note* поможет тебе создать конспект из аудиофайла.\n"
            + "Репозиторий: [Speech2Note](https://github.com/Ultrageopro1966/Speech2Note)\n"
            + "Нейросети: [GigaChat](https://developers.sber.ru/)\n"
            + "База данных: [Supabase](https://supabase.io/)\n"
            + "Разработчик: @UltraGeoPro\n"
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
