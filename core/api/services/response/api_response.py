import logging
from typing import Any, Dict, Optional

from playwright.async_api import APIResponse

logger = logging.getLogger(__name__)


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
