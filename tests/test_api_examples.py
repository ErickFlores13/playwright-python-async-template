"""
API Testing Examples

Comprehensive examples showing all API testing capabilities in this template:
- Authentication (Bearer, API Key, Basic)
- CRUD operations
- File upload/download
- Pagination
- Retry logic
- Performance testing
- Hybrid UI + API testing
"""

import pytest
import os
from pathlib import Path
from helpers.api_client import APIClient


# ============================================================================
# Example 1: Bearer Token from Environment Variable (Recommended)
# ============================================================================
@pytest.mark.asyncio
async def test_bearer_token_from_env(api_client: APIClient):
    """
    Most common approach: Store token in .env, use in tests.
    
    .env file:
        API_BEARER_TOKEN=eyJhbGci...
    """
    # Get token from environment
    token = os.getenv("API_BEARER_TOKEN")
    if token:
        await api_client.set_bearer_token(token)
    
    # Make authenticated requests
    response = await api_client.get("/users/me")
    assert "email" in response


# ============================================================================
# Example 2: Login Flow to Get Token (Very Common)
# ============================================================================
@pytest.mark.asyncio
async def test_login_to_get_token(api_client: APIClient):
    """
    Login with credentials to get a JWT token, then use it.
    
    This is the most realistic scenario for testing your own APIs.
    """
    # Login to get token (no auth needed for login endpoint)
    login_response = await api_client.post(
        "/auth/login",
        data={
            "username": os.getenv("TEST_USERNAME"),
            "password": os.getenv("TEST_PASSWORD")
        }
    )
    
    # Extract token from response
    token = login_response["access_token"]
    
    # Set token for subsequent requests
    await api_client.set_bearer_token(token)
    
    # Now make authenticated requests
    user_data = await api_client.get("/users/me")
    assert user_data["username"] == os.getenv("TEST_USERNAME")


# ============================================================================
# Example 3: API Key for Third-Party APIs
# ============================================================================
@pytest.mark.asyncio
async def test_api_key_authentication(api_client: APIClient):
    """
    Use API key for SaaS services (Stripe, SendGrid, etc.).
    
    .env file:
        API_KEY=sk_test_abc123xyz
    """
    api_key = os.getenv("API_KEY")
    if api_key:
        # Default header name (X-API-Key)
        await api_client.set_api_key(api_key)
        
        # Or custom header name
        # await api_client.set_api_key(api_key, header_name="Authorization")
    
    response = await api_client.get("/account")
    assert response is not None


# ============================================================================
# Example 4: No Authentication (Public Endpoints)
# ============================================================================
@pytest.mark.asyncio
async def test_public_endpoint(api_client: APIClient):
    """
    Test public endpoints without authentication.
    """
    # No auth setup needed
    response = await api_client.get("/health")
    assert response["status"] == "healthy"


# ============================================================================
# Example 5: Switching Between Authenticated and Public Endpoints
# ============================================================================
@pytest.mark.asyncio
async def test_mixed_auth_endpoints(api_client: APIClient):
    """
    Some tests need to call both public and private endpoints.
    """
    # Test public endpoint first
    health = await api_client.get("/health")
    assert health["status"] == "healthy"
    
    # Login to get token
    login_resp = await api_client.post(
        "/auth/login",
        data={"username": "test", "password": "test"}
    )
    await api_client.set_bearer_token(login_resp["token"])
    
    # Test private endpoint
    user_data = await api_client.get("/users/me")
    assert user_data is not None
    
    # Clear auth and test public endpoint again
    await api_client.clear_auth()
    health2 = await api_client.get("/health")
    assert health2["status"] == "healthy"


# ============================================================================
# Example 6: Custom Headers (Multi-Tenant, Request IDs, etc.)
# ============================================================================
@pytest.mark.asyncio
async def test_custom_headers(api_client: APIClient):
    """
    APIs requiring additional headers beyond authentication.
    """
    # Set authentication
    await api_client.set_bearer_token(os.getenv("API_BEARER_TOKEN"))
    
    # Add custom headers for tenant, tracing, etc.
    await api_client.set_extra_headers({
        "X-Tenant-ID": "tenant-123",
        "X-Request-ID": "req-456",
        "X-API-Version": "v2"
    })
    
    response = await api_client.get("/tenant/data")
    assert response is not None


# ============================================================================
# Example 7: Testing with Multiple User Roles
# ============================================================================
@pytest.mark.asyncio
async def test_multiple_user_roles(api_client: APIClient):
    """
    Test the same endpoint with different user tokens.
    """
    # Login as admin
    admin_login = await api_client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin_pass"}
    )
    await api_client.set_bearer_token(admin_login["token"])
    
    # Admin can access all users
    all_users = await api_client.get("/admin/users")
    assert len(all_users) > 0
    
    # Login as regular user
    user_login = await api_client.post(
        "/auth/login",
        data={"username": "user", "password": "user_pass"}
    )
    await api_client.set_bearer_token(user_login["token"])
    
    # Regular user can only access their own data
    my_data = await api_client.get("/users/me")
    assert my_data["role"] == "user"
    
    # Regular user cannot access admin endpoint
    with pytest.raises(Exception):  # Should raise APIError with 403
        await api_client.get("/admin/users", expected_status=403)


# ============================================================================
# Example 8: Token Refresh Flow
# ============================================================================
@pytest.mark.asyncio
async def test_token_refresh_flow(api_client: APIClient):
    """
    Handle token expiration and refresh.
    """
    # Initial login
    login_resp = await api_client.post(
        "/auth/login",
        data={"username": "test", "password": "test"}
    )
    
    access_token = login_resp["access_token"]
    refresh_token = login_resp["refresh_token"]
    
    await api_client.set_bearer_token(access_token)
    
    # Use access token
    user_data = await api_client.get("/users/me")
    assert user_data is not None
    
    # Simulate token expiration - refresh it
    refresh_resp = await api_client.post(
        "/auth/refresh",
        data={"refresh_token": refresh_token}
    )
    
    new_access_token = refresh_resp["access_token"]
    await api_client.set_bearer_token(new_access_token)
    
    # Continue using new token
    user_data2 = await api_client.get("/users/me")
    assert user_data2 is not None


# ============================================================================
# Example 9: Extract Token from UI Login (Hybrid Testing)
# ============================================================================
@pytest.mark.asyncio
async def test_ui_login_extract_token_for_api(page, api_client: APIClient):
    """
    Login via UI, extract token, use it for API testing.
    
    This ensures UI and API use the same authentication.
    """
    from pages.base_page import BasePage
    
    base_page = BasePage(page)
    
    # Login via UI
    await page.goto(f"{os.getenv('BASE_URL')}/login")
    await page.fill("#username", os.getenv("TEST_USERNAME"))
    await page.fill("#password", os.getenv("TEST_PASSWORD"))
    await page.click("button[type='submit']")
    
    # Wait for login to complete
    await page.wait_for_url("**/dashboard")
    
    # Extract token from browser storage using BasePage method
    token = await base_page.get_local_storage('access_token')
    
    # Use same token for API testing
    await api_client.set_bearer_token(token)
    
    # Verify API returns same user data as UI
    api_user_data = await api_client.get("/users/me")
    ui_username = await page.text_content(".username-display")
    
    assert api_user_data["username"] == ui_username.strip()


# ============================================================================
# Example 10: Basic Authentication (Legacy/Admin APIs)
# ============================================================================
@pytest.mark.asyncio
async def test_basic_authentication(api_client: APIClient):
    """
    Basic authentication for legacy or admin APIs.
    """
    await api_client.set_basic_auth(
        username=os.getenv("API_USERNAME", "admin"),
        password=os.getenv("API_PASSWORD", "admin")
    )
    
    response = await api_client.get("/admin/settings")
    assert response is not None


# ============================================================================
# FILE UPLOAD & DOWNLOAD EXAMPLES
# ============================================================================
@pytest.mark.asyncio
async def test_file_upload(api_client: APIClient):
    """
    Upload a file to the API.
    
    Use case: Profile pictures, document uploads, CSV imports
    """
    # Set authentication
    token = os.getenv("API_BEARER_TOKEN")
    if token:
        await api_client.set_bearer_token(token)
    
    # Upload file
    response = await api_client.upload_file(
        endpoint="/users/profile/avatar",
        file_path="test_data/sample_image.jpg",
        field_name="avatar",
        data={"user_id": "123", "public": "true"}
    )
    
    assert response["file_url"] is not None
    assert "avatar" in response["file_url"]


@pytest.mark.asyncio
async def test_file_download(api_client: APIClient):
    """
    Download a file from the API.
    
    Use case: Export reports, download generated PDFs, CSV exports
    """
    # Set authentication
    token = os.getenv("API_BEARER_TOKEN")
    if token:
        await api_client.set_bearer_token(token)
    
    # Download file
    file_path = await api_client.download_file(
        endpoint="/reports/monthly/export",
        save_path="downloads/report.pdf",
        params={"month": "2025-01", "format": "pdf"}
    )
    
    # Verify file was downloaded
    assert Path(file_path).exists()
    assert Path(file_path).stat().st_size > 0


# ============================================================================
# PAGINATION EXAMPLES
# ============================================================================
@pytest.mark.asyncio
async def test_pagination_fetch_all(api_client: APIClient):
    """
    Automatically fetch all pages from a paginated endpoint.
    
    Use case: Export all data, bulk operations, data analysis
    """
    token = os.getenv("API_BEARER_TOKEN")
    if token:
        await api_client.set_bearer_token(token)
    
    # Fetch all users (response format: {"data": [...], "total": 500})
    all_users = await api_client.get_paginated(
        endpoint="/users",
        page_param="page",
        limit_param="per_page",
        limit=50,
        data_key="data"
    )
    
    assert len(all_users) > 0
    assert isinstance(all_users, list)


@pytest.mark.asyncio
async def test_pagination_with_limit(api_client: APIClient):
    """
    Fetch only a specific number of pages.
    
    Use case: Testing pagination logic, sampling data
    """
    token = os.getenv("API_BEARER_TOKEN")
    if token:
        await api_client.set_bearer_token(token)
    
    # Fetch only first 3 pages
    limited_items = await api_client.get_paginated(
        endpoint="/products",
        limit=20,
        max_pages=3,
        data_key="items"
    )
    
    # Should have at most 60 items (3 pages * 20 per page)
    assert len(limited_items) <= 60


@pytest.mark.asyncio
async def test_pagination_simple_array_response(api_client: APIClient):
    """
    Pagination when API returns array directly (no wrapper object).
    
    Response format: [...]
    """
    token = os.getenv("API_BEARER_TOKEN")
    if token:
        await api_client.set_bearer_token(token)
    
    all_items = await api_client.get_paginated(
        endpoint="/items",
        data_key=None  # Response is array directly
    )
    
    assert isinstance(all_items, list)


# ============================================================================
# RETRY LOGIC EXAMPLES
# ============================================================================
@pytest.mark.asyncio
async def test_request_with_retry(api_client: APIClient):
    """
    Retry request on failure with exponential backoff.
    
    Use case: Rate-limited APIs, flaky networks, eventual consistency
    """
    token = os.getenv("API_BEARER_TOKEN")
    if token:
        await api_client.set_bearer_token(token)
    
    # Will retry on 429, 500, 502, 503, 504 status codes
    response = await api_client.request_with_retry(
        method="get",
        endpoint="/users/me",
        max_retries=3,
        backoff_factor=1.5
    )
    
    assert response is not None


@pytest.mark.asyncio
async def test_retry_on_rate_limit(api_client: APIClient):
    """
    Handle rate-limited APIs with retry logic.
    """
    token = os.getenv("API_BEARER_TOKEN")
    if token:
        await api_client.set_bearer_token(token)
    
    # Make multiple requests - will auto-retry if rate limited
    for i in range(5):
        response = await api_client.request_with_retry(
            method="get",
            endpoint=f"/users/{i+1}",
            max_retries=5,
            backoff_factor=2.0
        )
        assert response is not None


# ============================================================================
# PERFORMANCE TESTING EXAMPLES
# ============================================================================
@pytest.mark.asyncio
async def test_api_response_time(api_client: APIClient):
    """
    Measure API response time for performance testing.
    
    Use case: SLA validation, performance regression testing
    """
    token = os.getenv("API_BEARER_TOKEN")
    if token:
        await api_client.set_bearer_token(token)
    
    # GET with timing
    response, elapsed = await api_client.get_with_timing("/users")
    
    assert response is not None
    assert elapsed < 2.0, f"API response too slow: {elapsed:.3f}s (expected < 2s)"


@pytest.mark.asyncio
async def test_create_performance(api_client: APIClient):
    """
    Test create operation performance.
    """
    token = os.getenv("API_BEARER_TOKEN")
    if token:
        await api_client.set_bearer_token(token)
    
    # POST with timing
    response, elapsed = await api_client.post_with_timing(
        "/users",
        data={"name": "Test User", "email": "test@example.com"}
    )
    
    assert response is not None
    assert elapsed < 1.0, f"Create operation too slow: {elapsed:.3f}s"


@pytest.mark.asyncio
async def test_multiple_endpoints_performance(api_client: APIClient):
    """
    Compare performance across multiple endpoints.
    """
    token = os.getenv("API_BEARER_TOKEN")
    if token:
        await api_client.set_bearer_token(token)
    
    endpoints = ["/users", "/products", "/orders"]
    timings = {}
    
    for endpoint in endpoints:
        response, elapsed = await api_client.get_with_timing(endpoint)
        timings[endpoint] = elapsed
        assert elapsed < 3.0, f"{endpoint} too slow: {elapsed:.3f}s"
    
    # Log performance comparison
    slowest = max(timings, key=timings.get)
    print(f"\nPerformance Summary:")
    for endpoint, elapsed in timings.items():
        print(f"  {endpoint}: {elapsed:.3f}s")
    print(f"Slowest: {slowest} ({timings[slowest]:.3f}s)")


# ============================================================================
# COMBINED WORKFLOW EXAMPLES
# ============================================================================
@pytest.mark.asyncio
async def test_complete_workflow_with_all_features(api_client: APIClient):
    """
    Complete workflow using multiple API features together.
    
    Demonstrates: auth, CRUD, file upload, pagination, performance
    """
    # 1. Login to get token
    login_resp = await api_client.post(
        "/auth/login",
        data={"username": "test", "password": "test"}
    )
    await api_client.set_bearer_token(login_resp["token"])
    
    # 2. Create user with timing
    user_data, create_time = await api_client.post_with_timing(
        "/users",
        data={"name": "John Doe", "email": "john@example.com"}
    )
    user_id = user_data["id"]
    assert create_time < 1.0
    
    # 3. Upload profile picture
    upload_resp = await api_client.upload_file(
        f"/users/{user_id}/avatar",
        "test_data/avatar.jpg",
        field_name="file"
    )
    assert upload_resp["file_url"] is not None
    
    # 4. Fetch all users (pagination)
    all_users = await api_client.get_paginated(
        "/users",
        limit=50,
        data_key="data"
    )
    assert any(u["id"] == user_id for u in all_users)
    
    # 5. Update user with retry
    update_resp = await api_client.request_with_retry(
        "put",
        f"/users/{user_id}",
        data={"name": "John Updated"},
        max_retries=3
    )
    assert update_resp["name"] == "John Updated"
    
    # 6. Download user report
    report_path = await api_client.download_file(
        f"/users/{user_id}/report",
        f"downloads/user_{user_id}_report.pdf"
    )
    assert Path(report_path).exists()
    
    # 7. Delete user
    await api_client.delete(f"/users/{user_id}")
