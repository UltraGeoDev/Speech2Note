import telebot  # type: ignore
from modules.logger import CustomLogger
from data.user_database import UserDatabase


class TokensRoute:
    def __init__(self, bot: telebot.TeleBot, logger: CustomLogger, user_database: UserDatabase) -> None:  # type: ignore
        self.bot = bot
        self.logger = logger
        self.database = user_database

        @bot.message_handler(commands=["tokens"])
        def tokens(message: telebot.types.Message) -> None:  # type: ignore
            self.__tokens(message)

        self.logger.info("Tokens route initialized.", "server")

    def __tokens(self, message: telebot.types.Message) -> None:  # type: ignore

        code, user = self.database.get_user(message.chat.id)

        if code != 200:
            self.bot.send_message(
                message.chat.id,
                "Произошла ошибка. Попробуйте ещё раз позже.\nМы уже работаем над этим.",
            )

        if user is None:
            self.database.new_user(message.chat.id, message.from_user.username)
            self.bot.send_message(
                message.chat.id,
                f"Привет, {message.from_user.username}!\n"
                + "---------------\n"
                + "Ты не можешь получить токены, потому что ты не был зарегистрирован.\n"
                + "Но у меня хорошие новости! Я уже тебя зарагестрировал!\n"
                + "Пришли мне аудиофайл, и я помогу тебе создать конспект из него.\n"
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
            "На данном этапе разработки бота дополнительные токены можно получить только написав разработчику бота на почту:\n"
            + "dev@ultrageopro.ru\n"
            + "---------------\n"
            + "Приносим извинения за доставленные неудобства.\n"
            + "Пришли мне аудиофайл, и я помогу тебе создать конспект из него.\n"
            + "---------------\n"
            + "Посмотреть профиль /profile\n"
            + "Посмотреть цены /prices\n"
            + "Информация о боте /about\n"
            + "---------------",
        )
