"""
Core services for API framework.

Provides reusable services for:
- Retry logic with exponential backoff
- Request/response interceptors
- Response validation (schemas, status codes, JSON paths)
- Authentication strategies (JWT, OAuth, API keys, Basic auth)
"""

from core.api.services.retry import RetryService
from core.api.services.interceptor import InterceptorService
from core.api.services.validation import ValidationService
from core.api.services.auth import (
    AuthStrategy,
    BearerTokenAuth,
    APIKeyAuth,
    BasicAuth,
    OAuth2ClientCredentialsAuth,
    CustomHeaderAuth,
    CompositeAuth,
    RefreshableTokenAuth,
    TokenInfo,
    AuthService,  # Deprecated - kept for backward compatibility
)

__all__ = [
    # Core services
    'RetryService',
    'InterceptorService',
    'ValidationService',
    
    # Auth strategies (recommended)
    'AuthStrategy',
    'BearerTokenAuth',
    'APIKeyAuth',
    'BasicAuth',
    'OAuth2ClientCredentialsAuth',
    'CustomHeaderAuth',
    'CompositeAuth',
    'RefreshableTokenAuth',
    
    # Primary auth facade
    'TokenInfo',
    'AuthService',
]
