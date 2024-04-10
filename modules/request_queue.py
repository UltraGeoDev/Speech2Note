import threading
import time
from modules.request import Request
from modules.logger import CustomLogger
from typing import Callable


class Queue:
    def __init__(
        self, timeout: int, logger: CustomLogger, processing_function: Callable
    ) -> None:
        self.__queue: list[Request] = []
        self.__lock = threading.Lock()
        self.__timeout = timeout
        self.__logger = logger
        self.__processing_function = processing_function

    def put(self, item: Request) -> None:
        self.__lock.acquire()
        self.__queue.append(item)
        self.__lock.release()
        self.__logger.info(f"Request {item.request_type} added to queue.", "server")

    def get(self) -> Request:
        self.__lock.acquire()
        item = self.__queue.pop(0)
        self.__lock.release()
        self.__logger.info(f"Request {item.request_type} removed from queue.", "server")
        return item

    def run(self) -> None:
        queue_thread = threading.Thread(target=self.__run)

    def __len__(self) -> int:
        self.__lock.acquire()
        length = len(self.__queue)
        self.__lock.release()
        return length

    def __run(self) -> None:
        while True:
            self.__lock.acquire()
            if self.__queue:
                item = self.get()
                self.__lock.release()
                self.__processing_function(item)
                self.__logger.info(f"Request {item.request_type} processed.", "server")
            else:
                self.__lock.release()
            time.sleep(self.__timeout)
