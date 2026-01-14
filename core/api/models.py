import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from playwright.async_api import APIResponse

logger = logging.getLogger(__name__)


class APIError(Exception):
    """
    Base exception for all API errors.

    Provides structured error information including status code,
    response body, and request details.

    Attributes:
        message: Error description
        status_code: HTTP status code (if available)
        response_body: Response body (if available)
        url: Request URL
        method: HTTP method

    Example:
        >>> raise APIError(
        ...     message="User not found",
        ...     status_code=404,
        ...     url="https://api.example.com/users/999",
        ...     method="GET"
        ... )
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[Any] = None,
        url: Optional[str] = None,
        method: Optional[str] = None,
    ):
        """Initialize API error."""
        self.message = message
        self.status_code = status_code
        self.response_body = response_body
        self.url = url
        self.method = method
        super().__init__(self.message)

    def __str__(self) -> str:
        """String representation of error."""
        parts = [self.message]
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        if self.method and self.url:
            parts.append(f"{self.method} {self.url}")
        return " | ".join(parts)


class RetryExhaustedError(APIError):
    """
    Raised when all retry attempts have been exhausted.

    Example:
        >>> raise RetryExhaustedError(
        ...     message="Failed after 5 attempts",
        ...     url="https://api.example.com/users"
        ... )
    """

    pass


class ValidationError(APIError):
    """
    Raised when response validation fails.

    Used for schema validation failures, unexpected status codes,
    or missing required fields in responses.

    Example:
        >>> raise ValidationError(
        ...     message="Response missing required field 'id'",
        ...     status_code=200,
        ...     response_body={'name': 'John'}
        ... )
    """

    pass


class AuthenticationError(APIError):
    """
    Raised when authentication fails.

    Typically for 401 Unauthorized responses or token refresh failures.

    Example:
        >>> raise AuthenticationError(
        ...     message="Invalid access token",
        ...     status_code=401,
        ...     url="https://api.example.com/protected"
        ... )
    """

    pass


class AuthorizationError(APIError):
    """
    Raised when authorization fails.

    Typically for 403 Forbidden responses when user lacks permissions.

    Example:
        >>> raise AuthorizationError(
        ...     message="Insufficient permissions",
        ...     status_code=403,
        ...     url="https://api.example.com/admin/users"
        ... )
    """

    pass


class TimeoutError(APIError):
    """
    Raised when request times out.

    Example:
        >>> raise TimeoutError(
        ...     message="Request timed out after 30s",
        ...     url="https://api.example.com/slow-endpoint"
        ... )
    """

    pass


class RateLimitError(APIError):
    """
    Raised when rate limit is exceeded.

    Typically for 429 Too Many Requests responses.

    Attributes:
        retry_after: Seconds to wait before retrying (from Retry-After header)

    Example:
        >>> raise RateLimitError(
        ...     message="Rate limit exceeded",
        ...     status_code=429,
        ...     retry_after=60
        ... )
    """

    def __init__(self, *args, retry_after: Optional[int] = None, **kwargs):
        """Initialize rate limit error."""
        super().__init__(*args, **kwargs)
        self.retry_after = retry_after
