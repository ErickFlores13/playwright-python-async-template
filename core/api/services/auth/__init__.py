"""
Authentication module.

Provides authentication for API clients using a facade pattern with underlying strategies.

Primary API (Recommended):
    - AuthService: Simple facade with factory methods for common auth types
        - with_bearer_token() - JWT/Bearer token authentication
        - with_api_key() - API key authentication
        - with_basic_auth() - HTTP Basic authentication
        - with_custom_headers() - Custom header authentication

Advanced Usage:
    - Direct strategy classes for special cases:
        - BearerTokenAuth: JWT/OAuth bearer tokens
        - APIKeyAuth: API key authentication
        - BasicAuth: Username/password basic auth
        - OAuth2ClientCredentialsAuth: OAuth2 client credentials flow
        - CustomHeaderAuth: Custom authentication headers
        - CompositeAuth: Combine multiple strategies
        - RefreshableTokenAuth: Auto-refreshing tokens

Example:
    >>> from core.api.services.auth import AuthService
    >>> auth = AuthService.with_bearer_token("my-token")
    >>> client = UserServiceClient(context, base_url, auth_strategy=auth)
"""

from .auth_service import AuthService, TokenInfo
from .base import AuthStrategy
from .strategies import (
    APIKeyAuth,
    BasicAuth,
    BearerTokenAuth,
    CompositeAuth,
    CustomHeaderAuth,
    OAuth2ClientCredentialsAuth,
    RefreshableTokenAuth,
)

__all__ = [
    # Primary API (Recommended)
    "AuthService",
    "TokenInfo",
    # Base
    "AuthStrategy",
    # Advanced: Direct strategies
    "BearerTokenAuth",
    "APIKeyAuth",
    "BasicAuth",
    "OAuth2ClientCredentialsAuth",
    "CustomHeaderAuth",
    "CompositeAuth",
    "RefreshableTokenAuth",
]
