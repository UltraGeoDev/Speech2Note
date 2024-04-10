from datetime import datetime


class User:
    def __init__(self, user_id: int, name: str, tokens: int, created_at: str) -> None:
        self.__id = user_id
        self.__name = name
        self.__tokens = tokens
        self.__created_at = datetime.fromisoformat(created_at)

    @property
    def id(self) -> int:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def tokens(self) -> int:
        return self.__tokens

    @property
    def created_at(self) -> str:
        return datetime.strftime(self.__created_at, "%Y-%m-%d %H:%M:%S")

    def get_data(self) -> dict:
        return {
            "user_id": self.id,
            "name": self.name,
            "tokens": self.tokens,
            "created_at": self.__created_at,
        }
