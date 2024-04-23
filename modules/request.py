"""Request module."""

from __future__ import annotations


class Request:
    """Class that represents a request to process a file.

    Attributes
    ----------
        request_type (str): Type of the request.
        file_id (str): ID of the file to process.
        user_id (int): ID of the user who sent the request.
        duration (int): Duration of the file in seconds.

    """

    def __init__(
        self: Request,
        request_type: str,
        file_id: str,
        file_name: str,
        user_id: int,
        duration: int,
    ) -> None:
        """Create a new request.

        Args:
        ----
            request_type (str): Type of the request.
            file_id (str): ID of the file to process.
            file_name (str): Name of the file to process.
            user_id (int): ID of the user who sent the request.
            duration (int): Duration of the file in seconds.

        Raises:
        ------
            ValueError: If the request type is invalid.

        """
        if request_type not in ["to_note", "to_text"]:
            msg = "Invalid request type."
            raise ValueError(msg)

        self.__file_id = file_id
        self.__file_name = file_name
        self.__user_id = user_id
        self.__request_type = request_type
        self.__duration = duration

    @property
    def request_type(self: Request) -> str:
        """Return the request type.

        Returns
        -------
            str: The request type.

        """
        return self.__request_type

    @property
    def file_id(self: Request) -> str:
        """Return the file ID.

        Returns
        -------
            str: The file ID.

        """
        return self.__file_id

    @property
    def file_name(self: Request) -> str:
        """Return the file name.

        Returns
        -------
            str: The file name.

        """
        return self.__file_name

    @property
    def user_id(self: Request) -> int:
        """Return the user ID.

        Returns
        -------
            int: The user ID.

        """
        return self.__user_id

    @property
    def duration(self: Request) -> int:
        """Return the duration of the file in seconds.

        Returns
        -------
            int: The duration of the file in seconds.

        """
        return self.__duration
