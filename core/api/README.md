# API Framework - User Guide

**For:** QA Testers & SDETs
**Purpose:** Learn how to use the framework to automate API test cases

> **Maintaining/Extending the framework?** See [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)

## Table of Contents

- [Quick Start](#quick-start)
- [The Core Pattern](#the-core-pattern)
- [Authentication](#authentication)
- [Making Requests](#making-requests)
- [Response Validation](#response-validation)
- [Configuration Presets](#configuration-presets)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Create a Service Client

```python
from pydantic import BaseModel
from core.api import BaseAPIClient
from core.api.services.auth import BearerTokenAuth

class User(BaseModel):
    id: int
    name: str
    email: str

class UserServiceClient(BaseAPIClient):
    """Client for User Service API."""

    async def get_user(self, user_id: int) -> User:
        """Get user by ID."""
        response = await self.get(f'/users/{user_id}')
        return self.validation.validate_schema(response.data, User)

    async def create_user(self, name: str, email: str) -> User:
        """Create a new user."""
        response = await self.post('/users', data={
            'name': name,
            'email': email
        })
        return self.validation.validate_schema(response.data, User)
```

### 2. Use in Your Tests

```python
import pytest
from core.api.config import HTTPConfig
from core.api.services.auth import BearerTokenAuth

@pytest.fixture
async def user_service(context):
    """Create user service client with auth."""
    auth = BearerTokenAuth(token="your-api-token")

    return UserServiceClient(
        context.request,  # Playwright context from conftest
        base_url="https://api.example.com",
        http_config=HTTPConfig.standard(),
        auth_strategy=auth
    )

async def test_get_user(user_service):
    """Test getting a user."""
    user = await user_service.get_user(1)

    assert user.id == 1
    assert user.name
    assert user.email
```

---

## The Core Pattern

The framework uses a **3-layer architecture**:

```
┌────────────────────────────────────────┐
│  Service Clients (Your Code)          │  ← You write these
│  • create_user(), get_order(), etc.   │
│  • Business logic & validation         │
└────────────────────────────────────────┘
                 ↓ extends
┌────────────────────────────────────────┐
│  BaseAPIClient (Framework)             │  ← Framework provides
│  • get(), post(), put(), delete()      │
│  • Authentication                       │
│  • Response validation                 │
└────────────────────────────────────────┘
                 ↓ uses
┌────────────────────────────────────────┐
│  HTTPClient (Infrastructure)           │  ← Framework handles
│  • Retry logic                         │
│  • Logging/interceptors                │
│  • Timeout management                  │
└────────────────────────────────────────┘
```

**You focus on:** Business logic (creating users, orders, etc.)
**Framework handles:** HTTP mechanics, retries, auth, validation

---

## Authentication

### Bearer Token (JWT)

```python
from core.api.services.auth import BearerTokenAuth

auth = BearerTokenAuth(token="your-jwt-token")

# Or from environment
import os
auth = BearerTokenAuth(token=os.getenv('API_TOKEN'))
```

### API Key

```python
from core.api.services.auth import APIKeyAuth

# Default header: X-API-Key
auth = APIKeyAuth(api_key="sk_test_123456")

# Custom header
auth = APIKeyAuth(api_key="abc123", header_name="Authorization")
```

### Basic Auth

```python
from core.api.services.auth import BasicAuth

auth = BasicAuth(username="admin", password="password123")
```

### OAuth2 Client Credentials

```python
from core.api.services.auth import OAuth2ClientCredentialsAuth

auth = OAuth2ClientCredentialsAuth(
    client_id="your-client-id",
    client_secret="your-secret",
    token_url="https://auth.example.com/token"
)
```

### Custom Headers

```python
from core.api.services.auth import CustomHeaderAuth

auth = CustomHeaderAuth(headers={
    'X-API-Key': 'abc123',
    'X-Tenant-ID': 'tenant-456'
})
```

### Composite Auth (Multiple Strategies)

```python
from core.api.services.auth import CompositeAuth, BearerTokenAuth, CustomHeaderAuth

auth = CompositeAuth([
    BearerTokenAuth(token="jwt-token"),
    CustomHeaderAuth(headers={'X-Tenant-ID': 'tenant-123'})
])
```

### Switching Auth Mid-Test

```python
from core.api.services.auth import BearerTokenAuth

# Start with one auth
user_service.set_auth(BearerTokenAuth(token="user-token"))
await user_service.get_user(1)

# Switch to different auth
user_service.set_auth(BearerTokenAuth(token="admin-token"))
await user_service.delete_user(1)
```

---

## Making Requests

### GET Requests

```python
# Simple GET
response = await client.get('/users/1')
print(response.data)  # Parsed JSON

# GET with query parameters
response = await client.get('/users', params={
    'page': 1,
    'limit': 10,
    'status': 'active'
})
# Calls: GET /users?page=1&limit=10&status=active
```

### POST Requests

```python
# POST with JSON body
response = await client.post('/users', data={
    'name': 'John Doe',
    'email': 'john@example.com'
})

# POST with custom headers
response = await client.post('/users',
    data={'name': 'Jane'},
    headers={'X-Request-ID': 'abc123'}
)
```

### PUT/PATCH Requests

```python
# PUT - full update
response = await client.put('/users/1', data={
    'name': 'Updated Name',
    'email': 'updated@example.com'
})

# PATCH - partial update
response = await client.patch('/users/1', data={
    'name': 'New Name Only'
})
```

### DELETE Requests

```python
# Simple delete
response = await client.delete('/users/1')

# Delete with confirmation
response = await client.delete('/users/1', params={
    'confirm': 'true'
})
```

### Response Object

All methods return an `APIResponseWrapper`:

```python
response = await client.get('/users/1')

# Access response data
response.data           # Parsed JSON (dict/list)
response.status_code    # HTTP status (200, 404, etc.)
response.headers        # Response headers (dict)
response.elapsed_ms     # Request duration in milliseconds
response.is_success     # True if 2xx status
response.url            # Request URL
response.method         # HTTP method
```

---

## Response Validation

### Schema Validation (Pydantic)

**Recommended** for type safety:

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

# In your service client
async def get_user(self, user_id: int) -> User:
    response = await self.get(f'/users/{user_id}')
    return self.validation.validate_schema(response.data, User)

# Usage - fully type-safe!
user = await client.get_user(1)
print(user.name)  # IDE autocomplete works!
print(user.id)    # Type checking works!
```

### Status Code Validation

```python
# Validate specific status code
response = await client.get('/users/1')
self.validation.validate_status_code(response, expected=200)

# Validate success (2xx)
self.validation.validate_success(response)

# Multiple acceptable codes
self.validation.validate_status_code(response, expected=[200, 201])
```

### JSON Path Validation

Check if specific fields exist in response:

```python
response = await client.get('/users/1')

# Check field exists
self.validation.validate_json_path(response.data, 'user.email')

# Check field has specific value
self.validation.validate_json_path(
    response.data,
    'user.status',
    expected_value='active'
)

# Check nested fields
self.validation.validate_json_path(
    response.data,
    'user.address.city',
    expected_value='New York'
)
```

---

## Configuration Presets

The framework provides 3 pre-configured setups:

### 1. Standard (Default)

**Use for:** Most API testing scenarios

```python
from core.api.config import HTTPConfig

config = HTTPConfig.standard()
```

**Settings:**

- 3 retry attempts
- 30s request timeout
- Exponential backoff: 1s → 2s → 4s
- Logging enabled

### 2. External API

**Use for:** Third-party APIs (Stripe, AWS, etc.)

```python
config = HTTPConfig.external_api()
```

**Settings:**

- 5 retry attempts (more patient)
- 60s request timeout
- Slower backoff: 2s → 4s → 8s → 16s → 32s
- Better for unreliable external services

### 3. Local API

**Use for:** Local/Docker services

```python
config = HTTPConfig.local_api()
```

**Settings:**

- 1 retry attempt (fail fast)
- 10s request timeout
- Quick feedback for local development

### Custom Configuration

```python
from core.api.config import HTTPConfig, RetryConfig, TimeoutConfig

config = HTTPConfig(
    retry=RetryConfig(
        max_attempts=5,
        initial_delay=2.0
    ),
    timeout=TimeoutConfig(
        request_timeout=45.0
    ),
    base_headers={
        'User-Agent': 'MyTestFramework/1.0'
    }
)
```

---

## Common Patterns

### Pattern 1: CRUD Operations

```python
class UserServiceClient(BaseAPIClient):

    async def create_user(self, name: str, email: str) -> User:
        response = await self.post('/users', data={
            'name': name, 'email': email
        })
        return self.validation.validate_schema(response.data, User)

    async def get_user(self, user_id: int) -> User:
        response = await self.get(f'/users/{user_id}')
        return self.validation.validate_schema(response.data, User)

    async def update_user(self, user_id: int, **updates) -> User:
        response = await self.patch(f'/users/{user_id}', data=updates)
        return self.validation.validate_schema(response.data, User)

    async def delete_user(self, user_id: int) -> None:
        response = await self.delete(f'/users/{user_id}')
        self.validation.validate_status_code(response, expected=204)
```

### Pattern 2: List with Pagination

```python
async def list_users(self, page: int = 1, limit: int = 10) -> List[User]:
    response = await self.get('/users', params={
        'page': page,
        'limit': limit
    })

    # Validate and parse list of users
    users_data = response.data.get('users', [])
    return [User(**user) for user in users_data]
```

### Pattern 3: Search/Filter

```python
async def search_users(self, query: str, filters: dict = None) -> List[User]:
    params = {'q': query}
    if filters:
        params.update(filters)

    response = await self.get('/users/search', params=params)
    return [User(**u) for u in response.data]
```

### Pattern 4: Bulk Operations

```python
async def create_users_bulk(self, users: List[dict]) -> List[User]:
    response = await self.post('/users/bulk', data={'users': users})
    return [User(**u) for u in response.data]
```

---

## Best Practices

### ✅ DO: Use Type Hints

```python
async def get_user(self, user_id: int) -> User:
    """Return type helps with autocomplete and type checking."""
    ...
```

### ✅ DO: Validate Responses

```python
async def create_user(self, name: str) -> User:
    response = await self.post('/users', data={'name': name})
    # Always validate!
    return self.validation.validate_schema(response.data, User)
```

### ✅ DO: Use Environment Variables for Tokens

```python
import os

auth = AuthService.with_bearer_token(os.getenv('API_TOKEN'))
```

### ✅ DO: Create Fixtures for Reusable Clients

```python
@pytest.fixture
async def user_service(context):
    return UserServiceClient(
        context.request,
        base_url=os.getenv('USER_API_URL'),
        http_config=HTTPConfig.standard(),
        auth_strategy=AuthService.with_bearer_token(os.getenv('API_TOKEN'))
    )
```

### ❌ DON'T: Hardcode Tokens

```python
# BAD
auth = AuthService.with_bearer_token("abc123")  # Don't do this!

# GOOD
auth = AuthService.with_bearer_token(os.getenv('API_TOKEN'))
```

### ❌ DON'T: Skip Validation

```python
# BAD
async def get_user(self, user_id: int) -> User:
    response = await self.get(f'/users/{user_id}')
    return response.data  # No validation!

# GOOD
async def get_user(self, user_id: int) -> User:
    response = await self.get(f'/users/{user_id}')
    return self.validation.validate_schema(response.data, User)
```

### ❌ DON'T: Catch All Exceptions Silently

```python
# BAD
try:
    user = await client.get_user(1)
except:
    pass  # Hides real problems!

# GOOD - let exceptions bubble up or handle specifically
try:
    user = await client.get_user(1)
except APIError as e:
    logger.error(f"Failed to get user: {e}")
    raise  # Re-raise for test to fail properly
```

---

## Troubleshooting

### Issue: "Connection timeout"

**Cause:** Request taking too long

**Solutions:**

```python
# 1. Increase timeout
config = HTTPConfig(
    timeout=TimeoutConfig(request_timeout=60.0)
)

# 2. Check if service is running
# 3. Use local_api() config for local services
```

### Issue: "Validation failed"

**Cause:** Response doesn't match expected schema

**Solutions:**

```python
# 1. Print the response to see what you got
response = await client.get('/users/1')
print(response.data)  # See actual structure

# 2. Update your Pydantic model to match
class User(BaseModel):
    id: int
    name: str
    # Add missing fields here
```

### Issue: "Authentication failed (401)"

**Cause:** Invalid or missing authentication

**Solutions:**

```python
# 1. Check your token is valid
print(os.getenv('API_TOKEN'))

# 2. Verify auth is set
headers = await client.auth.get_auth_headers()
print(headers)  # Should show Authorization header

# 3. Try different auth method
auth = AuthService.with_api_key("key", header_name="X-API-Key")
```

### Issue: "All retries exhausted"

**Cause:** Service is down or endpoint doesn't exist

**Solutions:**

```python
# 1. Check endpoint exists
# GET https://api.example.com/users/1

# 2. Check service is running

# 3. Reduce retries for faster feedback
config = HTTPConfig.local_api()  # Only 1 retry
```

### Debugging: Enable Verbose Logging

```python
import logging

# See all HTTP requests/responses
logging.basicConfig(level=logging.DEBUG)

# Or specific logger
logging.getLogger('core.api.http_client').setLevel(logging.DEBUG)
logging.getLogger('core.api.services.interceptor').setLevel(logging.INFO)
```

**You'll see:**

```
[INFO] → GET https://api.example.com/users/1
[INFO] ← GET https://api.example.com/users/1 status=200 elapsed=245ms
```

---

## Next Steps

- **Need to extend the framework?** See [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)
- **Working with databases?** See [Database Testing Guide](../../docs/DATABASE_TESTING.md)
- **Example service client:** Check `services/user_service/api/user_client.py`

**Questions?** Check the logs - the interceptor shows every request/response!
