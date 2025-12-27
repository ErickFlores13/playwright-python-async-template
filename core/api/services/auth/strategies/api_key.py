"""API Key authentication strategy."""

from typing import Dict, Optional
from utils.config import Config
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
    def from_env(
        cls, 
        api_key: Optional[str] = None, 
        header_name: Optional[str] = None,
        ) -> "APIKeyAuth":
        """
        Create APIKeyAuth from environment variables.

        Args:
            api_key: API key value (if None, read from config)
            header_name: Header name (if None, read from config)
            
        Returns:
            APIKeyAuth instance
        """
        api_key = api_key or Config.get_api_key()
        header_name = header_name or Config.get_api_key_header_name()

        if not api_key:
            raise ValueError(f"API key not found")
        if not header_name:
            raise ValueError(f"API key header name not found")

        return cls(api_key, header_name)
