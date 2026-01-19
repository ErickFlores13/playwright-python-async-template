"""Bearer token authentication strategy."""

import time
from typing import Dict, Optional

from playwright.async_api import APIRequestContext

from core.api.models import AuthenticationError
from utils.config import Config

from ..base import AuthStrategy


class BearerTokenAuth(AuthStrategy):
    """
    Bearer token authentication (JWT, etc.).

    Attributes:
        token: Access token string
        token_type: Type of token (default: 'Bearer')
        expires_at: Optional expiration timestamp
        playwright_context: Optional Playwright APIRequestContext for fetching token
        api_url: Optional base API URL
        auth_endpoint: Optional endpoint to fetch new token
        credentials: Optional credentials for token fetching
        token_field: Field name in response containing the token (default: 'access_token')

    Example:
    ```
        auth = BearerTokenAuth("eyJhbGci...")
        headers = await auth.get_auth_headers()
        # {'Authorization': 'Bearer eyJhbGci...'}

        # From environment variable
        import os
        auth = BearerTokenAuth.from_env("API_TOKEN")

        # With token fetching
        playwright_context = await some_function_to_get_context()
        auth = BearerTokenAuth(
            playwright_context=playwright_context,
            api_url="https://api.example.com",
            auth_endpoint="/auth/token",
            credentials={"username": "user", "password": "pass"}
        )
    ```
    """

    def __init__(
        self,
        token: Optional[str] = None,
        token_type: str = "Bearer",
        expires_at: Optional[float] = None,
        playwright_context: Optional[APIRequestContext] = None,
        api_url: Optional[str] = None,
        auth_endpoint: Optional[str] = None,
        credentials: Optional[Dict[str, str]] = None,
        token_field: str = "access_token",
    ):
        """
        Initialize Bearer token auth.

        Args:
            token: Access token (optional if using lazy token fetching)
            token_type: Token type (default: 'Bearer')
            expires_at: Optional expiration timestamp
        """
        self.token = token
        self.token_type = token_type
        self.expires_at = expires_at
        self._playwright_context = playwright_context
        self._api_url = api_url
        self._auth_endpoint = auth_endpoint
        self._credentials = credentials
        self._token_field = token_field

    async def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authorization headers. Fetch new token if expired.
        Returns:
            Dictionary with Authorization header
        """
        if self.token is None or self.is_expired:
            await self._fetch_token()

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

    async def _fetch_token(self) -> None:
        """
        Fetch a new token using the provided credentials and auth endpoint.
        Raises:
            ValueError: If required parameters are missing
            Exception: If token fetch fails
        """
        from core.api.base_client import BaseAPIClient

        if not self._playwright_context or not self._auth_endpoint or not self._credentials:
            raise ValueError(
                "Playwright context, auth endpoint, and credentials must be provided to fetch token."
            )

        http_client = BaseAPIClient(self._playwright_context, self._api_url)

        response = await http_client.post(
            self._auth_endpoint, data=self._credentials, expected_status=None
        )

        if response.is_success:
            self.token = response.get_data_field(self._token_field)
            expires_in = response.get_data_field("expires_in")
            if expires_in:
                self.expires_at = time.time() + int(expires_in)
        else:
            raise AuthenticationError(
                message="Failed to fetch bearer token",
                status_code=response.status_code,
                response_body=response.data,
                url=response.url,
                method=response.method,
            )
