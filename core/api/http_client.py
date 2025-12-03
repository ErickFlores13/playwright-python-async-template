import logging
import time
from typing import Any, Dict, Optional

from playwright.async_api import APIRequestContext, APIResponse

from core.api.config import HTTPConfig
from core.api.models import APIError, APIResponseWrapper, TimeoutError
from core.api.services.interceptor import InterceptorService
from core.api.services.retry import RetryService

logger = logging.getLogger(__name__)


class HTTPClient:
    """
    Core HTTP client with resilience patterns.

    Handles low-level HTTP mechanics including:
    - Retry logic with exponential backoff
    - Request/response interceptors
    - Timeout management
    - Connection handling via Playwright

    This class should NOT contain business logic, authentication,
    or validation - those belong in BaseAPIClient and service clients.
    """

    def __init__(self, playwright_context: APIRequestContext, config: Optional[HTTPConfig] = None):
        """
        Initialize HTTP client.

        Args:
            playwright_context: Playwright APIRequestContext for making requests
            config: Optional HTTP configuration (defaults to HTTPConfig.standard())
        """
        self._context = playwright_context
        self.config = config or HTTPConfig.standard()

        # Initialize services
        self._retry_service = RetryService(self.config.retry)
        self._interceptor = InterceptorService(self.config.interceptor)

        logger.info(f"HTTPClient initialized with config: {self.config}")

    async def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> APIResponseWrapper:
        """
        Execute HTTP request with retry logic.

        This is the core method that all HTTP requests flow through.
        It applies retry logic and interceptors.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            url: Request URL (absolute or relative to base_url)
            params: Query parameters
            data: Request body (dict will be JSON encoded)
            headers: Request headers
            timeout: Request timeout in seconds (overrides config)

        Returns:
            APIResponseWrapper with response data and metadata

        Raises:
            APIError: For HTTP errors or request failures
            RetryExhaustedError: When all retry attempts fail
            TimeoutError: When request times out

        Example:
            >>> # GET request with query params
            >>> response = await client.request(
            ...     'GET',
            ...     '/users',
            ...     params={'page': 1, 'limit': 10}
            ... )
            >>>
            >>> # POST request with JSON body
            >>> response = await client.request(
            ...     'POST',
            ...     '/users',
            ...     data={'name': 'John', 'email': 'john@example.com'}
            ... )
        """
        # Merge headers with base headers
        request_headers = {**self.config.base_headers, **(headers or {})}

        # Before request interceptor
        request_context = await self._interceptor.before_request(
            method=method, url=url, headers=request_headers, params=params, data=data
        )

        # Execute request with retry
        try:
            response = await self._retry_service.execute(
                self._execute_request,
                method=method,
                url=url,
                params=params,
                data=data,
                headers=request_headers,
                timeout=timeout,
            )

            # After response interceptor
            response = await self._interceptor.after_response(response, request_context)

            return response

        except Exception as e:
            logger.error(f"Request failed: {method} {url} - {type(e).__name__}: {str(e)}")
            raise

    async def _execute_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]],
        data: Optional[Any],
        headers: Optional[Dict[str, str]],
        timeout: Optional[float],
    ) -> APIResponseWrapper:
        """
        Execute raw HTTP request via Playwright.

        Args:
            method: HTTP method
            url: Request URL
            params: Query parameters
            data: Request body
            headers: Request headers
            timeout: Request timeout

        Returns:
            APIResponseWrapper

        Raises:
            APIError: For HTTP errors
            TimeoutError: For timeout errors
        """
        start_time = time.time()

        # Get request timeout
        request_timeout = timeout or self.config.timeout.request_timeout
        timeout_ms = int(request_timeout * 1000)  # Convert to milliseconds

        try:
            # Get Playwright request method
            request_method = getattr(self._context, method.lower())

            # Build request kwargs
            kwargs = {"timeout": timeout_ms}

            if headers:
                kwargs["headers"] = headers
            if params:
                kwargs["params"] = params
            if data is not None:
                kwargs["data"] = data

            # Execute request
            logger.debug(f"Executing {method} {url}")
            playwright_response: APIResponse = await request_method(url, **kwargs)

            # Calculate elapsed time
            elapsed = (time.time() - start_time) * 1000  # milliseconds

            # Parse response
            response_wrapper = await self._parse_response(
                playwright_response, method=method, url=url, elapsed_ms=elapsed
            )

            return response_wrapper

        except Exception as e:
            elapsed = (time.time() - start_time) * 1000

            # Handle timeout errors
            if "timeout" in str(e).lower():
                raise TimeoutError(
                    message=f"Request timed out after {request_timeout}s", url=url, method=method
                )

            # Wrap other exceptions
            raise APIError(message=f"Request failed: {str(e)}", url=url, method=method) from e

    async def _parse_response(
        self, response: APIResponse, method: str, url: str, elapsed_ms: float
    ) -> APIResponseWrapper:
        """
        Parse Playwright APIResponse into APIResponseWrapper.

        Args:
            response: Playwright APIResponse
            method: HTTP method
            url: Request URL
            elapsed_ms: Request duration in milliseconds

        Returns:
            APIResponseWrapper
        """
        # Get response data
        try:
            # Handle 204 No Content
            if response.status == 204:
                data = None
            else:
                # Try to parse as JSON
                try:
                    data = await response.json()
                except Exception:
                    # Fall back to text
                    data = await response.text()
        except Exception as e:
            logger.warning(f"Failed to parse response body: {e}")
            data = None

        # Get response headers
        headers = dict(response.headers)

        # Create wrapper
        wrapper = APIResponseWrapper(
            status_code=response.status,
            data=data,
            headers=headers,
            url=url,
            method=method,
            elapsed_ms=elapsed_ms,
            raw_response=response,
        )

        return wrapper

    @property
    def retry_service(self) -> RetryService:
        """Access retry service for metrics/inspection."""
        return self._retry_service

    @property
    def interceptor(self) -> InterceptorService:
        """Access interceptor service for metrics/inspection."""
        return self._interceptor

    async def health_check(self, url: str = "/health") -> bool:
        """
        Perform health check against service.

        Args:
            url: Health check endpoint

        Returns:
            True if service is healthy

        Example:
            >>> is_healthy = await client.health_check('/api/health')
        """
        try:
            response = await self.request("GET", url)
            return response.is_success
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False
