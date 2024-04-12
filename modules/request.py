class Request:
    def __init__(
        self, request_type: str, file_id: str, user_id: int, duration: int
    ) -> None:

        if request_type not in ["to_note", "to_text"]:
            raise ValueError("Invalid request type.")

        self.__file_id = file_id
        self.__user_id = user_id
        self.__request_type = request_type
        self.__duration = duration

    @property
    def request_type(self) -> str:
        return self.__request_type

    @property
    def file_id(self) -> str:
        return self.__file_id

    @property
    def user_id(self) -> int:
        return self.__user_id

    @property
    def duration(self) -> int:
        return self.__duration
