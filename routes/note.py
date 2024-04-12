"""
Main route for bot.

Handles voice messages and processes requests.
"""

import telebot  # type: ignore
from modules.logger import CustomLogger
from data.user_database import UserDatabase

from modules.request import Request
from modules.audio_pocessing import AudioProcessing
from modules.request_queue import Queue
from modules.user import User

from model.oauth import get_token
from model.speech import speech2text
from model.text import text2note

from typing import Optional
import os, shutil
import uuid
import md2pdf  # type: ignore


class MainRoute:
    """
    Class for handling voice messages and processing requests.
    """

    def __init__(  # type: ignore
        self,
        bot: telebot.TeleBot,
        s2t_auth_data: str,
        t2n_auth_data: str,
        user_database: UserDatabase,
        logger: CustomLogger,
        request_queue: Queue,
    ) -> None:
        """
        Initializes MainRoute.
        """
        self.bot = bot
        self.logger = logger
        self.database = user_database
        self.s2t_auth_data = s2t_auth_data
        self.t2n_auth_data = t2n_auth_data
        self.request_queue = request_queue
        self.audio_pocessing = AudioProcessing(logger)

        @bot.message_handler(content_types=["voice"])
        def note(message: telebot.types.Message) -> None:  # type: ignore
            """
            Handles voice messages and sends them to the queue.
            """
            self.__note(message)

        self.logger.info("Main route initialized.", "server")

    @staticmethod
    def __get_price(duration: int) -> int:
        """
        Calculates price for note based on duration.
        """
        if duration < 1:
            return 1
        if duration < 5:
            return 5
        if duration < 10:
            return 10
        if duration < 20:
            return 15
        if duration < 40:
            return 25
        return 50

    @staticmethod
    def split_string(string: str, length: int) -> list[str]:
        return [string[i : i + length] for i in range(0, len(string), length)]

    def __note(self, message: telebot.types.Message) -> int:  # type: ignore
        """
        Process audio in chat and send request to the queue.
        Return 200 if successful.
        Return 500 if error.
        Return 404 if user not found or user already in queue.
        """

        voice_message: telebot.types.Voice = message.voice  # type: ignore
        user_id = message.chat.id

        # get duration for note
        duration = voice_message.duration // 60

        # get queue length
        queue_len = len(self.request_queue)

        # waiting time
        time = queue_len * self.request_queue.timeout * queue_len // 60
        str_time = "<1 минуты" if time == 0 else f"{time} минут"

        to_text_request = Request(
            "to_text", str(voice_message.file_id), message.from_user.id, duration
        )

        if self.request_queue.user_in_queue(user_id, "to_text") or os.path.exists(
            f"data/chunks/{user_id}"
        ):
            self.bot.send_message(
                user_id,
                "Извините, вы уже в очереди.\nПожалуйста, подождите.\nГлавное меню /start",
            )
            self.logger.info("User already in queue.", "server")
            return 404

        self.request_queue.put(to_text_request)
        self.bot.send_message(
            user_id,
            f"Вы добавлены в очередь. Запрос обрабатывается. Пожалуйста, подождите.\nПримерное время ожидания: {str_time} минут",
        )

        return 200

    def process_request(self, request: Request) -> int:  # type: ignore
        """
        Process request and return response.

        This method checks if the user with the specified ID exists in the database.
        If the user does not exist, the method sends an error message to the user and returns 404.

        If the user exists, the method checks if the user has enough tokens to make the request.
        If the user does not have enough tokens, the method sends an error message to the user and returns 403.

        If the user has enough tokens, the method processes the request. If an error occurs during
        the processing, the method sends an error message to the user and returns 500.

        If the request is successful, the method sends the document to the user and updates the user's tokens.
        The method then returns 200.

        Args:
            request (Request): Request to process.

        Returns:
            int: Response code.
        """

        code, user = self.database.get_user(request.user_id)
        price = self.__get_price(request.duration)

        if code != 200:
            self.bot.send_message(
                request.user_id, "Произошла ошибка. Попробуйте еще раз."
            )
            return 500

        if user is None:
            self.logger.info(f"User not found. User ID: {request.user_id}.", "server")
            self.bot.send_message(
                request.user_id, "Произошла ошибка. Попробуйте еще раз."
            )
            return 404

        if request.request_type == "to_text":
            code, req = self.__to_text(request, user)
        else:
            code, result_path = self.__to_note(request, user)

        if code == 403:
            self.bot.send_message(
                request.user_id, "Недостаточно средств. Попробуйте еще раз."
            )
            self.logger.info(
                f"Not enough tokens. User ID: {request.user_id}.", "server"
            )
        elif code == 500:
            self.logger.info(
                f"Error converting to mp3. User ID: {request.user_id}.",
                "server",
            )
            self.bot.send_message(
                request.user_id, "Произошла ошибка. Попробуйте еще раз."
            )
        elif code == 200 and request.request_type == "to_note":
            md_document = open(f"{result_path}.md", "rb")
            pdf_document = open(f"{result_path}.pdf", "rb")

            self.bot.send_document(request.user_id, md_document)
            self.bot.send_document(request.user_id, pdf_document)

            self.bot.send_message(
                request.user_id, f"Потрачено {price} токенов\nГлавное меню /start"
            )

            self.database.decrease_tokens(user.id, price)
            self.logger.info(f"Note sent. User ID: {request.user_id}.", "server")

            os.remove(f"{result_path}.md")
            os.remove(f"{result_path}.pdf")

            return 200

        return code  # type: ignore

    def __to_text(self, request: Request, user: User) -> tuple[int, Optional[Request]]:
        """
        Converts voice message to text and passes it to note route.

        This method downloads the file, converts it to mp3, divides it into chunks,
        converts each chunk to text, and then sends the text to the note route.

        Args:
            request (Request): Request to process.
            user (User): User who sent the request.

        Returns:
            tuple[int, Optional[Request]]: Response code and new request to process.
        """
        s2t_token = get_token(self.s2t_auth_data, "SALUTE_SPEECH_PERS")
        result = ""

        audio = self.bot.get_file(request.file_id)
        file_path = f"data/audio/{user.id}.ogg"
        price = self.__get_price(request.duration)

        # Check if user has enough tokens to make the request
        if price > user.tokens:
            return 403, None

        file_data: bytes = self.bot.download_file(audio.file_path)
        with open(file_path, "wb") as file:
            file.write(file_data)

        self.logger.info(f"Note downloaded. User ID: {request.user_id}.", "server")

        # Convert to mp3
        code, new_file_path = self.audio_pocessing.convert_to_mp3(file_path)
        if code != 200:
            return 500, None

        # Convert to chunks
        code = self.audio_pocessing.to_chunks(new_file_path, request.user_id)
        if code != 200:
            return 500, None

        # Convert each chunk to text
        for filename in os.listdir(f"data/chunks/{request.user_id}"):
            code, chunk_result = speech2text(
                s2t_token, f"data/chunks/{request.user_id}/{filename}", self.logger
            )
            if code != 200:
                return 500, None
            result += chunk_result

        shutil.rmtree(f"data/chunks/{request.user_id}")
        with open(f"data/texts/{user.id}.txt", "w") as f:
            f.write(result)
            del result

        self.logger.info(f"Speech to text done. User ID: {request.user_id}.", "server")

        self.bot.send_message(
            request.user_id, "Получен текст.\nНачинается создание конспекта..."
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

    def __to_note(self, request: Request, user: User) -> tuple[int, str]:
        """
        Converts text to note using GigaChat's text-to-note API.

        This method opens instructions.txt, reads it, opens the text file specified in the request,
        reads it, and sends it to GigaChat's text-to-note API. If the request is successful,
        the method creates a new file with the note and deletes the text file.

        Args:
            request (Request): Request to process.
            user (User): User who sent the request.

        Returns:
            tuple[int, str]: Response code and path to the new file with the note.
        """

        t2n_token = get_token(self.t2n_auth_data, "GIGACHAT_API_PERS")
        result = ""

        with open("data/instructions.txt", "r") as f:
            instructions = f.read()

        with open(request.file_id, "r") as f:
            text = f.read()

        text_substrings = self.split_string(text, 4096)

        for text_substring in text_substrings:
            code, result_substring = text2note(
                t2n_token, text_substring, instructions, self.logger
            )
            if code != 200:
                return 500, ""
            result += result_substring

        os.remove(request.file_id)
        result_path = f"data/results/{user.id}_{uuid.uuid4()}"

        with open(f"{result_path}.md", "w") as f:
            f.write(result)

        md2pdf.core.md2pdf(f"{result_path}.pdf", result)

        return 200, result_path
