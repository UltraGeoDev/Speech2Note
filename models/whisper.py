from openai import OpenAI
from typing import Optional
from modules.logger import CustomLogger


class Speech2TextClient:

    def __init__(self, api_key: str, logger: CustomLogger) -> None:
        self.__api_key = api_key
        self.openai_client = OpenAI(api_key=self.__api_key)

        self.logger = logger
        self.logger.info("Whisper initialized.", "openai")

    def transcribe(self, file_path: str, id: str) -> tuple[int, str]:
        with open(file_path, "rb") as file:
            try:
                transcription = self.openai_client.audio.transcriptions.create(
                    model="whisper-1", file=file
                )
                self.logger.info(f"Transcription {id} done.", "openai")
            except Exception as e:
                self.logger.error(str(e), "openai")
                return 400, ""
        return 200, transcription.text
