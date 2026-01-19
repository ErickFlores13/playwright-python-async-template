"""Custom header authentication strategy."""

import logging
from typing import Dict

from ..base import AuthStrategy

logger = logging.getLogger(__name__)


class CustomHeaderAuth(AuthStrategy):
    """
    Custom header authentication.

    For non-standard auth headers or multiple custom headers.

    Example:
        >>> auth = CustomHeaderAuth({
        ...     'X-Custom-Auth': 'secret-value',
        ...     'X-User-ID': '12345'
        ... })
        >>> headers = await auth.get_auth_headers()
        >>> # {'X-Custom-Auth': 'secret-value', 'X-User-ID': '12345'}

        >>> # From environment
        >>> auth = CustomHeaderAuth.from_env({
        ...     'X-API-Key': 'API_KEY_ENV_VAR',
        ...     'X-User-ID': 'USER_ID_ENV_VAR'
        ... })
    """

    def __init__(self, headers: Dict[str, str]):
        """
        Initialize custom header auth.

        Args:
            headers: Dict of custom headers
        """
        self.headers = headers

    async def get_auth_headers(self) -> Dict[str, str]:
        """Get custom headers."""
        return self.headers.copy()

    @classmethod
    def from_env(cls, header_env_mapping: Dict[str, str]) -> "CustomHeaderAuth":
        """
        Create from environment variables.

        Args:
            header_env_mapping: Dict mapping header names to env var names

        Returns:
            CustomHeaderAuth instance

        Example:
            >>> # .env: MY_API_KEY=secret123, USER_ID=789
            >>> auth = CustomHeaderAuth.from_env({
            ...     'X-API-Key': 'MY_API_KEY',
            ...     'X-User-ID': 'USER_ID'
            ... })
        """
        import os

        headers = {}

        for header_name, env_var in header_env_mapping.items():
            value = os.getenv(env_var)
            if value:
                headers[header_name] = value
            else:
                logger.warning(
                    f"Environment variable '{env_var}' not found for header '{header_name}'"
                )

        return cls(headers)
