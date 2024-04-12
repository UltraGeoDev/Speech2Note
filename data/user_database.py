from supabase import Client, create_client
from modules.logger import CustomLogger
from typing import Optional
from modules.user import User


class UserDatabase:
    """Class for interacting with the user database.

    Attributes:
        client (supabase.Client): The Supabase client for the database.
        logger (modules.logger.CustomLogger): The logger for the bot.
    """

    def __init__(
        self, supabase_url: str, supabase_key: str, logger: CustomLogger
    ) -> None:
        """Create a new UserDatabase instance.

        Args:
            supabase_url (str): The URL of the Supabase database.
            supabase_key (str): The API key of the Supabase database.
            logger (modules.logger.CustomLogger): The logger for the bot.
        """
        self.client: Client = create_client(supabase_url, supabase_key)
        self.logger = logger

    def new_user(self, user_id: int, username: str) -> None:
        """Insert a new user into the database.

        Args:
            user_id (int): The ID of the user.
            username (str): The name of the user.
        """
        try:
            self.client.table("users").insert(
                {"user_id": str(user_id), "name": username}
            ).execute()
        except Exception as e:
            self.logger.error(str(e), "user")

    def get_user(self, user_id: int) -> [int, Optional[User]]:
        """Get a user from the database.

        Args:
            user_id (int): The ID of the user.

        Returns:
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
            return 200, user
        except Exception as e:
            self.logger.error(str(e), "user")
            return 400, None

    def increase_tokens(self, user_id: int, tokens: int) -> int:
        """Increase the tokens of a user.

        Args:
            user_id (int): The ID of the user.
            tokens (int): The amount of tokens to increase by.

        Returns:
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
                "user_id", str(user_id)
            ).execute()
            return 200
        except Exception as e:
            self.logger.error(str(e), "user")
            return 400

    def decrease_tokens(self, user_id: int, tokens: int) -> int:
        """Decrease the tokens of a user.

        Args:
            user_id (int): The ID of the user.
            tokens (int): The amount of tokens to decrease by.

        Returns:
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
                "user_id", str(user_id)
            ).execute()
            return 200
        except Exception as e:
            self.logger.error(str(e), "user")
            return 400
