class Request:
    def __init__(self, request_type: str, file_path: str, user_id: int) -> None:

        if request_type not in ["to_note", "to_text"]:
            raise ValueError("Invalid request type.")

        self.__file_path = file_path
        self.__user_id = user_id
        self.__request_type = request_type

    @property
    def request_type(self) -> str:
        return self.__request_type

    @property
    def file_path(self) -> str:
        return self.__file_path

    @property
    def user_id(self) -> int:
        return self.__user_id
