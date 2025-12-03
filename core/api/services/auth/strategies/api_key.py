"""API Key authentication strategy."""

from typing import Dict

from ..base import AuthStrategy


class APIKeyAuth(AuthStrategy):
    """
    API Key authentication.

    Example:
        >>> auth = APIKeyAuth("sk_test_abc123", header_name="X-API-Key")
        >>> headers = await auth.get_auth_headers()
        >>> # {'X-API-Key': 'sk_test_abc123'}

        >>> # From environment
        >>> auth = APIKeyAuth.from_env("STRIPE_API_KEY", header_name="Authorization")
    """

    def __init__(self, api_key: str, header_name: str = "X-API-Key"):
        """
        Initialize API key auth.

        Args:
            api_key: API key value
            header_name: Header name (default: 'X-API-Key')
        """
        self.api_key = api_key
        self.header_name = header_name

    async def get_auth_headers(self) -> Dict[str, str]:
        """Get API key header."""
        return {self.header_name: self.api_key}

    @classmethod
    def from_env(cls, env_var: str = "API_KEY", header_name: str = "X-API-Key") -> "APIKeyAuth":
        """
        Create from environment variable.

        Args:
            env_var: Environment variable name (default: 'API_KEY')
            header_name: Header name (default: 'X-API-Key')

        Returns:
            APIKeyAuth instance

        Example:
            >>> # .env: STRIPE_API_KEY=sk_test_abc123
            >>> auth = APIKeyAuth.from_env("STRIPE_API_KEY", header_name="Authorization")
        """
        import os

        api_key = os.getenv(env_var)
        if not api_key:
            raise ValueError(f"Environment variable '{env_var}' not found")
        return cls(api_key, header_name)
