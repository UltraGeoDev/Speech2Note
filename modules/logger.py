import logging


class CustomLogger:
    """
    Класс для создания логгеров для различных типов логов
    """

    def __init__(self) -> None:
        """
        Инициализация логгеров
        args: None
        returns: None
        """

        # Создание логгера для пользовательских логов
        self.user_logger = logging.getLogger("user")
        self.user_logger.setLevel(logging.INFO)
        user_file_handler = logging.FileHandler("logs/user.log")
        user_file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - USER - %(message)s")
        )
        self.user_logger.addHandler(user_file_handler)

        # Создание логгера для логов OpenAI
        self.openai_logger = logging.getLogger("openai")
        self.openai_logger.setLevel(logging.INFO)
        openai_file_handler = logging.FileHandler("logs/openai.log")
        openai_file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - OPENAI - %(message)s")
        )
        self.openai_logger.addHandler(openai_file_handler)

        # Создание логгера для серверных логов
        self.server_logger = logging.getLogger("server")
        self.server_logger.setLevel(logging.INFO)
        server_file_handler = logging.FileHandler("logs/server.log")
        server_file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - SERVER - %(message)s")
        )
        self.server_logger.addHandler(server_file_handler)

    def info(self, message: str, log_type: str) -> None:
        """
        Метод для логгирования информационных сообщений
        args: message (str), log_type (str)
        returns: None
        """

        if log_type == "user":
            self.user_logger.info(message)
        elif log_type == "openai":
            self.openai_logger.info(message)
        elif log_type == "server":
            self.server_logger.info(message)
        else:
            raise ValueError(
                "Invalid log type. Please use 'user', 'openai', or 'server'."
            )

    def error(self, message: str, log_type: str) -> None:
        """
        Метод для логгирования ошибок
        args: message (str), log_type (str)
        returns: None
        """

        if log_type == "user":
            self.user_logger.error(message)
        elif log_type == "openai":
            self.openai_logger.error(message)
        elif log_type == "server":
            self.server_logger.error(message)
        else:
            raise ValueError(
                "Invalid log type. Please use 'user', 'openai', or 'server'."
            )
