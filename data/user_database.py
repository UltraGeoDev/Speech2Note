from supabase import Client, create_client
from modules.logger import CustomLogger
from typing import Optional
from modules.user import User


class UserDatabase:
    def __init__(
        self, supabase_url: str, supabase_key: str, logger: CustomLogger
    ) -> None:
        self.client: Client = create_client(supabase_url, supabase_key)
        self.logger = logger

    def new_user(self, user_id: int, username: str) -> None:
        try:
            self.client.table("users").insert(
                {"user_id": str(user_id), "name": username}
            ).execute()
        except Exception as e:
            self.logger.error(str(e), "user")

    def get_user(self, user_id: int) -> [int, Optional[User]]:
        try:
            user_data = (
                self.client.table("users")
                .select("*")
                .eq("user_id", str(user_id))
                .execute()
                .data
            )
            user = User(**user_data[0])
            return 200, user if user_data else None
        except Exception as e:
            self.logger.error(str(e), "user")
            return 400, None
