import time
from modules.request import Request
from modules.logger import CustomLogger
from typing import Callable


class Queue:
    def __init__(
        self, timeout: int, logger: CustomLogger, processing_function: Callable
    ) -> None:
        self.__queue: list[Request] = []
        self.__timeout = timeout
        self.__logger = logger
        self.__processing_function = processing_function

    def user_in_queue(self, user_id: int, request_type: str) -> bool:
        for item in self.__queue:
            if item.user_id == user_id and item.request_type == request_type:
                return True
        return False

    def put(self, item: Request) -> None:
        self.__queue.append(item)
        self.__logger.info(f"Request {item.request_type} added to queue.", "server")

    def get(self) -> Request:
        item = self.__queue.pop(0)
        self.__logger.info(f"Request {item.request_type} removed from queue.", "server")
        return item

    def __len__(self) -> int:
        length = len(self.__queue)
        return length

    def run(self) -> None:
        while True:
            if self.__queue:
                item = self.get()
                self.__processing_function(item)
                self.__logger.info(f"Request {item.request_type} processed.", "server")
            time.sleep(self.__timeout)

    @property
    def processing_function(self) -> Callable:
        return self.__processing_function

    @processing_function.setter
    def processing_function(self, processing_function: Callable) -> None:
        self.__processing_function = processing_function
