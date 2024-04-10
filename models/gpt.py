from openai import OpenAI
from typing import Optional
from modules.logger import CustomLogger


class GPTClient:

    def __init__(self, api_key: str, instructions: str, logger: CustomLogger) -> None:
        self.__api_key = api_key
        self.openai_client = OpenAI(api_key=self.__api_key)
        self.instructions = instructions

        self.logger = logger
        self.logger.info("GPT initialized.", "openai")

    def process_text(self, messages: list, request_id: str) -> tuple[int, list]:

        messages.insert(0, {"role": "system", "content": self.instructions})

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4", messages=messages
            )
            self.logger.info(f"Text processed. id: {request_id}", "openai")
            return 200, response.choices
        except Exception as e:
            self.logger.error(str(e), "openai")
            return 400, []
