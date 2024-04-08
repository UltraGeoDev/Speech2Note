from openai import OpenAI
from typing import Optional
from modules.logger import CustomLogger

class GPTClient:

    INSTANCE = None

    def __new__(cls, *args, **kwargs):
        if cls.INSTANCE is None:
            cls.INSTANCE = object.__new__(cls)
        return cls.INSTANCE

    def __init__(self, api_key: str, instructions: str, logger: Optional[CustomLogger]=None) -> None:
        self.__api_key = api_key
        self.openai_client = OpenAI(api_key=self.__api_key)
        self.instructions = instructions

        if logger is not None:
            self.logger = logger
            self.logger.info("GPT initialized.", "openai")

    def process_text(self, messages: list, request_id: str) -> list:

        messages.insert(0, {"role": "system", "content": self.instructions})

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        if self.logger is not None:
            self.logger.info(f"Text processed. id: {request_id}", "openai")
        return response.choices
    

instance = GPTClient("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", "")

messages=[
    {"role":""}
]