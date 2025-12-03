"""
Response and exception models for API framework.

Provides standardized response wrappers and custom exceptions
for consistent error handling across all API clients.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from playwright.async_api import APIResponse

logger = logging.getLogger(__name__)


@dataclass
class APIResponseWrapper:
    """
    Wrapper for API responses with common metadata.

    Provides a consistent interface for accessing response data,
    status codes, headers, and timing information.

    Attributes:
        status_code: HTTP status code
        data: Parsed response body (usually dict or list)
        headers: Response headers
        url: Request URL
        method: HTTP method used
        elapsed_ms: Request duration in milliseconds
        raw_response: Original Playwright APIResponse object

    Example:
        >>> response = APIResponseWrapper(
        ...     status_code=200,
        ...     data={'id': 1, 'name': 'John'},
        ...     headers={'content-type': 'application/json'},
        ...     url='https://api.example.com/users/1',
        ...     method='GET',
        ...     elapsed_ms=145.5
        ... )
        >>> print(response.data['name'])  # 'John'
        >>> print(response.is_success)    # True
    """

    status_code: int
    data: Any
    headers: Dict[str, str]
    url: str
    method: str
    elapsed_ms: float
    raw_response: Optional[APIResponse] = None

    @property
    def is_success(self) -> bool:
        """Check if response is successful (2xx status code)."""
        return 200 <= self.status_code < 300

    @property
    def is_client_error(self) -> bool:
        """Check if response is client error (4xx status code)."""
        return 400 <= self.status_code < 500

    @property
    def is_server_error(self) -> bool:
        """Check if response is server error (5xx status code)."""
        return 500 <= self.status_code < 600

    def get_header(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get response header value (case-insensitive).

        Args:
            name: Header name
            default: Default value if header not found

        Returns:
            Header value or default

        Example:
            >>> content_type = response.get_header('content-type')
        """
        for key, value in self.headers.items():
            if key.lower() == name.lower():
                return value
        return default

    def __repr__(self) -> str:
        """String representation of response."""
        return (
            f"APIResponseWrapper(status={self.status_code}, "
            f"method={self.method}, url={self.url}, "
            f"elapsed={self.elapsed_ms:.2f}ms)"
        )


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
