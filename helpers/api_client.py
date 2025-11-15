import logging
import asyncio
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from playwright.async_api import APIRequestContext
from utils.exceptions import APIError

logger = logging.getLogger(__name__)

class APIClient:
    """
    API client using Playwright's APIRequestContext.
    
    Provides methods for making HTTP requests with built-in
    error handling, authentication, and response validation.
    """
    
    def __init__(self, request_context: APIRequestContext, base_url: str) -> None:
        """
        Initialize API client with Playwright's request context.
        
        Args:
            request_context (APIRequestContext): Playwright's API request context.
            base_url (str): Base URL for API endpoints.
            
        Example:
            # In conftest.py or test
            async with playwright.request.new_context(base_url="https://api.example.com") as context:
                api = APIClient(context, "https://api.example.com")
        """
        self.request = request_context
        self.base_url = base_url.rstrip('/')
    
    async def get(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: int = 200
    ) -> Dict[str, Any]:
        """
        Make GET request.
        
        Args:
            endpoint (str): API endpoint (e.g., '/users/123').
            params (dict, optional): Query parameters.
            headers (dict, optional): Additional headers.
            expected_status (int): Expected HTTP status code. Defaults to 200.
            
        Returns:
            dict: Response JSON data.
            
        Raises:
            APIError: If response status doesn't match expected.
            
        Example:
            data = await api.get('/users', params={'page': 1})
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = await self.request.get(
                url,
                params=params,
                headers=headers
            )
            
            await self._validate_response(response, expected_status)
            return await response.json()
            
        except Exception as e:
            logger.error(f"GET request failed for {url}: {e}")
            raise APIError(f"GET {endpoint} failed: {str(e)}") from e
    
    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: int = 201
    ) -> Dict[str, Any]:
        """
        Make POST request.
        
        Args:
            endpoint (str): API endpoint.
            data (dict, optional): JSON data to send.
            headers (dict, optional): Additional headers.
            expected_status (int): Expected HTTP status code. Defaults to 201.
            
        Returns:
            dict: Response JSON data.
            
        Raises:
            APIError: If response status doesn't match expected.
            
        Example:
            response = await api.post('/users', data={'name': 'John', 'email': 'john@example.com'})
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = await self.request.post(
                url,
                data=data,
                headers=headers
            )
            
            await self._validate_response(response, expected_status)
            return await response.json()
            
        except Exception as e:
            logger.error(f"POST request failed for {url}: {e}")
            raise APIError(f"POST {endpoint} failed: {str(e)}") from e
    
    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: int = 200
    ) -> Dict[str, Any]:
        """
        Make PUT request.
        
        Args:
            endpoint (str): API endpoint.
            data (dict, optional): JSON data to send.
            headers (dict, optional): Additional headers.
            expected_status (int): Expected HTTP status code. Defaults to 200.
            
        Returns:
            dict: Response JSON data.
            
        Raises:
            APIError: If response status doesn't match expected.
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = await self.request.put(
                url,
                data=data,
                headers=headers
            )
            
            await self._validate_response(response, expected_status)
            return await response.json()
            
        except Exception as e:
            logger.error(f"PUT request failed for {url}: {e}")
            raise APIError(f"PUT {endpoint} failed: {str(e)}") from e
    
    async def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: int = 200
    ) -> Dict[str, Any]:
        """
        Make PATCH request.
        
        Args:
            endpoint (str): API endpoint.
            data (dict, optional): JSON data to send.
            headers (dict, optional): Additional headers.
            expected_status (int): Expected HTTP status code. Defaults to 200.
            
        Returns:
            dict: Response JSON data.
            
        Raises:
            APIError: If response status doesn't match expected.
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = await self.request.patch(
                url,
                data=data,
                headers=headers
            )
            
            await self._validate_response(response, expected_status)
            return await response.json()
            
        except Exception as e:
            logger.error(f"PATCH request failed for {url}: {e}")
            raise APIError(f"PATCH {endpoint} failed: {str(e)}") from e
    
    async def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        expected_status: int = 204
    ) -> Optional[Dict[str, Any]]:
        """
        Make DELETE request.
        
        Args:
            endpoint (str): API endpoint.
            headers (dict, optional): Additional headers.
            expected_status (int): Expected HTTP status code. Defaults to 204.
            
        Returns:
            dict or None: Response JSON data if available, None for 204 responses.
            
        Raises:
            APIError: If response status doesn't match expected.
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = await self.request.delete(
                url,
                headers=headers
            )
            
            await self._validate_response(response, expected_status)
            
            # DELETE often returns 204 No Content
            if response.status == 204:
                return None
                
            return await response.json()
            
        except Exception as e:
            logger.error(f"DELETE request failed for {url}: {e}")
            raise APIError(f"DELETE {endpoint} failed: {str(e)}") from e
    
    async def _validate_response(self, response, expected_status: int) -> None:
        """
        Validates HTTP response status.
        
        Args:
            response: Playwright APIResponse object.
            expected_status (int): Expected HTTP status code.
            
        Raises:
            APIError: If status doesn't match expected.
        """
        if response.status != expected_status:
            try:
                error_body = await response.json()
            except:
                error_body = await response.text()
                
            raise APIError(
                f"Expected status {expected_status} but got {response.status}. "
                f"Response: {error_body}"
            )
    
    async def set_bearer_token(self, token: str) -> None:
        """
        Sets Bearer token authentication (OAuth 2.0, JWT).
        
        Args:
            token (str): Bearer token.
            
        Example:
            await api.set_bearer_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        """
        await self.set_extra_headers({"Authorization": f"Bearer {token}"})
        logger.info("Bearer token authentication set")
    
    async def set_api_key(self, api_key: str, header_name: str = "X-API-Key") -> None:
        """
        Sets API Key authentication.
        
        Args:
            api_key (str): API key value.
            header_name (str): Header name for API key. Defaults to X-API-Key.
            
        Example:
            await api.set_api_key("your-api-key-123")
            await api.set_api_key("key-123", header_name="Authorization")
        """
        await self.set_extra_headers({header_name: api_key})
        logger.info(f"API Key authentication set (header: {header_name})")
    
    async def set_basic_auth(self, username: str, password: str) -> None:
        """
        Sets Basic authentication (username:password encoded in base64).
        
        Args:
            username (str): Username.
            password (str): Password.
            
        Example:
            await api.set_basic_auth("admin", "password123")
        """
        import base64
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        await self.set_extra_headers({"Authorization": f"Basic {credentials}"})
        logger.info("Basic authentication set")
    
    async def set_extra_headers(self, headers: Dict[str, str]) -> None:
        """
        Sets additional headers for all subsequent requests.
        
        Args:
            headers (dict): Dictionary of header key-value pairs.
            
        Example:
            await api.set_extra_headers({
                "X-Tenant-ID": "tenant-123",
                "Authorization": "Custom xyz789"
            })
        """
        await self.request.set_extra_http_headers(headers)
        logger.debug(f"Extra headers set: {list(headers.keys())}")
    
    async def clear_auth(self) -> None:
        """
        Clears authentication headers.
        
        Useful when switching between authenticated and public endpoints.
        
        Example:
            await api.clear_auth()
            public_data = await api.get("/public/health")
        """
        await self.set_extra_headers({"Authorization": ""})
        logger.info("Authentication cleared")
    
    # ========================================================================
    # FILE UPLOAD & DOWNLOAD
    # ========================================================================
    
    async def upload_file(
        self,
        endpoint: str,
        file_path: str,
        field_name: str = "file",
        data: Optional[Dict[str, Any]] = None,
        expected_status: int = 201
    ) -> Dict[str, Any]:
        """
        Upload a file to an API endpoint using multipart/form-data.
        
        Args:
            endpoint (str): API endpoint for file upload.
            file_path (str): Path to the file to upload.
            field_name (str): Form field name for the file. Defaults to "file".
            data (dict, optional): Additional form data to send with the file.
            expected_status (int): Expected HTTP status code. Defaults to 201.
            
        Returns:
            dict: Response JSON data.
            
        Raises:
            APIError: If file doesn't exist or upload fails.
            
        Example:
            response = await api.upload_file(
                "/users/profile/avatar",
                "path/to/image.jpg",
                field_name="avatar",
                data={"user_id": "123"}
            )
        """
        url = f"{self.base_url}{endpoint}"
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            raise APIError(f"File not found: {file_path}")
        
        try:
            # Prepare multipart form data
            multipart = {
                field_name: {
                    "name": file_path_obj.name,
                    "mimeType": self._get_mime_type(file_path_obj),
                    "buffer": file_path_obj.read_bytes()
                }
            }
            
            # Add additional form data if provided
            if data:
                for key, value in data.items():
                    multipart[key] = str(value)
            
            response = await self.request.post(url, multipart=multipart)
            await self._validate_response(response, expected_status)
            
            logger.info(f"File uploaded successfully: {file_path_obj.name} to {endpoint}")
            return await response.json()
            
        except Exception as e:
            logger.error(f"File upload failed for {endpoint}: {e}")
            raise APIError(f"Upload {endpoint} failed: {str(e)}") from e
    
    async def download_file(
        self,
        endpoint: str,
        save_path: str,
        params: Optional[Dict[str, Any]] = None,
        expected_status: int = 200
    ) -> str:
        """
        Download a file from an API endpoint.
        
        Args:
            endpoint (str): API endpoint for file download.
            save_path (str): Path where the file should be saved.
            params (dict, optional): Query parameters.
            expected_status (int): Expected HTTP status code. Defaults to 200.
            
        Returns:
            str: Path to the downloaded file.
            
        Raises:
            APIError: If download fails.
            
        Example:
            file_path = await api.download_file(
                "/reports/monthly/export",
                "downloads/report.pdf",
                params={"month": "2025-01"}
            )
        """
        url = f"{self.base_url}{endpoint}"
        save_path_obj = Path(save_path)
        
        # Create parent directory if it doesn't exist
        save_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            response = await self.request.get(url, params=params)
            await self._validate_response(response, expected_status)
            
            # Save the file
            file_content = await response.body()
            save_path_obj.write_bytes(file_content)
            
            logger.info(f"File downloaded successfully to: {save_path}")
            return str(save_path_obj)
            
        except Exception as e:
            logger.error(f"File download failed for {endpoint}: {e}")
            raise APIError(f"Download {endpoint} failed: {str(e)}") from e
    
    def _get_mime_type(self, file_path: Path) -> str:
        """Helper to determine MIME type from file extension."""
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.csv': 'text/csv',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.zip': 'application/zip',
        }
        return mime_types.get(file_path.suffix.lower(), 'application/octet-stream')
    
    # ========================================================================
    # PAGINATION HELPER
    # ========================================================================
    
    async def get_paginated(
        self,
        endpoint: str,
        page_param: str = "page",
        limit_param: str = "limit",
        limit: int = 100,
        max_pages: Optional[int] = None,
        data_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Automatically fetch all pages from a paginated API endpoint.
        
        Args:
            endpoint (str): API endpoint.
            page_param (str): Query parameter name for page number. Defaults to "page".
            limit_param (str): Query parameter name for page size. Defaults to "limit".
            limit (int): Number of items per page. Defaults to 100.
            max_pages (int, optional): Maximum number of pages to fetch. None = fetch all.
            data_key (str, optional): Key in response containing the data array.
                                     If None, assumes response is the array.
            headers (dict, optional): Additional headers.
            
        Returns:
            list: All items from all pages combined.
            
        Example:
            # Response format: {"data": [...], "total": 500}
            all_users = await api.get_paginated(
                "/users",
                page_param="page",
                limit_param="per_page",
                limit=50,
                data_key="data"
            )
            
            # Response format: [...]
            all_items = await api.get_paginated("/items", data_key=None)
        """
        all_items = []
        page = 1
        
        logger.info(f"Starting paginated fetch from {endpoint}")
        
        while True:
            if max_pages and page > max_pages:
                logger.info(f"Reached max_pages limit: {max_pages}")
                break
            
            params = {page_param: page, limit_param: limit}
            
            try:
                response = await self.get(endpoint, params=params, headers=headers)
                
                # Extract data from response
                if data_key:
                    items = response.get(data_key, [])
                else:
                    items = response if isinstance(response, list) else []
                
                if not items:
                    logger.info(f"No more items found at page {page}")
                    break
                
                all_items.extend(items)
                logger.info(f"Fetched page {page}: {len(items)} items (total: {len(all_items)})")
                
                # Check if there are more pages
                if len(items) < limit:
                    logger.info("Last page reached (fewer items than limit)")
                    break
                
                page += 1
                
            except Exception as e:
                logger.error(f"Pagination stopped at page {page}: {e}")
                break
        
        logger.info(f"Pagination complete. Total items fetched: {len(all_items)}")
        return all_items
    
    # ========================================================================
    # RETRY LOGIC WITH EXPONENTIAL BACKOFF
    # ========================================================================
    
    async def request_with_retry(
        self,
        method: str,
        endpoint: str,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        retry_statuses: List[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an HTTP request with automatic retry logic and exponential backoff.
        
        Args:
            method (str): HTTP method (get, post, put, patch, delete).
            endpoint (str): API endpoint.
            max_retries (int): Maximum number of retry attempts. Defaults to 3.
            backoff_factor (float): Multiplier for exponential backoff. Defaults to 2.0.
            retry_statuses (list, optional): HTTP status codes to retry on.
                                            Defaults to [429, 500, 502, 503, 504].
            **kwargs: Additional arguments to pass to the HTTP method.
            
        Returns:
            dict: Response JSON data.
            
        Raises:
            APIError: If all retries are exhausted.
            
        Example:
            # Retry on rate limit or server errors
            response = await api.request_with_retry(
                "post",
                "/users",
                max_retries=5,
                backoff_factor=1.5,
                data={"name": "John"}
            )
        """
        if retry_statuses is None:
            retry_statuses = [429, 500, 502, 503, 504]
        
        method_func = getattr(self, method.lower())
        
        for attempt in range(max_retries + 1):
            try:
                return await method_func(endpoint, **kwargs)
                
            except APIError as e:
                # Extract status code from error message if possible
                should_retry = any(str(status) in str(e) for status in retry_statuses)
                
                if attempt < max_retries and should_retry:
                    wait_time = backoff_factor ** attempt
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}/{max_retries + 1}). "
                        f"Retrying in {wait_time}s... Error: {e}"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Request failed after {attempt + 1} attempts")
                    raise
    
    # ========================================================================
    # PERFORMANCE TIMING
    # ========================================================================
    
    async def get_with_timing(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: int = 200
    ) -> Tuple[Dict[str, Any], float]:
        """
        Make GET request and return response with elapsed time.
        
        Args:
            endpoint (str): API endpoint.
            params (dict, optional): Query parameters.
            headers (dict, optional): Additional headers.
            expected_status (int): Expected HTTP status code.
            
        Returns:
            tuple: (response_data, elapsed_time_in_seconds)
            
        Example:
            response, elapsed = await api.get_with_timing("/users")
            assert elapsed < 2.0, f"API too slow: {elapsed}s"
        """
        start_time = time.time()
        response = await self.get(endpoint, params=params, headers=headers, expected_status=expected_status)
        elapsed = time.time() - start_time
        
        logger.info(f"GET {endpoint} completed in {elapsed:.3f}s")
        return response, elapsed
    
    async def post_with_timing(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_status: int = 201
    ) -> Tuple[Dict[str, Any], float]:
        """
        Make POST request and return response with elapsed time.
        
        Args:
            endpoint (str): API endpoint.
            data (dict, optional): Request body data.
            headers (dict, optional): Additional headers.
            expected_status (int): Expected HTTP status code.
            
        Returns:
            tuple: (response_data, elapsed_time_in_seconds)
            
        Example:
            response, elapsed = await api.post_with_timing("/users", data={...})
            assert elapsed < 1.0, f"Create too slow: {elapsed}s"
        """
        start_time = time.time()
        response = await self.post(endpoint, data=data, headers=headers, expected_status=expected_status)
        elapsed = time.time() - start_time
        
        logger.info(f"POST {endpoint} completed in {elapsed:.3f}s")
        return response, elapsed
    
    async def add_mock(self, pattern: str, response_body: str, status: int = 200, headers: dict = None):
        """
        Add a mock route to intercept API requests and return a custom response.
        Args:
            pattern (str): URL pattern to match (e.g., '**/users').
            response_body (str): JSON string or response body to return.
            status (int): HTTP status code for the mock response.
            headers (dict, optional): Response headers. Defaults to application/json.
        """
        async def handler(route, request):
            await route.fulfill(
                status=status,
                body=response_body,
                headers=headers or {"Content-Type": "application/json"}
            )

        await self.request.page.route(pattern, handler)