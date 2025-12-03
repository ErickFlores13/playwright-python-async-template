"""Composite authentication strategy."""

from typing import Dict

from ..base import AuthStrategy


class CompositeAuth(AuthStrategy):
    """
    Composite authentication (multiple strategies).

    Combines multiple auth strategies into one. Headers from all strategies
    are merged (later strategies override earlier ones on conflict).

    Example:
        >>> # API Key + Bearer Token
        >>> auth = CompositeAuth([
        ...     APIKeyAuth("api-key-123", "X-API-Key"),
        ...     BearerTokenAuth("jwt-token")
        ... ])
        >>> headers = await auth.get_auth_headers()
        >>> # {'X-API-Key': 'api-key-123', 'Authorization': 'Bearer jwt-token'}

        >>> # From environment
        >>> auth = CompositeAuth([
        ...     APIKeyAuth.from_env("STRIPE_API_KEY"),
        ...     CustomHeaderAuth.from_env({'X-User-ID': 'USER_ID'})
        ... ])
    """

    def __init__(self, strategies: list[AuthStrategy]):
        """
        Initialize composite auth.

        Args:
            strategies: List of auth strategies to combine
        """
        if not strategies:
            raise ValueError("At least one strategy is required")
        self.strategies = strategies

    async def get_auth_headers(self) -> Dict[str, str]:
        """Get combined headers from all strategies."""
        headers = {}

        for strategy in self.strategies:
            strategy_headers = await strategy.get_auth_headers()
            headers.update(strategy_headers)

        return headers
