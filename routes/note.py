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
        split_timeout: int,
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
        self.audio_pocessing = AudioProcessing(
            splt_timeout=split_timeout,
            logger=logger,
        )

        @bot.message_handler(content_types=["voice", "audio", "document"])
        def note(message: telebot.types.Message) -> None:  # type: ignore[no-any-unimported]
            """Voice messages and sends them to the queue."""
            self.__note(message)

        self.logger.info("Main route initialized.", extra={"message_type": "server"})

    @staticmethod
    def __get_price(duration: int) -> int:  # noqa: PLR0911
        """Calculate price for note based on duration."""
        levels = [1, 5, 10, 20, 40, 60]

        if duration < levels[0]:
            return 1
        if duration < levels[1]:
            return 5
        if duration < levels[2]:
            return 10
        if duration < levels[3]:
            return 15
        if duration < levels[4]:
            return 25
        if duration > levels[5]:
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
        result = []
        for i in range(0, len(string), length):
            result.append(string[i : i + length])  # noqa: PERF401
        return result

    def __note(self: MainRoute, message: telebot.types.Message) -> int:  # type: ignore[no-any-unimported]
        """Process audio in chat and send request to the queue.

        Return 200 if successful.
        Return 500 if error.
        Return 404 if user not found or user already in queue or queue is full.
        """
        user_id = message.chat.id

        # get message data
        if message.voice is not None:
            audio_message = message.voice
            file_name = str(message.chat.id) + ".ogg"
            duration = audio_message.duration // 60
            file_id = audio_message.file_id
        elif message.audio is not None:
            audio_message = message.audio
            file_name = str(message.chat.id) + Path(audio_message.file_name).suffix
            duration = audio_message.duration // 60
            file_id = audio_message.file_id
        elif message.document is not None:
            file_name = str(message.chat.id) + Path(message.document.file_name).suffix
            file_info = self.bot.get_file(message.document.file_id)
            file_data = self.bot.download_file(file_info.file_path)

            duration = self.audio_pocessing.get_audio_duration(file_name, file_data)
            file_id = message.document.file_id

        if duration is None:
            self.bot.send_message(
                message.chat.id,
                "Извини, но я не понимаю, что делать c этим сообщением.\n"
                "Возможно, формат этого сообщения пока не поддерживается.\n"
                "Главное меню: /start",
            )
            self.logger.info(
                "Failed to recognize audio message.",
                extra={"message_type": "server"},
            )
            return 500

        # get queue length
        queue_len = len(self.request_queue)

        # waiting time
        time = queue_len * self.request_queue.timeout * queue_len // 60
        str_time = "<1 минуты" if time == 0 else f"{time} минут"

        to_text_request = Request(
            request_type="to_text",
            file_id=str(file_id),
            file_name=file_name,
            user_id=message.from_user.id,
            duration=duration,
        )

        if (
            self.request_queue.user_in_queue(user_id, "to_text")
            or Path(f"data/chunks/{user_id}").exists()
        ):
            self.bot.send_message(
                user_id,
                "Извините, вы уже в очереди.\nПoжaлyйcтa, подождите.\nГлaвнoe меню /start",  # noqa: E501
            )
            self.logger.info("User already in queue.", extra={"message_type": "server"})
            return 404

        code = self.request_queue.put(to_text_request)
        if not code:
            self.bot.send_message(
                user_id,
                "Извините, очередь переполнена.\nПoжaлyйcтa, подождите.\nГлaвнoe меню /start",  # noqa: E501
            )
            self.logger.info("Queue is full.", extra={"message_type": "server"})
            return 404

        self.bot.send_message(
            user_id,
            f"Вы добавлены в очередь. Запрос обрабатывается. Пожалуйста, подождите.\nПpимepнoe время ожидания: {str_time}",  # noqa: E501
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
                "K сожалению, аудио слишком длинное.\n"
                "Длина записи должна быть не больше часа.\n"
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
                "Недостаточно средств.\nKyпить токены можно в меню /tokens",
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
                f"Потрачено {price} токенов\nГлaвнoe меню /start",
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
        file_path = f"data/audio/{request.file_name}"
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
            "Получен текст.\nHaчинaeтcя создание конспекта...",
        )

        # Create new request to note route
        new_request: Request = Request(
            user_id=request.user_id,
            request_type="to_note",
            file_name=f"data/texts/{user.id}.txt",
            duration=request.duration,
            file_id="",
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

        with Path(request.file_name).open() as f:
            text = f.read()

        text_substrings = self.split_string(text, 4096)
        for text_substring in text_substrings:

            code, ans = text2note(
                t2n_token,
                instructions,
                self.logger,
                text_substring,
            )
            if code != ok_code:
                return 500, ""
            result += ans

        Path(request.file_name).unlink()
        result_path = f"data/results/{user.id}_{uuid.uuid4()}"

        with Path(f"{result_path}.md").open("w") as f:
            f.write(result)

        md2pdf.core.md2pdf(f"{result_path}.pdf", result)

        return 200, result_path
