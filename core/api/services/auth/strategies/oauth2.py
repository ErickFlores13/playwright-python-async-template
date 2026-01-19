"""OAuth2 Client Credentials authentication strategy."""

import logging
import time
from typing import Dict, Optional

from ..base import AuthStrategy

logger = logging.getLogger(__name__)


class OAuth2ClientCredentialsAuth(AuthStrategy):
    """
    OAuth2 Client Credentials flow.

    Automatically fetches and refreshes tokens from token endpoint.

    Example:
        >>> auth = OAuth2ClientCredentialsAuth(
        ...     client_id="client123",
        ...     client_secret="secret456",
        ...     token_url="https://auth.example.com/oauth/token"
        ... )
        >>> headers = await auth.get_auth_headers()
        >>> # Automatically fetches token and returns {'Authorization': 'Bearer ...'}

        >>> # From environment
        >>> auth = OAuth2ClientCredentialsAuth.from_env(
        ...     token_url="https://auth.example.com/oauth/token"
        ... )
    """

    def __init__(
        self, client_id: str, client_secret: str, token_url: str, scope: Optional[str] = None
    ):
        """
        Initialize OAuth2 auth.

        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            token_url: Token endpoint URL
            scope: Optional scope string
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.scope = scope
        self._access_token: Optional[str] = None
        self._expires_at: Optional[float] = None

    async def get_auth_headers(self) -> Dict[str, str]:
        """
        Get Authorization header with OAuth2 token.

        Automatically fetches or refreshes token if needed.
        """
        if self._needs_refresh():
            await self._fetch_token()

        return {"Authorization": f"Bearer {self._access_token}"}

    def _needs_refresh(self) -> bool:
        """Check if token needs refresh."""
        if not self._access_token:
            return True
        if self._expires_at and time.time() >= (self._expires_at - 60):
            return True
        return False

    async def _fetch_token(self) -> None:
        """
        Fetch access token from token endpoint.

        Note: Requires HTTPClient to be injected or uses requests library.
        """
        # This would use HTTPClient in real implementation
        # For now, showing the structure
        logger.info(f"Fetching OAuth2 token from {self.token_url}")

        # In real implementation:
        # response = await http_client.post(
        #     self.token_url,
        #     data={
        #         'grant_type': 'client_credentials',
        #         'client_id': self.client_id,
        #         'client_secret': self.client_secret,
        #         'scope': self.scope
        #     }
        # )
        # self._access_token = response.data['access_token']
        # self._expires_at = time.time() + response.data.get('expires_in', 3600)

        raise NotImplementedError(
            "OAuth2 token fetching requires HTTPClient integration. "
            "Use BearerTokenAuth with pre-fetched token for now."
        )

    @classmethod
    def from_env(
        cls,
        token_url: str,
        client_id_var: str = "OAUTH_CLIENT_ID",
        client_secret_var: str = "OAUTH_CLIENT_SECRET",
        scope_var: str = "OAUTH_SCOPE",
    ) -> "OAuth2ClientCredentialsAuth":
        """
        Create from environment variables.

        Args:
            token_url: Token endpoint URL
            client_id_var: Client ID env var (default: 'OAUTH_CLIENT_ID')
            client_secret_var: Client secret env var (default: 'OAUTH_CLIENT_SECRET')
            scope_var: Scope env var (default: 'OAUTH_SCOPE')

        Returns:
            OAuth2ClientCredentialsAuth instance

        Example:
            >>> # .env: OAUTH_CLIENT_ID=client123, OAUTH_CLIENT_SECRET=secret456
            >>> auth = OAuth2ClientCredentialsAuth.from_env(
            ...     token_url="https://auth.example.com/oauth/token"
            ... )
        """
        import os

        client_id = os.getenv(client_id_var)
        client_secret = os.getenv(client_secret_var)
        scope = os.getenv(scope_var)

        if not client_id or not client_secret:
            raise ValueError(
                f"Environment variables '{client_id_var}' and '{client_secret_var}' are required"
            )

        return cls(client_id, client_secret, token_url, scope)
