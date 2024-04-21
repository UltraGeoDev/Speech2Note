"""User database module."""

from __future__ import annotations

from typing import TYPE_CHECKING

from supabase import Client, create_client  # type: ignore[import-untyped]

from modules.user import User

if TYPE_CHECKING:
    from logging import Logger


class UserDatabase:
    """Class for interacting with the user database.

    Attributes
    ----------
        client (supabase.Client): The Supabase client for the database.
        logger (modules.logger.CustomLogger): The logger for the bot.

    """

    def __init__(
        self: UserDatabase,
        supabase_url: str,
        supabase_key: str,
        logger: Logger,
    ) -> None:
        """Create a new UserDatabase instance.

        Args:
        ----
            supabase_url (str): The URL of the Supabase database.
            supabase_key (str): The API key of the Supabase database.
            logger (modules.logger.CustomLogger): The logger for the bot.

        """
        self.client: Client = create_client(supabase_url, supabase_key)  # type: ignore[no-any-unimported]
        self.logger = logger

    def new_user(self: UserDatabase, user_id: int, username: str | None) -> None:
        """Insert a new user into the database.

        Args:
        ----
            user_id (int): The ID of the user.
            username (str): The name of the user.

        """
        try:
            self.client.table("users").insert(
                {
                    "user_id": str(user_id),
                    "name": username if username is not None else "unknown user",
                },
            ).execute()
        except Exception as e:
            self.logger.exception(str(e), "user")  # noqa: TRY401

    def get_user(self: UserDatabase, user_id: int) -> [int, User | None]:
        """Get a user from the database.

        Args:
        ----
            user_id (int): The ID of the user.

        Returns:
        -------
            (int, Optional[User]): The status code and the user if found, else None.

        """
        try:
            user_data = (
                self.client.table("users")
                .select("*")
                .eq("user_id", str(user_id))
                .execute()
                .data
            )
            user = User(**user_data[0]) if user_data else None
        except Exception:
            self.logger.exception("Error in get_user", extra={"message_type": "user"})
            return 400, None
        else:
            return 200, user

    def increase_tokens(self: UserDatabase, user_id: int, tokens: int) -> int:
        """Increase the tokens of a user.

        Args:
        ----
            user_id (int): The ID of the user.
            tokens (int): The amount of tokens to increase by.

        Returns:
        -------
            int: The status code.

        """
        try:
            current_tokens = (
                self.client.table("users")
                .select("tokens")
                .eq("user_id", str(user_id))
                .execute()
            ).data[0]["tokens"]
            self.client.table("users").update({"tokens": current_tokens + tokens}).eq(
                "user_id",
                str(user_id),
            ).execute()
        except Exception:
            self.logger.exception(
                "Error in increase_tokens",
                extra={"message_type": "user"},
            )
            return 400
        else:
            return 200

    def decrease_tokens(self: UserDatabase, user_id: int, tokens: int) -> int:
        """Decrease the tokens of a user.

        Args:
        ----
            user_id (int): The ID of the user.
            tokens (int): The amount of tokens to decrease by.

        Returns:
        -------
            int: The status code.

        """
        try:
            current_tokens = (
                self.client.table("users")
                .select("tokens")
                .eq("user_id", str(user_id))
                .execute()
            ).data[0]["tokens"]
            self.client.table("users").update({"tokens": current_tokens - tokens}).eq(
                "user_id",
                str(user_id),
            ).execute()
        except Exception:
            self.logger.exception(
                "Error in decrease_tokens",
                extra={"message_type": "user"},
            )
            return 400
        else:
            return 200
