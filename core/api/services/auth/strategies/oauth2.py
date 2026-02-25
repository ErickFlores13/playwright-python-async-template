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
        Fetch access token from token endpoint using client credentials flow.

        Makes a POST request to the token URL with client credentials.
        Uses the standard OAuth2 client_credentials grant type.

        Raises:
            RuntimeError: If token request fails or response is invalid
        """
        import asyncio
        import json
        import urllib.error
        import urllib.parse
        import urllib.request

        logger.info(f"Fetching OAuth2 token from {self.token_url}")

        post_data: dict = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        if self.scope:
            post_data["scope"] = self.scope

        encoded_data = urllib.parse.urlencode(post_data).encode("utf-8")

        def _sync_fetch() -> dict:
            req = urllib.request.Request(
                self.token_url,
                data=encoded_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                method="POST",
            )
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode("utf-8"))

        try:
            token_response = await asyncio.to_thread(_sync_fetch)
            self._access_token = token_response["access_token"]
            expires_in = token_response.get("expires_in", 3600)
            self._expires_at = time.time() + int(expires_in)
            logger.info("OAuth2 token fetched successfully")
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            raise RuntimeError(
                f"OAuth2 token request failed (HTTP {e.code}): {error_body}"
            ) from e
        except (KeyError, ValueError) as e:
            raise RuntimeError(f"Invalid OAuth2 token response: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to fetch OAuth2 token: {e}") from e

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
