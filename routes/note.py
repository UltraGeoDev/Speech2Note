"""Main route for bot.

Handles voice messages and processes requests.
"""

from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

import md2pdf  # type: ignore[import-untyped]

from model.oauth import get_token
from model.speech import speech2text
from model.text import text2note
from modules.audio_pocessing import AudioProcessing
from modules.request import Request

if TYPE_CHECKING:
    from logging import Logger

    import telebot  # type: ignore[import-untyped]

    from data.user_database import UserDatabase
    from modules.request_queue import Queue
    from modules.user import User


class MainRoute:
    """Class for handling voice messages and processing requests."""

    def __init__(  # type: ignore[no-any-unimported]  # noqa: PLR0913
        self: MainRoute,
        bot: telebot.TeleBot,
        s2t_auth_data: str,
        t2n_auth_data: str,
        user_database: UserDatabase,
        logger: Logger,
        request_queue: Queue,
    ) -> None:
        """Create MainRoute."""
        self.bot = bot
        self.logger = logger
        self.database = user_database
        self.s2t_auth_data = s2t_auth_data
        self.t2n_auth_data = t2n_auth_data
        self.request_queue = request_queue
        self.audio_pocessing = AudioProcessing(logger)

        @bot.message_handler(content_types=["voice"])
        def note(message: telebot.types.Message) -> None:  # type: ignore[no-any-unimported]
            """Voice messages and sends them to the queue."""
            self.__note(message)

        self.logger.info("Main route initialized.", extra={"message_type": "server"})

    @staticmethod
    def __get_price(duration: int) -> int:  # noqa: PLR0911
        """Calculate price for note based on duration."""
        first_level = 1
        second_level = 5
        third_level = 10
        fourth_level = 20
        fifth_level = 40
        max_level = 60

        if duration < first_level:
            return 1
        if duration < second_level:
            return 5
        if duration < third_level:
            return 10
        if duration < fourth_level:
            return 15
        if duration < fifth_level:
            return 25
        if duration > max_level:
            return -1
        return 50

    @staticmethod
    def split_string(string: str, length: int) -> list[str]:
        """Split string.

        Args:
        ----
            string (str): input string
            length (int): length of the substring

        Returns:
        -------
            list[str]: list of substrings

        """
        return [string[i : i + length] for i in range(0, len(string), length)]

    def __note(self: MainRoute, message: telebot.types.Message) -> int:  # type: ignore[no-any-unimported]
        """Process audio in chat and send request to the queue.

        Return 200 if successful.
        Return 500 if error.
        Return 404 if user not found or user already in queue.
        """
        voice_message: telebot.types.Voice = message.voice  # type: ignore[no-any-unimported]
        user_id = message.chat.id

        # get duration for note
        duration = voice_message.duration // 60

        # get queue length
        queue_len = len(self.request_queue)

        # waiting time
        time = queue_len * self.request_queue.timeout * queue_len // 60
        str_time = "<1 минуты" if time == 0 else f"{time} минут"

        to_text_request = Request(
            "to_text",
            str(voice_message.file_id),
            message.from_user.id,
            duration,
        )

        if (
            self.request_queue.user_in_queue(user_id, "to_text")
            or Path(f"data/chunks/{user_id}").exists()
        ):
            self.bot.send_message(
                user_id,
                "Извините, вы уже в очереди.\nПожалуйста, подождите.\nГлавное меню /start",  # noqa: RUF001, E501
            )
            self.logger.info("User already in queue.", extra={"message_type": "server"})
            return 404

        self.request_queue.put(to_text_request)
        self.bot.send_message(
            user_id,
            f"Вы добавлены в очередь. Запрос обрабатывается. Пожалуйста, подождите.\nПримерное время ожидания: {str_time}",  # noqa: E501, RUF001
        )

        return 200

    def process_request(self: MainRoute, request: Request) -> int:  # type: ignore[no-any-unimported]
        """Process request and return response.

        This method checks if the user with the specified ID exists in the database.
        If the user does not exist, the method sends an error message to the user and returns 404.

        If the user exists, the method checks if the user has enough tokens to make the request.
        If the user does not have enough tokens, the method sends an error message to the user and returns 403.

        If the user has enough tokens, the method processes the request. If an error occurs during
        the processing, the method sends an error message to the user and returns 500.

        If the request is successful, the method sends the document to the user and updates the user's tokens.
        The method then returns 200.

        Args:
        ----
            request (Request): Request to process.

        Returns:
        -------
            int: Response code.

        """  # noqa: E501
        code, user = self.database.get_user(request.user_id)

        ok_code = 200
        tokens_error = 403
        server_error = 500

        price = self.__get_price(request.duration)
        if price == -1:
            self.bot.send_message(
                request.user_id,
                "К сожалению, аудио слишком длинное.\n"  # noqa: RUF001
                "Длина записи должна быть не меньше часа.\n"
                "Главное меню /start",
            )
            return 403

        if code != ok_code:
            self.bot.send_message(
                request.user_id,
                "Произошла ошибка. Попробуйте еще раз.",
            )
            return 500

        if user is None:
            self.logger.info("User not found.", extra={"message_type": "server"})
            self.bot.send_message(
                request.user_id,
                "Произошла ошибка. Попробуйте еще раз.",
            )
            return 404

        if request.request_type == "to_text":
            code, req = self.__to_text(request, user)
        else:
            try:
                code, result_path = self.__to_note(request, user)
            except md2pdf.exceptions.ValidationError:
                self.bot.send_message(
                    request.user_id,
                    "Произошла ошибка.\n"
                    "Возможно, данная запись не содержит ценной информации.\n"
                    "Главное меню /start",
                )
                return 404

        if code == tokens_error:
            self.bot.send_message(
                request.user_id,
                "Недостаточно средств.\nКупить токены можно в меню /tokens",  # noqa: RUF001
            )
            self.logger.info(
                "Not enough tokens. User ID",
                extra={"message_type": "server"},
            )
        elif code == server_error:
            self.logger.info(
                "Error converting to mp3. User ID:",
                extra={"message_type": "server"},
            )
            self.bot.send_message(
                request.user_id,
                "Произошла ошибка. Попробуйте еще раз.",
            )
        elif code == ok_code and request.request_type == "to_note":
            with Path(f"{result_path}.md").open("rb") as md_document:
                self.bot.send_document(request.user_id, md_document)

            with Path(f"{result_path}.pdf").open("rb") as pdf_document:
                self.bot.send_document(request.user_id, pdf_document)

            self.bot.send_message(
                request.user_id,
                f"Потрачено {price} токенов\nГлавное меню /start",  # noqa: RUF001
            )

            self.database.decrease_tokens(user.id, price)
            self.logger.info("Note sent", extra={"message_type": "server"})

            Path(f"{result_path}.md").unlink()
            Path(f"{result_path}.pdf").unlink()

            return 200

        return code  # type: ignore[no-any-return]

    def __to_text(
        self: MainRoute,
        request: Request,
        user: User,
    ) -> tuple[int, Request | None]:
        """Convert voice message to text and passes it to note route.

        This method downloads the file, converts it to mp3, divides it into chunks,
        converts each chunk to text, and then sends the text to the note route.

        Args:
        ----
            request (Request): Request to process.
            user (User): User who sent the request.

        Returns:
        -------
            tuple[int, Optional[Request]]: Response code and new request to process.

        """
        s2t_token = get_token(self.s2t_auth_data, "SALUTE_SPEECH_PERS")
        ok_code = 200
        result = ""

        audio = self.bot.get_file(request.file_id)
        file_path = f"data/audio/{user.id}.ogg"
        price = self.__get_price(request.duration)

        # Check if user has enough tokens to make the request
        if price > user.tokens:
            return 403, None

        file_data: bytes = self.bot.download_file(audio.file_path)
        with Path(file_path).open("wb") as file:
            file.write(file_data)

        self.logger.info("Note downloaded.", extra={"message_type": "server"})

        # Convert to mp3
        code, new_file_path = self.audio_pocessing.convert_to_mp3(file_path)
        if code != ok_code:
            return 500, None

        # Convert to chunks
        code = self.audio_pocessing.to_chunks(new_file_path, request.user_id)
        if code != ok_code:
            return 500, None

        # Convert each chunk to text
        for filename in os.listdir(f"data/chunks/{request.user_id}"):
            code, chunk_result = speech2text(
                s2t_token,
                f"data/chunks/{request.user_id}/{filename}",
                self.logger,
            )
            if code != ok_code:
                return 500, None
            result += chunk_result

        shutil.rmtree(f"data/chunks/{request.user_id}")
        with Path(f"data/texts/{user.id}.txt").open("w") as f:
            f.write(result)
            del result

        self.logger.info("Speech to text done.", extra={"message_type": "server"})

        self.bot.send_message(
            request.user_id,
            "Получен текст.\nНачинается создание конспекта...",  # noqa: RUF001
        )

        # Create new request to note route
        new_request: Request = Request(
            user_id=request.user_id,
            request_type="to_note",
            duration=request.duration,
            file_id=f"data/texts/{user.id}.txt",
        )

        self.request_queue.put(new_request)

        return 200, None

    def __to_note(self: MainRoute, request: Request, user: User) -> tuple[int, str]:
        """Convert text to note using GigaChat's text-to-note API.

        This method opens instructions.txt, reads it, opens the text file specified in the request,
        reads it, and sends it to GigaChat's text-to-note API. If the request is successful,
        the method creates a new file with the note and deletes the text file.

        Args:
        ----
            request (Request): Request to process.
            user (User): User who sent the request.

        Returns:
        -------
            tuple[int, str]: Response code and path to the new file with the note.

        """  # noqa: E501
        t2n_token = get_token(self.t2n_auth_data, "GIGACHAT_API_PERS")
        result = ""
        ok_code = 200

        with Path("data/instructions.txt").open() as f:
            instructions = f.read()

        with Path(request.file_id).open() as f:
            text = f.read()

        text_substrings = self.split_string(text, 4096)
        messages: list[dict[str, str]] = []

        for ind, text_substring in enumerate(text_substrings):

            code, messages = text2note(
                t2n_token,
                instructions,
                self.logger,
                text_substring,
                messages=None if not ind else messages,
            )
            if code != ok_code:
                return 500, ""
            result += messages[-1]["content"]

        Path(request.file_id).unlink()
        result_path = f"data/results/{user.id}_{uuid.uuid4()}"

        with Path(f"{result_path}.md").open("w") as f:
            f.write(result)

        md2pdf.core.md2pdf(f"{result_path}.pdf", result)

        return 200, result_path
