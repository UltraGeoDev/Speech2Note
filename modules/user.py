"""User class represents a user in our database."""

from __future__ import annotations

from datetime import datetime


class User:
    """User class represents a user in our database.

    Attributes
    ----------
        user_id (int): user id
        name (str): user name
        tokens (int): number of tokens user has
        created_at (str): date when user was created

    """

    def __init__(
        self: User,
        user_id: int,
        name: str,
        tokens: int,
        created_at: str,
    ) -> None:
        """Class constructor.

        Args:
        ----
            user_id (int): user id
            name (str): user name
            tokens (int): number of tokens user has
            created_at (str): date when user was created

        """
        self.__id = user_id
        self.__name = name
        self.__tokens = tokens
        self.__created_at = datetime.fromisoformat(created_at)

    @property
    def id(self: User) -> int:
        """Returns user id.

        Returns
        -------
            int: user id

        """
        return self.__id

    @property
    def name(self: User) -> str:
        """Returns user name.

        Returns
        -------
            str: user name

        """
        return self.__name

    @property
    def tokens(self: User) -> int:
        """Returns number of tokens user has.

        Returns
        -------
            int: number of tokens

        """
        return self.__tokens

    @property
    def created_at(self: User) -> str:
        """Returns date when user was created.

        Returns
        -------
            str: date when user was created

        """
        return datetime.strftime(self.__created_at, "%Y-%m-%d %H:%M:%S")

    def get_data(self: User) -> dict:
        """User data.

        Returns
        -------
            dict: user data

        """
        return {
            "user_id": self.id,
            "name": self.name,
            "tokens": self.tokens,
            "created_at": self.__created_at,
        }
