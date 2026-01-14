import logging
from functools import cached_property
from typing import Any, Dict, List, Literal, Optional, Union

from playwright.async_api import APIRequestContext

from core.api.config import HTTPConfig
from core.api.http_client import HTTPClient
from core.api.services.auth import APIKeyAuth, AuthStrategy, BasicAuth, BearerTokenAuth
from core.api.services.response.api_response import APIResponseWrapper
from core.api.services.validation import ValidationService

logger = logging.getLogger(__name__)

HTTPMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]


class BaseAPIClient:
    """
    Base class for API clients with authentication and validation.

    Provides:
    - Standard HTTP methods (get, post, put, patch, delete)
    - Authentication via AuthService
    - Response validation via ValidationService
    - Lazy-loaded services (dependency injection pattern)

    Service clients should extend this class and add domain-specific methods.
    """

    def __init__(
        self,
        playwright_context: APIRequestContext,
        base_url: str,
        auth_strategy: Optional[AuthStrategy] = None,
        http_config: Optional[HTTPConfig] = None,
    ):
        """
        Initialize base API client.

        Args:
            playwright_context: Playwright APIRequestContext for making requests
            base_url: Base URL for API endpoints
            auth_strategy: Optional pre-configured authentication strategy
            http_config: Optional HTTP configuration (defaults to HTTPConfig.from_env())
                        Set HTTP_CONFIG_MODE environment variable to control default:
                        - standard (default)
                        - external_api (for third-party APIs)
                        - local_api (for localhost/Docker)
                        - testing (for fast unit tests)
        """
        self._http = HTTPClient(playwright_context, http_config or HTTPConfig.from_env())
        self._base_url = base_url.rstrip("/")
        self._auth_strategy = auth_strategy

        logger.info(f"BaseAPIClient initialized for {self._base_url}")

    @cached_property
    def validation(self) -> ValidationService:
        """
        Lazy-loaded validation service.

        Returns:
            ValidationService instance

        Example:
            >>> # Validate response schema
            >>> user = self.validation.validate_schema(response.data, UserModel)
            >>>
            >>> # Validate status code
            >>> self.validation.validate_status_code(response, 200)
        """
        return ValidationService()

    @property
    def auth(self) -> Optional[AuthStrategy]:
        """
        Get authentication strategy.

        Returns:
            AuthStrategy instance or None

        Example:
            >>> # Check if authenticated
            >>> if self.auth:
            ...     headers = await self.auth.get_auth_headers()
        """
        return self._auth_strategy

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: Union[int, List[int]] = 200,
    ) -> APIResponseWrapper:
        """
        Make GET request.

        Args:
            endpoint: API endpoint (e.g., '/users/1' or '/users')
            params: Query parameters
            headers: Additional headers
            expected_status: Expected status code(s)

        Returns:
            APIResponseWrapper with response data

        Raises:
            ValidationError: If status code doesn't match expected

        Example:
            >>> # Simple GET
            >>> response = await client.get('/users/1')
            >>>
            >>> # With query params
            >>> response = await client.get('/users', params={'page': 1, 'limit': 10})
            >>>
            >>> # Accept multiple status codes
            >>> response = await client.get('/users/1', expected_status=[200, 304])
        """
        return await self._execute_request(
            method="GET",
            endpoint=endpoint,
            params=params,
            headers=headers,
            expected_status=expected_status,
        )

    async def post(
        self,
        endpoint: str,
        data: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: Union[int, List[int]] = 201,
    ) -> APIResponseWrapper:
        """
        Make POST request.

        Args:
            endpoint: API endpoint
            data: Request body (dict will be JSON encoded)
            params: Query parameters
            headers: Additional headers
            expected_status: Expected status code(s)

        Returns:
            APIResponseWrapper with response data

        Example:
            >>> response = await client.post(
            ...     '/users',
            ...     data={'name': 'John', 'email': 'john@example.com'}
            ... )
            >>>
            >>> # With Pydantic model
            >>> user_data = CreateUserRequest(name='John', email='john@example.com')
            >>> response = await client.post('/users', data=user_data.dict())
        """
        return await self._execute_request(
            method="POST",
            endpoint=endpoint,
            data=data,
            params=params,
            headers=headers,
            expected_status=expected_status,
        )

    async def put(
        self,
        endpoint: str,
        data: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: Union[int, List[int]] = 200,
    ) -> APIResponseWrapper:
        """
        Make PUT request.

        Args:
            endpoint: API endpoint
            data: Request body
            params: Query parameters
            headers: Additional headers
            expected_status: Expected status code(s)

        Returns:
            APIResponseWrapper with response data

        Example:
            >>> response = await client.put(
            ...     '/users/1',
            ...     data={'name': 'John Updated', 'email': 'john.new@example.com'}
            ... )
        """
        return await self._execute_request(
            method="PUT",
            endpoint=endpoint,
            data=data,
            params=params,
            headers=headers,
            expected_status=expected_status,
        )

    async def patch(
        self,
        endpoint: str,
        data: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: Union[int, List[int]] = 200,
    ) -> APIResponseWrapper:
        """
        Make PATCH request.

        Args:
            endpoint: API endpoint
            data: Request body (partial update)
            params: Query parameters
            headers: Additional headers
            expected_status: Expected status code(s)

        Returns:
            APIResponseWrapper with response data

        Example:
            >>> # Partial update
            >>> response = await client.patch('/users/1', data={'email': 'new@example.com'})
        """
        return await self._execute_request(
            method="PATCH",
            endpoint=endpoint,
            data=data,
            params=params,
            headers=headers,
            expected_status=expected_status,
        )

    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: Union[int, List[int]] = 204,
    ) -> APIResponseWrapper:
        """
        Make DELETE request.

        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers
            expected_status: Expected status code(s)

        Returns:
            APIResponseWrapper (data may be None for 204 responses)

        Example:
            >>> response = await client.delete('/users/1')
            >>> assert response.status_code == 204
        """
        return await self._execute_request(
            method="DELETE",
            endpoint=endpoint,
            params=params,
            headers=headers,
            expected_status=expected_status,
        )

    async def _execute_request(
        self,
        method: HTTPMethod,
        endpoint: str,
        data: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: Union[int, List[int]] = None,
    ) -> APIResponseWrapper:
        """
        Generalized request method.

        Args:
            method: HTTP method (GET, POST, etc.)
            data: Request body
            params: Query parameters
            headers: Additional headers
            expected_status: Expected status code(s)

        Returns:
            APIResponseWrapper with response data

        Example:
            >>> response = await client.request(
            ...     'POST',
            ...     '/users',
            ...     data={'name': 'Alice'},
            ...     expected_status=201
            ... )
        """
        url = self._build_url(endpoint)
        request_headers = await self._prepare_headers(headers)

        response = await self._http.request(
            method, url, params=params, data=data, headers=request_headers
        )

        if expected_status is not None:
            self.validation.validate_status_code(response, expected_status)

        return response

    def _build_url(self, endpoint: str) -> str:
        """
        Build full URL from endpoint.

        Args:
            endpoint: Endpoint path

        Returns:
            Full URL
        """
        # Handle absolute URLs
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint

        # Ensure endpoint starts with /
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"

        return f"{self._base_url}{endpoint}"

    async def _prepare_headers(
        self, custom_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Prepare request headers with authentication.

        Args:
            custom_headers: Additional headers to merge

        Returns:
            Complete headers dict
        """
        headers = {}

        # Add auth headers if auth strategy configured
        if self._auth_strategy:
            auth_headers = await self._auth_strategy.get_auth_headers()
            headers.update(auth_headers)

        # Merge custom headers (override auth headers if conflicts)
        if custom_headers:
            headers.update(custom_headers)

        return headers

    # Authentication convenience methods

    def set_bearer_token(
        self,
        token: Optional[str] = None,
        token_type: Optional[str] = None,
        expires_at: Optional[float] = None,
    ) -> None:
        """
        Configure Bearer token authentication.

        Args:
            token: JWT or Bearer token (if None, read from environment)
            token_type: Token type (default: 'Bearer')
            expires_at: Token expiration timestamp

        Example:
            >>> client.set_bearer_token("eyJhbGci...")
            >>> # or from environment:
            >>> client.set_bearer_token()
        """
        self._auth_strategy = BearerTokenAuth.from_env(token, token_type)
        if expires_at:
            self._auth_strategy.expires_at = expires_at
        logger.info("Bearer token authentication configured")

    def set_api_key(self, api_key: Optional[str] = None, header_name: Optional[str] = None) -> None:
        """
        Configure API key authentication.

        Args:
            api_key: API key value (if None, read from environment)
            header_name: Header name for API key (if None, read from environment)

        Example:
            >>> client.set_api_key("sk_test_abc123", header_name="Authorization")
            >>> # or from environment:
            >>> client.set_api_key()
        """
        self._auth_strategy = APIKeyAuth.from_env(api_key, header_name)
        logger.info(
            f"API key authentication configured (header: {self._auth_strategy.header_name})"
        )

    def set_basic_auth(
        self, username: Optional[str] = None, password: Optional[str] = None
    ) -> None:
        """
        Configure Basic authentication.

        Args:
            username: Username (if None, read from environment)
            password: Password (if None, read from environment)

        Example:
            >>> client.set_basic_auth("admin", "password123")
            >>> # or from environment:
            >>> client.set_basic_auth()
        """
        self._auth_strategy = BasicAuth.from_env(username, password)
        logger.info(f"Basic authentication configured (user: {self._auth_strategy.username})")

    def set_auth(self, auth_strategy: AuthStrategy) -> None:
        """
        Set custom authentication strategy.

        Args:
            auth_strategy: Pre-configured AuthStrategy

        Example:
            >>> from core.api.services.auth import CompositeAuth, APIKeyAuth, BearerTokenAuth
            >>> auth = CompositeAuth([APIKeyAuth('key'), BearerTokenAuth('token')])
            >>> client.set_auth(auth)
        """
        self._auth_strategy = auth_strategy
        logger.info("Custom authentication strategy configured")

    @property
    def base_url(self) -> str:
        """Get base URL."""
        return self._base_url

    @property
    def http_client(self) -> HTTPClient:
        """Get underlying HTTP client."""
        return self._http
