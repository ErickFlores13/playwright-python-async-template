"""Composite authentication strategy."""

from typing import Dict

from ..base import AuthStrategy


class CompositeAuth(AuthStrategy):
    """
    Composite authentication (multiple strategies).

    Combines multiple auth strategies into one. Headers from all strategies
    are merged (later strategies override earlier ones on conflict).

    Example:
        API KEY + Bearer Token:
        ```
        api_key_auth = APIKeyAuth("sk_test_abc123", header_name="X-API-Key")
        bearer_auth = BearerTokenAuth("eyJhbGci...")
        composite_auth = CompositeAuth([api_key_auth, bearer_auth])
        headers = await composite_auth.get_auth_headers()
        # {'X-API-Key': 'sk_test_abc123', 'Authorization': 'Bearer eyJhbGci...'}
        ```
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
