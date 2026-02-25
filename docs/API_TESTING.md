# API Testing Guide

Complete guide for REST API testing using the Playwright Python Async Framework.

> **Quick reference?** See [core/api/README.md](../core/api/README.md)  
> **Extending the framework?** See [core/api/DEVELOPER_GUIDE.md](../core/api/DEVELOPER_GUIDE.md)

---

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Service Client Pattern](#service-client-pattern)
- [HTTP Methods](#http-methods)
- [Authentication](#authentication)
- [Response Validation](#response-validation)
- [HTTP Configuration Presets](#http-configuration-presets)
- [conftest Fixtures](#conftest-fixtures)
- [Complete Examples](#complete-examples)

---

## Overview

The API testing layer wraps Playwright's `APIRequestContext` with a clean,
strategy-based client. The architecture has three layers:

```
Service Clients (your code)        e.g. UserServiceClient, OrderClient
        ↓ extends
BaseAPIClient (framework)          get(), post(), put(), patch(), delete()
        ↓ uses
HTTPClient (infrastructure)        retry logic, interceptors, timeouts
```

You focus on **business logic**; the framework handles HTTP mechanics.

---

## Quick Start

### 1. Create a Service Client

```python
from pydantic import BaseModel
from core.api.base_client import BaseAPIClient

class User(BaseModel):
    id: int
    name: str
    email: str

class UserServiceClient(BaseAPIClient):
    """Typed client for the User service."""

    async def list_users(self) -> list[User]:
        response = await self.get('/users')
        return [User(**u) for u in response.data]

    async def get_user(self, user_id: int) -> User:
        response = await self.get(f'/users/{user_id}')
        return self.validation.validate_schema(response.data, User)

    async def create_user(self, name: str, email: str) -> User:
        response = await self.post('/users', data={'name': name, 'email': email})
        return self.validation.validate_schema(response.data, User)

    async def delete_user(self, user_id: int) -> None:
        await self.delete(f'/users/{user_id}')
```

### 2. Use the `api_client` Fixture

A generic `api_client` fixture is available in every test via `conftest.py`:

```python
async def test_api_health(api_client):
    response = await api_client.get('/health')
    assert response.is_success
```

### 3. Create a Typed Service Fixture

For domain-specific clients, define a fixture in your test file or a
shared `conftest.py`:

```python
import pytest_asyncio
from core.api.services.auth import BearerTokenAuth

@pytest_asyncio.fixture
async def user_client(context):
    auth = BearerTokenAuth(token='my-jwt-token')
    return UserServiceClient(
        context.request,
        base_url='https://api.example.com',
        auth_strategy=auth,
    )

async def test_get_user(user_client):
    user = await user_client.get_user(1)
    assert user.id == 1
    assert user.name
```

---

## Service Client Pattern

Define one `BaseAPIClient` subclass per service/domain:

```python
class OrderServiceClient(BaseAPIClient):
    """Client for the Orders microservice."""

    async def create_order(self, items: list[dict]) -> dict:
        response = await self.post('/orders', data={'items': items}, expected_status=201)
        return response.data

    async def get_order(self, order_id: str) -> dict:
        response = await self.get(f'/orders/{order_id}')
        self.validation.validate_required_fields(response.data, ['id', 'status', 'items'])
        return response.data

    async def cancel_order(self, order_id: str) -> None:
        await self.delete(f'/orders/{order_id}', expected_status=[200, 204])
```

---

## HTTP Methods

All methods return an `APIResponseWrapper`:

```python
response.data         # Parsed JSON (dict or list), or plain text
response.status_code  # HTTP status code (int)
response.headers      # Response headers (dict)
response.elapsed_ms   # Request duration in milliseconds
response.is_success   # True for 2xx status codes
response.url          # Request URL
response.method       # HTTP method used
```

### GET

```python
# Simple fetch
response = await client.get('/users/1')

# With query parameters
response = await client.get('/users', params={'page': 1, 'per_page': 20, 'status': 'active'})

# Accept multiple status codes
response = await client.get('/users/99999', expected_status=[200, 404])
```

### POST

```python
response = await client.post('/users', data={
    'name': 'Alice',
    'email': 'alice@example.com',
    'role': 'editor',
})
# Default expected_status is 201
```

### PUT (full update)

```python
response = await client.put('/users/1', data={
    'id': 1,
    'name': 'Alice Updated',
    'email': 'alice.new@example.com',
})
```

### PATCH (partial update)

```python
response = await client.patch('/users/1', data={'email': 'new@example.com'})
```

### DELETE

```python
response = await client.delete('/users/1')
# Default expected_status is 204
```

### Custom Headers per Request

```python
response = await client.get(
    '/protected',
    headers={'X-Request-ID': 'trace-abc-123', 'X-Tenant': 'tenant-1'},
)
```

---

## Authentication

### Bearer Token

```python
from core.api.services.auth import BearerTokenAuth

auth = BearerTokenAuth(token='your-jwt-token')

# Or from environment (reads API_BEARER_TOKEN)
auth = BearerTokenAuth.from_env()

# Or lazy fetch via login endpoint
auth = BearerTokenAuth(
    playwright_context=context.request,
    api_url='https://api.example.com',
    auth_endpoint='/auth/token',
    credentials={'username': 'user', 'password': 'pass'},
    token_field='access_token',
)
```

### API Key

```python
from core.api.services.auth import APIKeyAuth

auth = APIKeyAuth(api_key='sk_test_123456')                    # header: X-API-Key
auth = APIKeyAuth(api_key='abc123', header_name='Authorization')  # custom header

# From environment (reads API_KEY and API_KEY_HEADER_NAME)
auth = APIKeyAuth.from_env()
```

### Basic Auth

```python
from core.api.services.auth import BasicAuth

auth = BasicAuth(username='admin', password='password123')

# From environment (reads API_USERNAME and API_PASSWORD)
auth = BasicAuth.from_env()
```

### OAuth2 Client Credentials

```python
from core.api.services.auth import OAuth2ClientCredentialsAuth

auth = OAuth2ClientCredentialsAuth(
    client_id='your-client-id',
    client_secret='your-secret',
    token_url='https://auth.example.com/oauth/token',
    scope='read write',           # optional
)
# Token is fetched and cached automatically; refreshed when expired.

# From environment (reads OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET, OAUTH_SCOPE)
auth = OAuth2ClientCredentialsAuth.from_env(
    token_url='https://auth.example.com/oauth/token'
)
```

### Refreshable Token

```python
from core.api.services.auth import RefreshableTokenAuth
import time

async def get_fresh_token():
    # Your refresh logic here
    return 'new-access-token'

auth = RefreshableTokenAuth(
    initial_token='current-token',
    refresh_callback=get_fresh_token,
    expires_at=time.time() + 3600,
)
```

### Custom Headers

```python
from core.api.services.auth import CustomHeaderAuth

auth = CustomHeaderAuth(headers={
    'X-API-Key':    'abc123',
    'X-Tenant-ID':  'tenant-456',
    'X-API-Version': 'v2',
})
```

### Composite (Multiple Strategies)

```python
from core.api.services.auth import CompositeAuth, BearerTokenAuth, CustomHeaderAuth

auth = CompositeAuth([
    BearerTokenAuth(token='jwt-token'),
    CustomHeaderAuth(headers={'X-Tenant-ID': 'tenant-1'}),
])
```

### Switching Auth Mid-Test

```python
from core.api.services.auth import BearerTokenAuth

client.set_bearer_token('admin-token')
await client.delete('/users/42')

client.set_bearer_token('regular-user-token')
response = await client.get('/users/me')
```

---

## Response Validation

### Schema Validation (Pydantic)

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
    status: str

user = self.validation.validate_schema(response.data, User)
print(user.name)   # IDE autocomplete works, type-safe access
assert user.status == 'active'
```

### Status Code Validation

```python
self.validation.validate_status_code(response, 200)
self.validation.validate_status_code(response, [200, 201])  # multiple acceptable
```

### Required Fields

```python
self.validation.validate_required_fields(
    response.data,
    ['id', 'name', 'email', 'created_at']
)
```

### JSON Path Validation

```python
# Assert a field exists
self.validation.validate_json_path(response.data, 'user.address.city')

# Assert a specific value
self.validation.validate_json_path(response.data, 'user.status', expected_value='active')

# Nested array access: items[0].price
self.validation.validate_json_path(response.data, 'items[0].price', expected_value=9.99)
```

### Type and Length Validation

```python
# Type check
self.validation.validate_response_type(response.data, list)
self.validation.validate_response_type(response.data, dict)

# List length
self.validation.validate_list_length(response.data, min_length=1)
self.validation.validate_list_length(response.data, min_length=1, max_length=100)
self.validation.validate_list_length(response.data, exact_length=10)
```

---

## HTTP Configuration Presets

Control retry and timeout behaviour with built-in presets:

| Preset | Use Case | Retries | Timeout |
|--------|----------|---------|---------|
| `HTTPConfig.standard()` | Most API testing | 3 | 30 s |
| `HTTPConfig.external_api()` | Third-party APIs (Stripe, AWS) | 5 | 60 s |
| `HTTPConfig.local_api()` | Localhost / Docker | 1 | 10 s |
| `HTTPConfig.testing()` | Fast unit tests | 1 | 5 s |

```python
from core.api.config import HTTPConfig

client = BaseAPIClient(context.request, 'https://api.example.com',
                       http_config=HTTPConfig.external_api())
```

Set the default preset via environment variable (applies to the `api_client` fixture):

```bash
HTTP_CONFIG_MODE=local_api   # Options: standard | external_api | local_api | testing
```

### Custom Configuration

```python
from core.api.config import HTTPConfig, RetryConfig, TimeoutConfig

config = HTTPConfig(
    retry=RetryConfig(max_attempts=5, initial_delay=2.0, max_delay=30.0),
    timeout=TimeoutConfig(request_timeout=45.0, connect_timeout=10.0),
    base_headers={'User-Agent': 'MyTestFramework/1.0'},
)
```

---

## conftest Fixtures

### `api_client` (generic)

Available in every test without any setup:

```python
async def test_create_resource(api_client):
    api_client.set_bearer_token('my-token')
    response = await api_client.post('/resources', data={'name': 'test'})
    assert response.status_code == 201
```

### `context` (Playwright browser context)

Used to create service-specific clients:

```python
@pytest_asyncio.fixture
async def order_client(context):
    return OrderServiceClient(
        context.request,
        base_url='https://orders.example.com',
        auth_strategy=BearerTokenAuth.from_env(),
    )
```

---

## Complete Examples

### Example 1: Full CRUD Test

```python
import pytest_asyncio
from pydantic import BaseModel
from core.api.base_client import BaseAPIClient
from core.api.services.auth import BearerTokenAuth

class Product(BaseModel):
    id: int
    name: str
    price: float
    in_stock: bool

class ProductClient(BaseAPIClient):
    async def create(self, name, price) -> Product:
        r = await self.post('/products', data={'name': name, 'price': price})
        return self.validation.validate_schema(r.data, Product)

    async def get(self, pid) -> Product:
        r = await self.get(f'/products/{pid}')
        return self.validation.validate_schema(r.data, Product)

    async def update(self, pid, **kw) -> Product:
        r = await self.patch(f'/products/{pid}', data=kw)
        return self.validation.validate_schema(r.data, Product)

    async def delete(self, pid) -> None:
        await self.delete(f'/products/{pid}')

@pytest_asyncio.fixture
async def products(context):
    return ProductClient(
        context.request,
        base_url='https://api.example.com',
        auth_strategy=BearerTokenAuth.from_env(),
    )

async def test_product_crud(products):
    # CREATE
    p = await products.create('Laptop', 999.99)
    assert p.id > 0

    # READ
    fetched = await products.get(p.id)
    assert fetched.name == 'Laptop'

    # UPDATE
    updated = await products.update(p.id, price=899.99)
    assert updated.price == 899.99

    # DELETE
    await products.delete(p.id)
```

### Example 2: Pagination

```python
async def get_all_users(client: BaseAPIClient) -> list[dict]:
    """Fetch all pages of users."""
    all_users = []
    page = 1
    while True:
        response = await client.get('/users', params={'page': page, 'per_page': 50})
        data = response.data
        if not data:
            break
        all_users.extend(data)
        if len(data) < 50:
            break
        page += 1
    return all_users

async def test_all_users_are_active(api_client):
    users = await get_all_users(api_client)
    assert all(u['status'] == 'active' for u in users)
```

### Example 3: Performance Gate

```python
async def test_api_response_time(api_client):
    response = await api_client.get('/health')
    assert response.elapsed_ms < 500, (
        f"Health check took {response.elapsed_ms}ms — SLA is 500ms"
    )
```

---

See [core/api/README.md](../core/api/README.md) for the full framework reference.
