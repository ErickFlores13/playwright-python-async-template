"""Bearer token authentication strategy."""

import time
from typing import Dict, Optional

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
    def from_env(cls, env_var: str = "API_TOKEN", token_type: str = "Bearer") -> "BearerTokenAuth":
        """
        Create from environment variable.

        Args:
            env_var: Environment variable name (default: 'API_TOKEN')
            token_type: Token type (default: 'Bearer')

        Returns:
            BearerTokenAuth instance

        Example:
            >>> # .env: API_TOKEN=eyJhbGci...
            >>> auth = BearerTokenAuth.from_env("API_TOKEN")
        """
        import os

        token = os.getenv(env_var)
        if not token:
            raise ValueError(f"Environment variable '{env_var}' not found")
        return cls(token, token_type)
