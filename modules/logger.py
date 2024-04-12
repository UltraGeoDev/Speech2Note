import logging


class CustomLogger:
    """
    Class for creating loggers for different types of logs

    The class creates three loggers:
        - user_logger - for user-related logs
        - openai_logger - for OpenAI-related logs
        - server_logger - for server-related logs

    Each logger logs to a separate file:
        - user.log
        - openai.log
        - server.log

    Each logger has a DEBUG level and a FileHandler that appends to the corresponding file.
    """

    def __init__(self) -> None:
        """
        Initialization of loggers

        Args:
            None
        Returns:
            None
        """

        # Creating a logger for user-related logs
        self.user_logger = logging.getLogger("user")
        self.user_logger.setLevel(logging.INFO)
        user_file_handler = logging.FileHandler("logs/user.log")
        user_file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - USER - %(message)s")
        )
        self.user_logger.addHandler(user_file_handler)

        # Creating a logger for OpenAI-related logs
        self.openai_logger = logging.getLogger("openai")
        self.openai_logger.setLevel(logging.INFO)
        openai_file_handler = logging.FileHandler("logs/openai.log")
        openai_file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - OPENAI - %(message)s")
        )
        self.openai_logger.addHandler(openai_file_handler)

        # Creating a logger for server-related logs
        self.server_logger = logging.getLogger("server")
        self.server_logger.setLevel(logging.INFO)
        server_file_handler = logging.FileHandler("logs/server.log")
        server_file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - SERVER - %(message)s")
        )
        self.server_logger.addHandler(server_file_handler)

    def info(self, message: str, log_type: str) -> None:
        """
        Method for logging informational messages

        Args:
            message (str): message to log
            log_type (str): type of the log. Can be 'user', 'openai', or 'server'
        Returns:
            None
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
        Method for logging errors

        Args:
            message (str): message to log
            log_type (str): type of the log. Can be 'user', 'openai', or 'server'
        Returns:
            None
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
