# API Framework - Developer Guide

**For:** SDETs maintaining, enhancing, and extending the core API layer
**Purpose:** Understand architecture, design decisions, and how to add new capabilities

> **Just using the framework for tests?** See [README.md](./README.md)

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Design Principles](#design-principles)
- [Core Components Deep Dive](#core-components-deep-dive)
- [Extending the Framework](#extending-the-framework)
- [Design Decisions](#design-decisions)
- [Testing the Framework](#testing-the-framework)
- [Contributing Guidelines](#contributing-guidelines)
- [Common Maintenance Tasks](#common-maintenance-tasks)

---

## Architecture Overview

### The 3-Layer Pattern

```
┌─────────────────────────────────────────────────────┐
│ HTTPClient (Infrastructure Layer)                   │
│ • Owns Playwright APIRequestContext                 │
│ • Implements retry logic with exponential backoff   │
│ • Manages request/response interceptors             │
│ • Handles timeout management                        │
│ • Pure HTTP mechanics - no business logic           │
└─────────────────────────────────────────────────────┘
                        ▲
                        │ created internally by
                        │
┌─────────────────────────────────────────────────────┐
│ BaseAPIClient (Abstraction Layer)                   │
│ • Creates HTTPClient from playwright_context        │
│ • Provides get(), post(), put(), delete()           │
│ • Manages authentication strategies                 │
│ • Provides validation services                      │
│ • Template for service-specific clients             │
└─────────────────────────────────────────────────────┘
                        ▲
                        │ extended by
                        │
┌─────────────────────────────────────────────────────┐
│ Service Clients (Business Layer)                    │
│ • UserServiceClient, OrderServiceClient, etc.       │
│ • Domain-specific methods (create_user, etc.)       │
│ • Business validation using Pydantic                │
│ • Lives in services/ directory (not core/)          │
└─────────────────────────────────────────────────────┘
```

### Key Architectural Patterns

#### 1. Dependency Injection

**Problem:** How do service clients get their dependencies?

**Solution:** Constructor injection with Playwright context

```python
class BaseAPIClient:
    def __init__(
        self,
        playwright_context: APIRequestContext,  # From Playwright
        base_url: str,
        http_config: Optional[HTTPConfig] = None,
        auth_strategy: Optional[AuthStrategy] = None
    ):
        # Create HTTPClient internally
        self._http_client = HTTPClient(playwright_context, http_config or HTTPConfig.standard())
        self._auth = auth_strategy
        # ...
```

**Why:** Keeps service clients simple - they receive Playwright context from pytest fixtures, framework handles the rest.

#### 2. Strategy Pattern (Authentication)

**Problem:** Different APIs use different auth methods (JWT, API keys, Basic auth)

**Solution:** Pluggable auth strategies with facade for simplicity

```python
# Strategy Interface
class AuthStrategy(ABC):
    @abstractmethod
    async def get_auth_headers(self) -> Dict[str, str]:
        pass

# Concrete Strategies
class BearerTokenAuth(AuthStrategy):
    async def get_auth_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

class APIKeyAuth(AuthStrategy):
    async def get_auth_headers(self) -> Dict[str, str]:
        return {self.header_name: self.api_key}

```

**Why Strategy Pattern:**

- Add new auth types without changing existing code
- Strategies are composable (CompositeAuth)
- Direct instantiation keeps usage simple and explicit

#### 3. Composition Over Inheritance

**Problem:** HTTPClient and BaseAPIClient both need validation/interceptor services

**Solution:** Inject service instances instead of inheritance

```python
class HTTPClient:
    def __init__(self, context: APIRequestContext, config: HTTPConfig):
        self._context = context
        self._config = config
        # Compose services
        self._retry_service = RetryService(config.retry)
        self._interceptor = InterceptorService(config.interceptor)

class BaseAPIClient:
    def __init__(self, playwright_context, base_url, ...):
        self._http_client = HTTPClient(playwright_context, ...)
        # Compose different services
        self._validation = ValidationService()
```

**Why:** More flexible than inheritance - can swap implementations, easier to test

---

## Design Principles

### 1. YAGNI (You Aren't Gonna Need It)

**Applied:** Removed circuit breaker implementation

**Reasoning:**

```
Circuit Breaker is for production microservices:
- Handle 1000s of requests/second
- Prevent cascading failures across services
- Fast-fail when downstream is down

Test automation reality:
- Low request volume (dozens, not thousands)
- Need to see actual failures (not "circuit open")
- Each test should be independent
- One endpoint's failure shouldn't block others
```

**Decision:** Removed entirely - retry + interceptor is enough for automation

### 2. Separation of Concerns

**HTTPClient:** Pure HTTP mechanics

- Retry logic
- Timeout management
- Interceptors (logging)
- No knowledge of "users" or "orders"

**BaseAPIClient:** API abstraction

- get(), post(), put(), delete()
- Authentication
- Response validation
- Still no business logic

**Service Clients:** Business logic

- create_user(), get_order()
- Domain validation
- Pydantic models

**Why:** Each layer has one responsibility - easier to test and maintain

### 3. Fail Fast for Framework Code

**Validation strictness:**

```python
@dataclass
class RetryConfig:
    def __post_init__(self):
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        if self.initial_delay <= 0:
            raise ValueError("initial_delay must be > 0")
```

**Why:** Framework misconfiguration should error immediately, not fail mysteriously in tests

### 4. Explicit Over Implicit

**Bad (implicit):**

```python
client = BaseAPIClient("https://api.example.com")  # Where's config? Where's auth?
```

**Good (explicit):**

```python
from core.api.services.auth import BearerTokenAuth

client = BaseAPIClient(
    playwright_context,
    base_url="https://api.example.com",
    http_config=HTTPConfig.standard(),
    auth_strategy=BearerTokenAuth(token="token")
)
```

**Why:** Test automation code should be clear about what it's doing

---

## Core Components Deep Dive

### HTTPClient

**File:** `core/api/http_client.py`

**Responsibilities:**

1. Execute HTTP requests using Playwright APIRequestContext
2. Retry failed requests with exponential backoff
3. Log all requests/responses via interceptor
4. Handle timeouts
5. Convert Playwright responses to framework format

**Key Methods:**

```python
async def request(
    self,
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    data: Any = None,
    params: Optional[Dict[str, Any]] = None,
) -> APIResponseWrapper:
    """Execute HTTP request with retry logic."""

    # 1. Merge headers with config defaults
    final_headers = {**self._config.base_headers, **(headers or {})}

    # 2. Execute with retry
    response = await self._retry_service.execute_with_retry(
        self._execute_request,
        method, url, final_headers, data, params
    )

    return response

async def _execute_request(...) -> APIResponseWrapper:
    """Single request attempt (no retry)."""

    # 1. Request interceptor (logging, tracing)
    await self._interceptor.on_request(...)

    # 2. Make actual request via Playwright
    response = await self._context.fetch(url, ...)

    # 3. Response interceptor (logging, metrics)
    await self._interceptor.on_response(...)

    # 4. Convert to framework format
    return APIResponseWrapper(...)
```

**Services Used:**

- `RetryService`: Exponential backoff logic
- `Interceptor`: Request/response logging
- `TimeoutConfig`: Request timeout settings

**Design Notes:**

- Doesn't know about auth (HTTPClient is pure HTTP)
- Doesn't validate business logic (leaves that to BaseAPIClient)
- Playwright context is passed in (not created) - supports multiple contexts

### BaseAPIClient

**File:** `core/api/base_api_client.py`

**Responsibilities:**

1. Create HTTPClient from Playwright context
2. Provide HTTP method wrappers (get, post, etc.)
3. Manage authentication
4. Provide validation service
5. Build full URLs from base_url + path

**Key Methods:**

```python
async def get(self, path: str, params: Optional[Dict] = None, **kwargs):
    """GET request with auth."""
    headers = await self._get_headers(kwargs.get('headers'))
    url = self._build_url(path)
    return await self._http_client.request('GET', url, headers=headers, params=params)

async def post(self, path: str, data: Any = None, **kwargs):
    """POST request with auth."""
    headers = await self._get_headers(kwargs.get('headers'))
    url = self._build_url(path)
    return await self._http_client.request('POST', url, headers=headers, data=data)

async def _get_headers(self, extra_headers: Optional[Dict] = None) -> Dict:
    """Merge auth headers with extra headers."""
    auth_headers = await self._auth.get_auth_headers() if self._auth else {}
    return {**auth_headers, **(extra_headers or {})}
```

**Services Provided:**

- `self.validation`: ValidationService for response validation
- `self._auth`: Current auth strategy (can be swapped via set_auth())

**Design Notes:**

- All methods are async (follows Playwright's async API)
- Authentication is optional (some APIs don't need it)
- Validation is provided but not enforced (service clients decide what to validate)

### ValidationService

**File:** `core/api/services/validation.py`

**Responsibilities:**

1. Validate Pydantic schemas
2. Validate HTTP status codes
3. Validate JSON path existence/values
4. Validate required fields

**Key Methods:**

```python
def validate_schema(self, data: Any, model: Type[BaseModel]) -> BaseModel:
    """Validate data against Pydantic model."""
    try:
        return model(**data) if isinstance(data, dict) else model.parse_obj(data)
    except ValidationError as e:
        raise ValidationError(f"Schema validation failed: {e}")

def validate_status_code(self, response: APIResponseWrapper, expected: Union[int, List[int]]):
    """Validate HTTP status code."""
    expected_codes = [expected] if isinstance(expected, int) else expected
    if response.status_code not in expected_codes:
        raise ValidationError(
            f"Expected status {expected_codes}, got {response.status_code}"
        )

def validate_json_path(self, data: Any, path: str, expected_value: Any = None):
    """Validate nested JSON field exists and optionally has specific value."""
    # Supports dot notation: "user.address.city"
    # ...
```

**Design Notes:**

- All methods raise `ValidationError` on failure (fails fast)
- Works with any dict/list (not just API responses)
- JSON path uses simple dot notation (no JSONPath library needed)

### RetryService

**File:** `core/api/services/retry.py`

**Responsibilities:**

1. Implement exponential backoff with jitter
2. Decide which status codes/exceptions to retry
3. Log retry attempts

**Algorithm:**

```python
async def execute_with_retry(self, func, *args, **kwargs):
    """Execute function with exponential backoff."""

    for attempt in range(1, self.config.max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if not self._should_retry(e, attempt):
                raise

            delay = self._calculate_delay(attempt)
            logger.warning(f"Retry {attempt}/{self.config.max_attempts} after {delay}s")
            await asyncio.sleep(delay)

    raise RetryExhaustedError(...)

def _calculate_delay(self, attempt: int) -> float:
    """Exponential backoff: 1s → 2s → 4s → 8s → 16s..."""
    base_delay = self.config.initial_delay * (self.config.exponential_base ** (attempt - 1))
    capped_delay = min(base_delay, self.config.max_delay)

    if self.config.jitter:
        # Add 0-25% random jitter to avoid thundering herd
        jitter = capped_delay * random.uniform(0, 0.25)
        return capped_delay + jitter

    return capped_delay
```

**Retry Logic:**

- Network errors: Always retry
- 429 (rate limit), 500, 502, 503, 504: Retry
- 400, 401, 403, 404: Don't retry (client errors are permanent)

### InterceptorService

**File:** `core/api/services/interceptor.py`

**Responsibilities:**

1. Generate correlation IDs for request tracking
2. Log all requests (method, URL, headers, body)
3. Log all responses (status, elapsed time, body)
4. Support custom interceptors (for metrics, tracing, etc.)
5. Collect request metrics (timing, status codes)

**Key Methods:**

```python
async def before_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Any] = None
) -> Dict[str, Any]:
    """Intercept request before sending.

    Returns request context with:
    - correlation_id: Unique UUID for tracking
    - start_time: For calculating elapsed time
    - Adds X-Correlation-ID header if configured
    """

async def after_response(
    context: Dict[str, Any],
    response: APIResponseWrapper
) -> APIResponseWrapper:
    """Intercept response after receiving.

    Logs response details and calculates timing.
    """
```

**Configuration:**

```python
from core.api.config import InterceptorConfig

config = InterceptorConfig(
    enable_logging=True,
    enable_metrics=True,
    enable_tracing=True,
    add_correlation_header=True,
    correlation_header_name='X-Correlation-ID'
)
```

**Why Essential:**

- **Debugging:** See exact requests/responses in logs
- **Distributed Tracing:** Correlation IDs track requests across services
- **Performance:** Automatic timing metrics
- **Custom Logic:** Pluggable interceptors for team-specific needs

---

## Extending the Framework

### Adding a New Authentication Strategy

**Scenario:** Your API uses OAuth2 client credentials flow

**Step 1:** Create strategy in `core/api/services/auth/strategies/`

```python
# oauth2_client_credentials_strategy.py
from dataclasses import dataclass
from typing import Dict, Optional
import time
from core.api.services.auth.base_strategy import AuthStrategy

@dataclass
class OAuth2ClientCredentials(AuthStrategy):
    """OAuth2 client credentials authentication."""

    client_id: str
    client_secret: str
    token_url: str
    _access_token: Optional[str] = None
    _expires_at: Optional[float] = None

    async def get_auth_headers(self) -> Dict[str, str]:
        """Get auth headers, refreshing token if needed."""
        if not self._access_token or self._is_token_expired():
            await self._refresh_token()

        return {"Authorization": f"Bearer {self._access_token}"}

    async def _refresh_token(self):
        """Fetch new access token from OAuth2 server."""
        # Make request to token_url with client_id/client_secret
        # Parse response and update _access_token and _expires_at
        # ...

    def _is_token_expired(self) -> bool:
        """Check if token is expired or about to expire."""
        if not self._expires_at:
            return True
        # Refresh 5 minutes before expiration
        return time.time() >= (self._expires_at - 300)
```

**Step 2:** Export in `__init__.py`

```python
# core/api/services/auth/__init__.py
from .strategies.oauth2_client_credentials_strategy import OAuth2ClientCredentials

__all__ = [
    'AuthStrategy',
    'BearerTokenAuth',
    'OAuth2ClientCredentials',  # Add here
    # ...
]
```

**Step 3:** Use in tests

```python
from core.api.services.auth import OAuth2ClientCredentials

auth = OAuth2ClientCredentials(
    client_id="my-client-id",
    client_secret="my-secret",
    token_url="https://auth.example.com/token"
)

client = UserServiceClient(
    context.request,
    base_url="https://api.example.com",
    auth_strategy=auth
)
```

### Adding a New Validation Method

**Scenario:** Need to validate response headers

**Step 1:** Add method to `ValidationService`

```python
# core/api/services/validation.py
class ValidationService:
    # ... existing methods ...

    def validate_header(
        self,
        response: APIResponseWrapper,
        header_name: str,
        expected_value: Optional[str] = None
    ) -> str:
        """Validate response header exists and optionally has specific value."""
        if header_name not in response.headers:
            raise ValidationError(f"Header '{header_name}' not found in response")

        actual_value = response.headers[header_name]

        if expected_value is not None and actual_value != expected_value:
            raise ValidationError(
                f"Header '{header_name}' expected '{expected_value}', got '{actual_value}'"
            )

        return actual_value
```

**Step 2:** Use in service clients

```python
async def create_user(self, name: str) -> User:
    response = await self.post('/users', data={'name': name})

    # Validate header
    self.validation.validate_header(response, 'X-Rate-Limit-Remaining')

    # Validate body
    return self.validation.validate_schema(response.data, User)
```

### Adding a New Configuration Preset

**Scenario:** Need config for CI/CD environment (faster timeouts, fewer retries)

**Step 1:** Add class method to `HTTPConfig`

```python
# core/api/config.py
class HTTPConfig:
    # ... existing methods ...

    @classmethod
    def ci_environment(cls) -> 'HTTPConfig':
        """Configuration optimized for CI/CD pipelines.

        - Fail fast (2 retries)
        - Short timeouts (20s)
        - Quick feedback for build failures
        """
        return cls(
            retry=RetryConfig(
                max_attempts=2,  # Less patient than standard
                initial_delay=0.5,  # Faster retries
                max_delay=5.0
            ),
            timeout=TimeoutConfig(
                request_timeout=20.0  # Faster timeout
            ),
            base_headers={'User-Agent': 'CI-Test-Runner'}
        )
```

**Step 2:** Document in README

```markdown
### 4. CI Environment

**Use for:** CI/CD pipelines (Jenkins, GitHub Actions)

config = HTTPConfig.ci_environment()

**Settings:**
- 2 retry attempts (fail fast for quick feedback)
- 20s request timeout
- Optimized for build speed
```

---

## Design Decisions

### Why Playwright for HTTP?

**Alternatives:**

- `httpx`: Popular async HTTP library
- `aiohttp`: Another async HTTP library
- `requests`: Sync, would need threading

**Decision:** Use Playwright's APIRequestContext

**Reasoning:**

1. **Already a dependency:** Framework uses Playwright for UI testing
2. **Browser-like behavior:** Playwright handles cookies, redirects like browsers
3. **Context isolation:** Each Playwright context is isolated (parallel tests)
4. **Single async runtime:** No mixing asyncio libraries
5. **HAR recording:** Playwright can record all network traffic

**Trade-off:** Locked into Playwright (but that's already a dependency)

### Why Remove Circuit Breaker?

**Original reasoning for circuit breaker:**

- Prevent cascading failures in microservices
- Fail fast when downstream is overloaded
- Protect system from thundering herd

**Why it doesn't fit automation:**

| Production Systems | Test Automation |
|-------------------|----------------|
| 1000s of requests/sec | Dozens of requests/test |
| Shared across many callers | Isolated per test |
| One endpoint fails → protect others | Each endpoint tested independently |
| Need fast-fail to prevent cascades | Need to see actual failures |

**Real example:**

```python
# With circuit breaker (BAD for tests):
test_create_user()  # Fails - circuit opens
test_get_user()     # Skipped - circuit open
test_update_user()  # Skipped - circuit open
test_delete_user()  # Skipped - circuit open
# Result: 1 real failure → 4 test failures

# Without circuit breaker (GOOD for tests):
test_create_user()  # Fails - real error
test_get_user()     # Runs - may pass
test_update_user()  # Runs - may pass
test_delete_user()  # Runs - may pass
# Result: Clear view of which endpoints work
```

**Decision:** Removed in favor of retry + logging

### Why Direct Strategy Instantiation (No Facade)?

**With Facade (pre-refactor):**

```python
auth = AuthService.with_bearer_token("abc123")
# Extra layer, indirect
```

**Direct Strategies (current):**

```python
# Simple and explicit
auth = BearerTokenAuth(token="abc123")

# Clear what you're creating
auth = OAuth2ClientCredentialsAuth(
    client_id="id",
    client_secret="secret",
    token_url="url"
)
```

**Decision:** Direct instantiation - fewer layers, more explicit, simpler codebase

### Why Separate HTTPConfig Presets?

**Alternative:** Single config with parameters

```python
config = HTTPConfig(environment='external')  # Implicit settings
```

**Current:** Explicit presets

```python
config = HTTPConfig.external_api()  # Explicit settings
```

**Reasoning:**

1. **Discoverability:** IDE autocomplete shows all presets
2. **Documentation:** Each preset has clear docstring
3. **Explicitness:** `external_api()` clearer than `environment='external'`
4. **Type safety:** Can't typo preset name

---

## Testing the Framework

### Unit Testing Core Components

**File:** `tests/core/api/test_retry_service.py`

```python
import pytest
from core.api.services.retry import RetryService, RetryConfig
from core.api.models import RetryExhaustedError

@pytest.mark.asyncio
async def test_retry_succeeds_on_second_attempt():
    """Test that retry works when request succeeds on retry."""
    config = RetryConfig(max_attempts=3, initial_delay=0.1)
    retry_service = RetryService(config)

    attempts = 0
    async def flaky_function():
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise Exception("Temporary failure")
        return "success"

    result = await retry_service.execute_with_retry(flaky_function)

    assert result == "success"
    assert attempts == 2  # Failed once, then succeeded

@pytest.mark.asyncio
async def test_retry_exhausted():
    """Test that RetryExhaustedError raised after max attempts."""
    config = RetryConfig(max_attempts=2, initial_delay=0.1)
    retry_service = RetryService(config)

    async def always_fails():
        raise Exception("Permanent failure")

    with pytest.raises(RetryExhaustedError):
        await retry_service.execute_with_retry(always_fails)
```

### Integration Testing with Real API

**File:** `tests/integration/test_api_framework.py`

```python
import pytest
from core.api import BaseAPIClient, HTTPConfig
from core.api.services.auth import BearerTokenAuth

@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_api_request(context):
    """Test framework against real API (httpbin.org)."""
    client = BaseAPIClient(
        context.request,
        base_url="https://httpbin.org",
        http_config=HTTPConfig.external_api()
    )

    # GET request
    response = await client.get('/get', params={'test': 'value'})
    assert response.status_code == 200
    assert 'test=value' in response.data['url']

    # POST request
    response = await client.post('/post', data={'key': 'value'})
    assert response.status_code == 200
    assert response.data['json']['key'] == 'value'
```

### Testing Service Clients

**File:** `services/user_service/tests/test_user_client.py`

```python
@pytest.mark.asyncio
async def test_create_user(user_client, mock_server):
    """Test user creation through service client."""
    # Mock server returns user JSON
    mock_server.expect_post('/users').respond_with({
        'id': 1,
        'name': 'Test User',
        'email': 'test@example.com'
    })

    user = await user_client.create_user('Test User', 'test@example.com')

    assert user.id == 1
    assert user.name == 'Test User'
    assert isinstance(user, User)  # Pydantic model
```

---

## Contributing Guidelines

### Code Style

**Follow existing patterns:**

- Async everywhere (no sync HTTP calls)
- Type hints on all public methods
- Docstrings in Google style
- Dataclasses for config objects

**Example:**

```python
async def validate_schema(
    self,
    data: Any,
    model: Type[BaseModel]
) -> BaseModel:
    """Validate data against Pydantic model.

    Args:
        data: Raw data (dict/list) from API response
        model: Pydantic model class to validate against

    Returns:
        Validated Pydantic model instance

    Raises:
        ValidationError: If data doesn't match schema

    Example:
        >>> user = validation.validate_schema(response.data, User)
        >>> print(user.name)  # Type-safe access
    """
    # Implementation...
```

### Adding New Features

**Checklist:**

- [ ] Does it solve a real test automation problem?
- [ ] Is it the simplest solution? (YAGNI check)
- [ ] Does it fit the 3-layer architecture?
- [ ] Are there unit tests?
- [ ] Is there documentation in README.md?
- [ ] Does it work with existing code?

### Deprecating Features

**Don't delete - deprecate first:**

```python
def old_method(self):
    """DEPRECATED: Use new_method() instead.

    This method will be removed in v2.0.0
    """
    import warnings
    warnings.warn(
        "old_method() is deprecated, use new_method()",
        DeprecationWarning,
        stacklevel=2
    )
    return self.new_method()
```

**Deprecation timeline:**

1. Release X.Y.0: Add deprecation warning
2. Release X.Y+1.0: Keep warning
3. Release X+1.0.0: Remove deprecated method

---

## Common Maintenance Tasks

### Updating Retry Logic

**File:** `core/api/services/retry.py`

**Common changes:**

- Add new status code to retry: Edit `retry_on_status_codes` in RetryConfig
- Change backoff algorithm: Edit `_calculate_delay()` method
- Add retry condition: Edit `_should_retry()` method

### Adding New Exception Type

**File:** `core/api/models.py`

```python
class NewError(APIError):
    """Description of when this error occurs."""
    pass
```

Then use in code:

```python
if response.status_code == 418:  # I'm a teapot
    raise NewError("Server is a teapot")
```

### Updating Configuration Defaults

**File:** `core/api/config.py`

**Example:** Increase default timeout

```python
@classmethod
def standard(cls) -> 'HTTPConfig':
    return cls(
        retry=RetryConfig(max_attempts=3, initial_delay=1.0),
        timeout=TimeoutConfig(request_timeout=45.0),  # Changed from 30s
    )
```

**Important:** Document in changelog - users may rely on old defaults!

### Debugging Framework Issues

**Enable debug logging:**

```python
import logging
logging.getLogger('core.api').setLevel(logging.DEBUG)
```

**Common issues:**

1. **"Retries not working"**
   - Check status code in `retry_on_status_codes`
   - Verify exception type is retryable

2. **"Auth headers not sent"**
   - Check `await client.auth.get_auth_headers()` returns correct dict
   - Verify headers are merged in `_get_headers()`

3. **"Validation fails unexpectedly"**
   - Print `response.data` before validation
   - Check Pydantic model matches actual response structure

---

## Architecture Evolution

### Version History

**v1.0.0 (Current):**

- Playwright-based HTTP client
- Auth facade + strategy pattern
- Retry with exponential backoff
- Interceptor for logging
- Circuit breaker **REMOVED** (YAGNI)

**v0.9.0 (Previous):**

- Circuit breaker included
- Factory pattern for auth (removed - overengineering)
- HTTPClient passed as parameter (changed - now created internally)

### Future Considerations

**Potential additions:**

- GraphQL support (if many services use GraphQL)
- Request caching (if tests make duplicate requests)
- Mock server integration (for offline testing)

**Non-goals:**

- Replace Playwright (locked in - that's okay)
- Support sync code (framework is async-first)
- Production usage (this is a test framework)

---

## References

**Design Patterns:**

- Strategy Pattern: Authentication strategies
- Composition: Services composed, not inherited
- Dependency Injection: Playwright context injected

**Similar Frameworks:**

- Playwright Python: API testing with APIRequestContext
- httpx: Async HTTP client (alternative to Playwright)
- requests-mock: Mocking HTTP requests (testing strategy)

**Test Automation Principles:**

- Test independence (no shared state)
- Fast feedback (retry + timeouts)
- Clear failures (logging + validation)

---

**Questions? Check existing code examples or ask the team!**
