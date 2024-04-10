import telebot  # type: ignore
from data.user_database import UserDatabase
from modules.logger import CustomLogger


class ProfileRoute:

    def __init__(self, bot: telebot.TeleBot, logger: CustomLogger, user_database: UserDatabase) -> None:  # type: ignore
        self.bot = bot
        self.logger = logger
        self.database = user_database

        @bot.message_handler(commands=["profile"])
        def profile(message: telebot.types.Message) -> None:  # type: ignore
            self.__profile(message)

        self.logger.info("Profile route initialized.", "server")

    def __profile(self, message: telebot.types.Message) -> None:  # type: ignore

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
                + "Ты не можешь видеть профиль, потому что ты не был зарегистрирован.\n"
                + "Но у меня хорошие новости! Я уже тебя зарагестрировал!\n"
                + "Пришли мне аудиофайл, и я помогу тебе создать конспект из него.\n"
                + "---------------\n"
                + "Посмотреть профиль /profile\n"
                + "Получить токены /tokens\n"
                + "Посмотреть цены /prices\n"
                + "---------------",
            )
            return

        self.bot.send_message(
            message.chat.id,
            f"Привет, {user.name}!\n"
            + "---------------\n"
            + f"У тебя {user.tokens} токенов.\n"
            + f"Аккаунт создан {user.created_at}\n"
            + "---------------\n"
            + "Получить токены /tokens\n"
            + "Посмотреть цены /prices\n"
            + "---------------\n"
            + "Пришли мне аудиофайл, и я помогу тебе создать конспект из него.\n"
            + "---------------",
        )
