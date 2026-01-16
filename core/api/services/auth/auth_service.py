import logging
import time
from dataclasses import dataclass
from typing import Dict, Optional

from .base import AuthStrategy
from .strategies import APIKeyAuth, BasicAuth, BearerTokenAuth, CustomHeaderAuth

logger = logging.getLogger(__name__)


@dataclass
class TokenInfo:
    """
    Token information container for managing authentication tokens.

    Provides convenience methods for token expiration checking and header formatting.

    Attributes:
        access_token: Access token string
        token_type: Token type (e.g., 'Bearer')
        expires_at: Token expiration timestamp (Unix time)
        refresh_token: Refresh token (optional)
    """

    access_token: str
    token_type: str = "Bearer"
    expires_at: Optional[float] = None
    refresh_token: Optional[str] = None

    @property
    def is_expired(self) -> bool:
        """Check if token is expired (with 60s buffer)."""
        if self.expires_at is None:
            return False
        return time.time() >= (self.expires_at - 60)

    @property
    def authorization_header(self) -> str:
        """Get formatted authorization header value."""
        return f"{self.token_type} {self.access_token}"


class AuthService:
    """
    Primary authentication service providing convenient factory methods.

    This is the recommended way to create authentication for API clients.
    Provides a simple, discoverable API with methods for common auth types:

    - with_bearer_token() - JWT/Bearer token authentication
    - with_api_key() - API key in custom header
    - with_basic_auth() - HTTP Basic authentication
    - with_custom_headers() - Custom header authentication

    Example:
        >>> auth = AuthService.with_bearer_token("my-token")
        >>> client = UserServiceClient(context, base_url, auth_strategy=auth)
    """

    def __init__(self):
        """Initialize authentication service."""
        self._strategy: Optional[AuthStrategy] = None

    @classmethod
    def with_bearer_token_from_env(
        cls,
        api_token: Optional[str] = None,
        token_type: Optional[str] = None,
        expires_at: Optional[float] = None,
    ) -> "AuthService":
        """
        Create auth service with Bearer token from environment variables.

        Args:
            api_token: Bearer token (if None, read from API_BEARER_TOKEN env var)
            token_type: Token type (if None, defaults to 'Bearer')
            expires_at: Optional token expiration timestamp

        Returns:
            Configured AuthService instance

        Example:
            >>> # From environment
            >>> auth = AuthService.with_bearer_token_from_env()
            >>> # With explicit token
            >>> auth = AuthService.with_bearer_token_from_env("my-token")
        """
        service = cls()
        service._strategy = BearerTokenAuth.from_env(api_token, token_type)
        if expires_at:
            service._strategy.expires_at = expires_at
        return service

    @classmethod
    def with_api_key_from_env(
        cls, api_key: Optional[str] = None, header_name: Optional[str] = None
    ) -> "AuthService":
        """
        Create auth service with API key from environment variables.

        Args:
            api_key: API key (if None, read from API_KEY env var)
            header_name: Header name (if None, read from API_KEY_HEADER_NAME env var)

        Returns:
            Configured AuthService instance

        Example:
            >>> # From environment
            >>> auth = AuthService.with_api_key_from_env()
            >>> # With explicit values
            >>> auth = AuthService.with_api_key_from_env("key123", "X-API-Key")
        """
        service = cls()
        service._strategy = APIKeyAuth.from_env(api_key, header_name)
        return service

    @classmethod
    def with_basic_auth_from_env(
        cls, username: Optional[str] = None, password: Optional[str] = None
    ) -> "AuthService":
        """
        Create auth service with Basic auth from environment variables.

        Args:
            username: Username (if None, read from API_USERNAME env var)
            password: Password (if None, read from API_PASSWORD env var)

        Returns:
            Configured AuthService instance

        Example:
            >>> # From environment
            >>> auth = AuthService.with_basic_auth_from_env()
            >>> # With explicit credentials
            >>> auth = AuthService.with_basic_auth_from_env("admin", "pass123")
        """
        service = cls()
        service._strategy = BasicAuth.from_env(username, password)
        return service

    async def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        if self._strategy:
            return await self._strategy.get_auth_headers()
        return {}

    def set_token(self, token: str, expires_at: Optional[float] = None) -> None:
        """
        Update Bearer token for an existing auth service.

        Args:
            token: New token value
            expires_at: Optional new expiration timestamp
        """
        if isinstance(self._strategy, BearerTokenAuth):
            self._strategy.token = token
            if expires_at:
                self._strategy.expires_at = expires_at

    def clear_auth(self) -> None:
        """Clear all authentication from this service."""
        self._strategy = None
