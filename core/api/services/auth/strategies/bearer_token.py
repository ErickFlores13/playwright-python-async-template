"""Bearer token authentication strategy."""

import time
from typing import Dict, Optional

from utils.config import Config

from ..base import AuthStrategy


class BearerTokenAuth(AuthStrategy):
    """
    Bearer token authentication (JWT, etc.).

    Example:
        >>> auth = BearerTokenAuth("eyJhbGci...")
        >>> headers = await auth.get_auth_headers()
        >>> # {'Authorization': 'Bearer eyJhbGci...'}

        >>> # From environment variable
        >>> import os
        >>> auth = BearerTokenAuth.from_env("API_TOKEN")
    """

    def __init__(self, token: str, token_type: str = "Bearer", expires_at: Optional[float] = None):
        """
        Initialize Bearer token auth.

        Args:
            token: Access token
            token_type: Token type (default: 'Bearer')
            expires_at: Optional expiration timestamp
        """
        self.token = token
        self.token_type = token_type
        self.expires_at = expires_at

    async def get_auth_headers(self) -> Dict[str, str]:
        """Get Authorization header with Bearer token."""
        return {"Authorization": f"{self.token_type} {self.token}"}

    @property
    def is_expired(self) -> bool:
        """Check if token is expired (with 60s buffer)."""
        if self.expires_at is None:
            return False
        return time.time() >= (self.expires_at - 60)

    @classmethod
    def from_env(
        cls,
        api_token: Optional[str] = None,
        token_type: Optional[str] = None,
    ) -> "BearerTokenAuth":
        """
        Create BearerTokenAuth from environment variables.

        Args:
            api_token: API token value (if None, read from config)
            token_type: Token type (if None, defaults to 'Bearer')

        Returns:
            BearerTokenAuth instance
        """
        token = api_token or Config.get_api_bearer_token()
        token_type = token_type or "Bearer"

        if not token:
            raise ValueError("API token not provided in environment")

        return cls(token, token_type)
