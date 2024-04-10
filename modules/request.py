class Request:
    def __init__(self, request_type: str, request_data: str) -> None:
        self.__request_data = request_data
        self.__request_type = request_type

    @property
    def request_type(self) -> str:
        return self.__request_type

    @property
    def request_data(self) -> str:
        return self.__request_data

    @property
    def request(self) -> tuple[str, str]:
        return self.__request_type, self.__request_data
