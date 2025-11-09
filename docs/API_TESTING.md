# API Testing Guide

Complete guide for API testing in this Playwright template. This template provides a powerful, flexible API client built on Playwright's native `APIRequestContext`.

---

## Table of Contents
1. [Quick Start](#quick-start)
2. [Authentication](#authentication)
3. [HTTP Methods](#http-methods)
4. [File Operations](#file-operations)
5. [Pagination](#pagination)
6. [Retry Logic](#retry-logic)
7. [Performance Testing](#performance-testing)
8. [Hybrid UI + API Testing](#hybrid-ui--api-testing)
9. [Best Practices](#best-practices)
10. [Complete Examples](#complete-examples)

---

## Quick Start

### Basic Setup

**1. Configure `.env`:**
```bash
API_BASE_URL=https://api.example.com
API_BEARER_TOKEN=your_token_here  # Optional
```

**2. Use in Tests:**
```python
@pytest.mark.asyncio
async def test_api(api_client):
    # Set authentication (if needed)
    await api_client.set_bearer_token(os.getenv("API_BEARER_TOKEN"))
    
    # Make requests
    response = await api_client.get("/users")
    assert response is not None
```

---

## Authentication

The API client supports multiple authentication methods. **You decide** when and how to authenticate.

### 1. Bearer Token (JWT/OAuth) - Most Common ⭐

```python
@pytest.mark.asyncio
async def test_bearer_auth(api_client):
    # From environment variable
    token = os.getenv("API_BEARER_TOKEN")
    await api_client.set_bearer_token(token)
    
    response = await api_client.get("/users/me")
```

**Use cases:** Modern APIs, OAuth 2.0, JWT tokens

---

### 2. API Key

```python
@pytest.mark.asyncio
async def test_api_key(api_client):
    # Default header (X-API-Key)
    await api_client.set_api_key(os.getenv("API_KEY"))
    
    # Custom header
    await api_client.set_api_key("your_key", header_name="Authorization")
```

**Use cases:** SaaS APIs (Stripe, SendGrid, Twilio, OpenAI)

---

### 3. Basic Authentication

```python
@pytest.mark.asyncio
async def test_basic_auth(api_client):
    await api_client.set_basic_auth("admin", "password123")
    response = await api_client.get("/admin/settings")
```

**Use cases:** Legacy APIs, admin endpoints

---

### 4. Login Flow (Dynamic Tokens)

```python
@pytest.mark.asyncio
async def test_login_flow(api_client):
    # Login to get token
    login_resp = await api_client.post(
        "/auth/login",
        data={"username": "test", "password": "test"}
    )
    
    # Extract and use token
    token = login_resp["access_token"]
    await api_client.set_bearer_token(token)
    
    # Make authenticated requests
    user_data = await api_client.get("/users/me")
```

**Use cases:** Testing your own API

---

### 5. Custom Headers

```python
@pytest.mark.asyncio
async def test_custom_headers(api_client):
    await api_client.set_extra_headers({
        "X-Tenant-ID": "tenant-123",
        "X-API-Version": "v2",
        "Authorization": "Custom xyz789"
    })
```

**Use cases:** Multi-tenant apps, API versioning, custom auth schemes

---

### 6. Clear Authentication

```python
@pytest.mark.asyncio
async def test_public_endpoint(api_client):
    await api_client.clear_auth()
    health = await api_client.get("/health")
```

---

## HTTP Methods

All standard HTTP methods with built-in validation.

### GET
```python
response = await api_client.get(
    "/users/123",
    params={"include": "profile"},
    headers={"X-Custom": "value"},
    expected_status=200
)
```

### POST
```python
response = await api_client.post(
    "/users",
    data={"name": "John", "email": "john@example.com"},
    expected_status=201
)
```

### PUT
```python
response = await api_client.put(
    "/users/123",
    data={"name": "John Updated"},
    expected_status=200
)
```

### PATCH
```python
response = await api_client.patch(
    "/users/123",
    data={"email": "newemail@example.com"},
    expected_status=200
)
```

### DELETE
```python
response = await api_client.delete(
    "/users/123",
    expected_status=204
)
```

---

## File Operations

### File Upload

Upload files using multipart/form-data:

```python
@pytest.mark.asyncio
async def test_upload(api_client):
    response = await api_client.upload_file(
        endpoint="/users/profile/avatar",
        file_path="test_data/image.jpg",
        field_name="avatar",
        data={"user_id": "123", "public": "true"}
    )
    
    assert response["file_url"] is not None
```

**Supported file types:**
- Images: `.jpg`, `.jpeg`, `.png`, `.gif`
- Documents: `.pdf`, `.txt`, `.csv`, `.json`, `.xml`
- Archives: `.zip`
- Auto-detects MIME type from extension

---

### File Download

Download files from API endpoints:

```python
@pytest.mark.asyncio
async def test_download(api_client):
    file_path = await api_client.download_file(
        endpoint="/reports/monthly",
        save_path="downloads/report.pdf",
        params={"month": "2025-01"}
    )
    
    # Verify download
    assert Path(file_path).exists()
    assert Path(file_path).stat().st_size > 0
```

**Features:**
- Auto-creates parent directories
- Returns path to downloaded file
- Supports query parameters

---

## Pagination

Automatically fetch all pages from paginated endpoints.

### Basic Pagination

```python
@pytest.mark.asyncio
async def test_pagination(api_client):
    # Response format: {"data": [...], "total": 500}
    all_users = await api_client.get_paginated(
        endpoint="/users",
        page_param="page",
        limit_param="per_page",
        limit=50,
        data_key="data"
    )
    
    print(f"Fetched {len(all_users)} total users")
```

---

### Pagination with Limits

```python
# Fetch only first 3 pages
limited_items = await api_client.get_paginated(
    endpoint="/products",
    limit=20,
    max_pages=3,
    data_key="items"
)
```

---

### Simple Array Response

```python
# When API returns array directly: [...]
all_items = await api_client.get_paginated(
    endpoint="/items",
    data_key=None  # No wrapper object
)
```

---

### Custom Pagination Parameters

```python
# Different API pagination styles
all_data = await api_client.get_paginated(
    endpoint="/data",
    page_param="pageNumber",      # Custom page param
    limit_param="pageSize",       # Custom limit param
    limit=100,
    data_key="results"
)
```

**Features:**
- Auto-detects when to stop (empty page or fewer items than limit)
- Configurable page/limit parameter names
- Optional max pages limit
- Supports both array and object responses

---

## Retry Logic

Automatic retry with exponential backoff for handling rate limits and server errors.

### Basic Retry

```python
@pytest.mark.asyncio
async def test_with_retry(api_client):
    # Will retry on 429, 500, 502, 503, 504
    response = await api_client.request_with_retry(
        method="get",
        endpoint="/users/me",
        max_retries=3,
        backoff_factor=2.0
    )
```

**Default retry statuses:**
- `429` - Too Many Requests (rate limit)
- `500` - Internal Server Error
- `502` - Bad Gateway
- `503` - Service Unavailable
- `504` - Gateway Timeout

---

### Custom Retry Configuration

```python
# Custom retry behavior
response = await api_client.request_with_retry(
    method="post",
    endpoint="/users",
    max_retries=5,
    backoff_factor=1.5,
    retry_statuses=[429, 500, 503],
    data={"name": "John"}
)
```

**Backoff calculation:** `wait_time = backoff_factor ^ attempt`
- Attempt 1: 1.5^0 = 1s
- Attempt 2: 1.5^1 = 1.5s
- Attempt 3: 1.5^2 = 2.25s

---

### Handling Rate Limits

```python
# Make multiple requests with auto-retry on rate limit
for i in range(100):
    response = await api_client.request_with_retry(
        method="get",
        endpoint=f"/users/{i}",
        max_retries=5
    )
```

---

## Performance Testing

Measure API response times for SLA validation and performance regression testing.

### GET with Timing

```python
@pytest.mark.asyncio
async def test_performance(api_client):
    response, elapsed = await api_client.get_with_timing("/users")
    
    assert elapsed < 2.0, f"API too slow: {elapsed:.3f}s"
```

---

### POST with Timing

```python
response, elapsed = await api_client.post_with_timing(
    "/users",
    data={"name": "Test"}
)

assert elapsed < 1.0, f"Create too slow: {elapsed:.3f}s"
```

---

### Compare Multiple Endpoints

```python
@pytest.mark.asyncio
async def test_endpoint_performance(api_client):
    endpoints = ["/users", "/products", "/orders"]
    timings = {}
    
    for endpoint in endpoints:
        response, elapsed = await api_client.get_with_timing(endpoint)
        timings[endpoint] = elapsed
    
    # Log performance comparison
    for endpoint, time in timings.items():
        print(f"{endpoint}: {time:.3f}s")
    
    # Assert SLA compliance
    assert all(t < 3.0 for t in timings.values()), "SLA violated"
```

---

## Hybrid UI + API Testing

Combine UI and API testing to ensure consistency.

### Extract Token from UI Login

```python
@pytest.mark.asyncio
async def test_ui_api_hybrid(page, api_client):
    from pages.base_page import BasePage
    
    base_page = BasePage(page)
    
    # 1. Login via UI
    await page.goto(f"{os.getenv('BASE_URL')}/login")
    await page.fill("#username", "test_user")
    await page.fill("#password", "test_pass")
    await page.click("button[type='submit']")
    await page.wait_for_url("**/dashboard")
    
    # 2. Extract token from browser storage
    token = await base_page.get_local_storage('access_token')
    
    # 3. Use token for API testing
    await api_client.set_bearer_token(token)
    
    # 4. Verify UI and API data match
    api_user = await api_client.get("/users/me")
    ui_username = await page.text_content(".username")
    
    assert api_user["username"] == ui_username
```

**Use cases:**
- Verify UI and API use same auth
- Test that UI displays same data as API returns
- Performance comparison (UI vs API)

---

## Best Practices

### ✅ DO

1. **Store tokens in `.env`**
```python
token = os.getenv("API_BEARER_TOKEN")
await api_client.set_bearer_token(token)
```

2. **Use explicit authentication**
```python
# Good - clear and explicit
await api_client.set_bearer_token(token)
response = await api_client.get("/users")
```

3. **Validate response structure**
```python
response = await api_client.get("/users/123")
assert "id" in response
assert "email" in response
assert response["id"] == 123
```

4. **Use retry for flaky endpoints**
```python
response = await api_client.request_with_retry(
    "get", "/external-api/data", max_retries=3
)
```

5. **Test performance for critical paths**
```python
response, elapsed = await api_client.post_with_timing("/checkout", data={...})
assert elapsed < 2.0, "Checkout too slow"
```

---

### ❌ DON'T

1. **Don't hardcode tokens**
```python
# Bad
await api_client.set_bearer_token("eyJhbGci...")  # ❌
```

2. **Don't ignore expected_status**
```python
# Bad - no validation
response = await api_client.get("/users")  # ❌

# Good - validate status
response = await api_client.get("/users", expected_status=200)  # ✅
```

3. **Don't commit `.env` file**
```bash
# Add to .gitignore
.env  # ✅
```

4. **Don't fetch unlimited pages without limit**
```python
# Risky - could fetch millions of records
all_data = await api_client.get_paginated("/logs")  # ⚠️

# Better - set max pages
all_data = await api_client.get_paginated("/logs", max_pages=10)  # ✅
```

---

## Complete Examples

### Example 1: Full CRUD Workflow

```python
@pytest.mark.asyncio
async def test_complete_crud(api_client):
    # Login
    login_resp = await api_client.post(
        "/auth/login",
        data={"username": "test", "password": "test"}
    )
    await api_client.set_bearer_token(login_resp["token"])
    
    # Create
    user = await api_client.post(
        "/users",
        data={"name": "John", "email": "john@example.com"}
    )
    user_id = user["id"]
    
    # Read
    fetched = await api_client.get(f"/users/{user_id}")
    assert fetched["name"] == "John"
    
    # Update
    updated = await api_client.put(
        f"/users/{user_id}",
        data={"name": "John Updated"}
    )
    assert updated["name"] == "John Updated"
    
    # Delete
    await api_client.delete(f"/users/{user_id}")
```

---

### Example 2: Performance Testing Suite

```python
@pytest.mark.asyncio
async def test_api_performance_suite(api_client):
    await api_client.set_bearer_token(os.getenv("API_BEARER_TOKEN"))
    
    # Test read performance
    users, read_time = await api_client.get_with_timing("/users")
    assert read_time < 1.0, f"Read too slow: {read_time}s"
    
    # Test create performance
    new_user, create_time = await api_client.post_with_timing(
        "/users",
        data={"name": "Perf Test", "email": "perf@test.com"}
    )
    assert create_time < 0.5, f"Create too slow: {create_time}s"
    
    # Test update performance
    user_id = new_user["id"]
    updated, update_time = await api_client.put_with_timing(
        f"/users/{user_id}",
        data={"name": "Updated"}
    )
    assert update_time < 0.5, f"Update too slow: {update_time}s"
    
    # Cleanup
    await api_client.delete(f"/users/{user_id}")
```

---

### Example 3: Complete Workflow with All Features

```python
@pytest.mark.asyncio
async def test_complete_workflow(api_client):
    # 1. Login
    login = await api_client.post("/auth/login", data={...})
    await api_client.set_bearer_token(login["token"])
    
    # 2. Create with timing
    user, time = await api_client.post_with_timing("/users", data={...})
    assert time < 1.0
    
    # 3. Upload file
    upload = await api_client.upload_file(
        f"/users/{user['id']}/avatar",
        "test_data/avatar.jpg"
    )
    
    # 4. Fetch all with pagination
    all_users = await api_client.get_paginated("/users", limit=50)
    assert any(u["id"] == user["id"] for u in all_users)
    
    # 5. Update with retry (handles rate limits)
    updated = await api_client.request_with_retry(
        "put",
        f"/users/{user['id']}",
        data={"name": "Updated"},
        max_retries=3
    )
    
    # 6. Download report
    report = await api_client.download_file(
        f"/users/{user['id']}/report",
        "downloads/report.pdf"
    )
    assert Path(report).exists()
    
    # 7. Cleanup
    await api_client.delete(f"/users/{user['id']}")
```

---

## Environment Variables Reference

```bash
# Required
API_BASE_URL=https://api.example.com

# Authentication (choose based on your API)
API_BEARER_TOKEN=your_jwt_token
API_KEY=your_api_key
API_USERNAME=test_user
API_PASSWORD=test_password
```

---

## API Client Methods Reference

### HTTP Methods
- `get(endpoint, params, headers, expected_status)`
- `post(endpoint, data, headers, expected_status)`
- `put(endpoint, data, headers, expected_status)`
- `patch(endpoint, data, headers, expected_status)`
- `delete(endpoint, headers, expected_status)`

### Authentication
- `set_bearer_token(token)`
- `set_api_key(api_key, header_name)`
- `set_basic_auth(username, password)`
- `set_extra_headers(headers_dict)`
- `clear_auth()`

### File Operations
- `upload_file(endpoint, file_path, field_name, data, expected_status)`
- `download_file(endpoint, save_path, params, expected_status)`

### Pagination
- `get_paginated(endpoint, page_param, limit_param, limit, max_pages, data_key, headers)`

### Retry
- `request_with_retry(method, endpoint, max_retries, backoff_factor, retry_statuses, **kwargs)`

### Performance
- `get_with_timing(endpoint, params, headers, expected_status)`
- `post_with_timing(endpoint, data, headers, expected_status)`

---

## Summary

This template provides **production-ready API testing** with:

✅ **Flexible Authentication** - Bearer, API Key, Basic, Custom  
✅ **All HTTP Methods** - GET, POST, PUT, PATCH, DELETE  
✅ **File Operations** - Upload/download with auto MIME detection  
✅ **Smart Pagination** - Auto-fetch all pages  
✅ **Retry Logic** - Exponential backoff for rate limits  
✅ **Performance Testing** - Built-in timing measurements  
✅ **Hybrid Testing** - Combine UI + API seamlessly  

**Philosophy:** Simple, explicit, flexible. No magic - just clean tools you control.
