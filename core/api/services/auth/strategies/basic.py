import base64
from typing import Dict

from ..base import AuthStrategy


class BasicAuth(AuthStrategy):
    """
    Basic authentication (username:password).

    Example:
        >>> auth = BasicAuth("admin", "password123")
        >>> headers = await auth.get_auth_headers()
        >>> # {'Authorization': 'Basic YWRtaW46cGFzc3dvcmQxMjM='}

        >>> # From environment
        >>> auth = BasicAuth.from_env()  # Uses TEST_USERNAME, TEST_PASSWORD
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
        cls, username_var: str = "TEST_USERNAME", password_var: str = "TEST_PASSWORD"
    ) -> "BasicAuth":
        """
        Create from environment variables.

        Args:
            username_var: Username env var (default: 'TEST_USERNAME')
            password_var: Password env var (default: 'TEST_PASSWORD')

        Returns:
            BasicAuth instance

        Example:
            >>> # .env: TEST_USERNAME=admin, TEST_PASSWORD=secret
            >>> auth = BasicAuth.from_env()
        """
        import os

        username = os.getenv(username_var)
        password = os.getenv(password_var)

        if not username or not password:
            raise ValueError(
                f"Environment variables '{username_var}' and '{password_var}' are required"
            )

        return cls(username, password)
