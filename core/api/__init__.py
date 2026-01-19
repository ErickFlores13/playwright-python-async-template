"""
Core API Testing Framework

Production-ready async API testing framework with resilience patterns,
authentication, validation, and clean architecture.

Quick Start:
    >>> from playwright.async_api import async_playwright
    >>> from core.api import HTTPClient, BaseAPIClient, HTTPConfig
    >>>
    >>> async with async_playwright() as p:
    ...     # Create Playwright request context
    ...     context = await p.request.new_context(base_url="https://api.example.com")
    ...
    ...     # Create HTTP client with config
    ...     config = HTTPConfig.standard()
    ...     http = HTTPClient(context, config)
    ...
    ...     # Create API client
    ...     api = BaseAPIClient(http, base_url="https://api.example.com")
    ...
    ...     # Configure authentication
    ...     api.set_bearer_token("your-jwt-token")
    ...
    ...     # Make requests
    ...     response = await api.get('/users/1')
    ...     print(response.data)

Architecture:
    HTTPClient (Low-level)
        ├── Retry logic with exponential backoff
        ├── Request/response interceptors
        └── Timeout management

    BaseAPIClient (Mid-level)
        ├── Uses HTTPClient
        ├── Authentication (JWT, OAuth, API keys)
        ├── Response validation (schemas, status codes)
        └── Standard HTTP methods (get, post, put, patch, delete)

    Service Clients (High-level)
        ├── Extend BaseAPIClient
        ├── Domain-specific methods (create_user, get_order, etc.)
        └── Business logic

Main Components:
    - HTTPClient: Core HTTP infrastructure with resilience
    - BaseAPIClient: Reusable API patterns with auth/validation
    - HTTPConfig: Configuration for retry and timeouts
    - Services: Retry, Interceptor, Validation, Auth
    - Models: APIResponseWrapper, exceptions

Example Service Client:
    >>> from pydantic import BaseModel
    >>> from core.api import BaseAPIClient
    >>>
    >>> class User(BaseModel):
    ...     id: int
    ...     name: str
    ...     email: str
    >>>
    >>> class UserAPIClient(BaseAPIClient):
    ...     async def create_user(self, name: str, email: str) -> User:
    ...         response = await self.post(
    ...             '/users',
    ...             data={'name': name, 'email': email}
    ...         )
    ...         return self.validation.validate_schema(response.data, User)
    ...
    ...     async def get_user(self, user_id: int) -> User:
    ...         response = await self.get(f'/users/{user_id}')
    ...         return self.validation.validate_schema(response.data, User)
"""

from core.api.base_client import BaseAPIClient

# Configuration
from core.api.config import HTTPConfig, InterceptorConfig, RetryConfig, TimeoutConfig

# Core clients
from core.api.http_client import HTTPClient

# Models and exceptions
from core.api.models import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    RetryExhaustedError,
    TimeoutError,
    ValidationError,
)

# Services
from core.api.services import (
    AuthService,
    InterceptorService,
    RetryService,
    TokenInfo,
    ValidationService,
)

# Auth strategies
from core.api.services.auth import (
    APIKeyAuth,
    BasicAuth,
    BearerTokenAuth,
    CompositeAuth,
    CustomHeaderAuth,
    OAuth2ClientCredentialsAuth,
    RefreshableTokenAuth,
)
from core.api.services.response.api_response import APIResponseWrapper

__version__ = "1.0.0"

__all__ = [
    # Core clients
    "HTTPClient",
    "BaseAPIClient",
    # Configuration
    "HTTPConfig",
    "RetryConfig",
    "TimeoutConfig",
    "InterceptorConfig",
    # Models
    "APIResponseWrapper",
    # Exceptions
    "APIError",
    "RetryExhaustedError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "TimeoutError",
    "RateLimitError",
    # Services
    "RetryService",
    "InterceptorService",
    "ValidationService",
    "AuthService",
    "TokenInfo",
    # Auth strategies
    "BearerTokenAuth",
    "APIKeyAuth",
    "BasicAuth",
    "OAuth2ClientCredentialsAuth",
    "CustomHeaderAuth",
    "CompositeAuth",
    "RefreshableTokenAuth",
]
