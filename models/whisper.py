from openai import OpenAI
from typing import Optional
from modules.logger import CustomLogger

class Speech2TextClient:

    INSTANCE = None

    def __new__(cls, *args, **kwargs):
        if cls.INSTANCE is None:
            cls.INSTANCE = object.__new__(cls)
        return cls.INSTANCE

    def __init__(self, api_key: str, logger: Optional[CustomLogger]=None) -> None:
        self.__api_key = api_key
        self.openai_client = OpenAI(api_key=self.__api_key)

        if logger is not None:
            self.logger = logger
            self.logger.info("Whisper initialized.", "openai")

    def transcribe(self, file_path: str, id: str) -> str:
        with open(file_path, "rb") as file:
            transcription = self.openai_client.audio.transcriptions.create(
                model="whisper-1", 
                file=file
            )
            if self.logger is not None:
                self.logger.info(f"Transcription {id} done.", "openai")
        return transcription.text