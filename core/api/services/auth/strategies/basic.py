import base64
from typing import Dict, Optional

from utils.config import Config

from ..base import AuthStrategy


class BasicAuth(AuthStrategy):
    """
    Basic authentication (username:password).

    Example:
        >>> auth = BasicAuth("admin", "password123")
        >>> headers = await auth.get_auth_headers()
        >>> # {'Authorization': 'Basic YWRtaW46cGFzc3dvcmQxMjM='}

        >>> # From environment
        >>> auth = BasicAuth.from_env()
    """

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    async def get_auth_headers(self) -> Dict[str, str]:
        """Get Authorization header with Basic auth."""
        credentials = f"{self.username}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}

    @classmethod
    def from_env(
        cls,
        api_username: Optional[str] = None,
        password_username: Optional[str] = None,
    ) -> "BasicAuth":
        """
        Create BasicAuth from environment variables.

        Args:
            api_username: Username (if None, read from config)
            password_username: Password (if None, read from config)

        Returns:
            BasicAuth instance
        """
        username = api_username or Config.get_api_username()
        password = password_username or Config.get_api_password()

        if not username or not password:
            raise ValueError("Username or password not provided in environment")

        return cls(username, password)
