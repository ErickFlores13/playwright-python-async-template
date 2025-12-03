"""Refreshable token authentication strategy."""

import logging
import time
from typing import Callable, Dict, Optional

from ..base import AuthStrategy

logger = logging.getLogger(__name__)


class RefreshableTokenAuth(AuthStrategy):
    """
    Token authentication with automatic refresh.

    Wraps a token and provides automatic refresh via callback.

    Example:
        >>> async def refresh_token():
        ...     response = await auth_api.refresh()
        ...     return response.data['access_token']
        >>>
        >>> auth = RefreshableTokenAuth(
        ...     initial_token="old-token",
        ...     refresh_callback=refresh_token,
        ...     expires_at=time.time() + 3600
        ... )
        >>> headers = await auth.get_auth_headers()
        >>> # Automatically refreshes if expired
    """

    def __init__(
        self,
        initial_token: str,
        refresh_callback: Callable[[], str],
        expires_at: Optional[float] = None,
        token_type: str = "Bearer",
    ):
        """
        Initialize refreshable token auth.

        Args:
            initial_token: Initial access token
            refresh_callback: Async function that returns new token
            expires_at: Token expiration timestamp
            token_type: Token type (default: 'Bearer')
        """
        self.token = initial_token
        self.refresh_callback = refresh_callback
        self.expires_at = expires_at
        self.token_type = token_type

    async def get_auth_headers(self) -> Dict[str, str]:
        """Get Authorization header, refreshing token if needed."""
        if self._needs_refresh():
            await self._refresh_token()

        return {"Authorization": f"{self.token_type} {self.token}"}

    def _needs_refresh(self) -> bool:
        """Check if token needs refresh (with 60s buffer)."""
        if self.expires_at is None:
            return False
        return time.time() >= (self.expires_at - 60)

    async def _refresh_token(self) -> None:
        """Refresh access token via callback."""
        try:
            logger.info("Refreshing access token")
            new_token = await self.refresh_callback()
            self.token = new_token
            # Reset expiration (estimate 1 hour if not provided)
            self.expires_at = time.time() + 3600
            logger.info("Access token refreshed successfully")
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise
