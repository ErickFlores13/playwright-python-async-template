"""
API Testing Examples
====================

Demonstrates how to use the framework's API client for REST API testing.

All examples target https://jsonplaceholder.typicode.com (a free fake REST API)
so they can be run without a private backend.

Run::

    pytest tests/test_api_examples.py -v
"""

import pytest
import pytest_asyncio
from playwright.async_api import BrowserContext
from pydantic import BaseModel

from core.api.base_client import BaseAPIClient
from core.api.config import HTTPConfig
from core.api.services.auth import APIKeyAuth, BasicAuth, BearerTokenAuth, CompositeAuth, CustomHeaderAuth
from utils.config import Config

# ---------------------------------------------------------------------------
# Pydantic models for response validation
# ---------------------------------------------------------------------------

BASE_URL = "https://jsonplaceholder.typicode.com"


class Post(BaseModel):
    """JSONPlaceholder post schema."""

    userId: int
    id: int
    title: str
    body: str


class Comment(BaseModel):
    """JSONPlaceholder comment schema."""

    postId: int
    id: int
    name: str
    email: str
    body: str


class CreatePostResponse(BaseModel):
    """Response schema for post creation (JSONPlaceholder fakes 201)."""

    id: int
    title: str
    body: str
    userId: int


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def posts_client(context: BrowserContext) -> BaseAPIClient:
    """API client pre-configured for JSONPlaceholder."""
    return BaseAPIClient(
        context.request,
        base_url=BASE_URL,
        http_config=HTTPConfig.standard(),
    )


# ---------------------------------------------------------------------------
# Tests — GET requests
# ---------------------------------------------------------------------------


@pytest.mark.smoke_test
async def test_get_all_posts(posts_client: BaseAPIClient) -> None:
    """
    Smoke test: GET /posts returns a non-empty list of posts.

    Demonstrates:
    - BaseAPIClient.get() with no authentication
    - response.is_success check
    - validate_response_type for list responses
    """
    response = await posts_client.get("/posts")

    assert response.is_success
    posts_client.validation.validate_response_type(response.data, list)
    posts_client.validation.validate_list_length(response.data, min_length=1)


@pytest.mark.smoke_test
async def test_get_single_post(posts_client: BaseAPIClient) -> None:
    """
    Smoke test: GET /posts/1 returns a correctly-shaped post.

    Demonstrates:
    - validate_schema() with a Pydantic model for type-safe access
    - JSON path validation
    """
    response = await posts_client.get("/posts/1")

    assert response.is_success
    post = posts_client.validation.validate_schema(response.data, Post)
    assert post.id == 1
    assert post.userId > 0
    assert post.title


@pytest.mark.regression
async def test_get_posts_with_query_params(posts_client: BaseAPIClient) -> None:
    """
    Regression test: filter posts by userId query parameter.

    Demonstrates:
    - Query parameters via the params argument
    - Filtering and counting results
    """
    response = await posts_client.get("/posts", params={"userId": 1})

    assert response.is_success
    posts_client.validation.validate_response_type(response.data, list)
    for post_data in response.data:
        assert post_data["userId"] == 1


@pytest.mark.regression
async def test_get_post_comments(posts_client: BaseAPIClient) -> None:
    """
    Regression test: retrieve comments for a specific post.

    Demonstrates:
    - Nested resource endpoints
    - Schema validation on a list of items
    """
    response = await posts_client.get("/posts/1/comments")

    assert response.is_success
    assert len(response.data) > 0
    comment = posts_client.validation.validate_schema(response.data[0], Comment)
    assert comment.postId == 1


# ---------------------------------------------------------------------------
# Tests — POST / PUT / PATCH / DELETE
# ---------------------------------------------------------------------------


@pytest.mark.regression
async def test_create_post(posts_client: BaseAPIClient) -> None:
    """
    Regression test: POST /posts creates a new resource.

    Demonstrates:
    - post() with a JSON body
    - 201 status code assertion
    - Schema validation of the created resource
    """
    response = await posts_client.post(
        "/posts",
        data={"title": "Test Post", "body": "Framework example", "userId": 1},
        expected_status=201,
    )

    assert response.status_code == 201
    created = posts_client.validation.validate_schema(response.data, CreatePostResponse)
    assert created.title == "Test Post"
    assert created.id > 0


@pytest.mark.regression
async def test_update_post_put(posts_client: BaseAPIClient) -> None:
    """
    Regression test: PUT /posts/1 performs a full update.

    Demonstrates:
    - put() for full resource replacement
    - 200 status on update
    """
    response = await posts_client.put(
        "/posts/1",
        data={"id": 1, "title": "Updated Title", "body": "Updated body", "userId": 1},
    )

    assert response.is_success
    assert response.data["title"] == "Updated Title"


@pytest.mark.regression
async def test_patch_post(posts_client: BaseAPIClient) -> None:
    """
    Regression test: PATCH /posts/1 performs a partial update.

    Demonstrates:
    - patch() for partial resource updates
    - Only the changed field is sent in the request body
    """
    response = await posts_client.patch("/posts/1", data={"title": "Patched Title"})

    assert response.is_success
    assert response.data["title"] == "Patched Title"


@pytest.mark.regression
async def test_delete_post(posts_client: BaseAPIClient) -> None:
    """
    Regression test: DELETE /posts/1 removes the resource.

    Demonstrates:
    - delete() with 200 status (JSONPlaceholder returns 200 not 204)
    """
    response = await posts_client.delete("/posts/1", expected_status=200)

    assert response.is_success


# ---------------------------------------------------------------------------
# Tests — Response validation helpers
# ---------------------------------------------------------------------------


@pytest.mark.regression
async def test_validate_required_fields(posts_client: BaseAPIClient) -> None:
    """
    Regression test: validate required fields are present in the response.

    Demonstrates:
    - validate_required_fields() for presence checks
    """
    response = await posts_client.get("/posts/1")

    posts_client.validation.validate_required_fields(
        response.data, ["id", "userId", "title", "body"]
    )


@pytest.mark.regression
async def test_validate_json_path(posts_client: BaseAPIClient) -> None:
    """
    Regression test: JSON path assertion on nested response data.

    Demonstrates:
    - validate_json_path() for deep value checks
    """
    response = await posts_client.get("/posts/1")

    posts_client.validation.validate_json_path(response.data, "id", expected_value=1)
    posts_client.validation.validate_json_path(response.data, "userId", expected_value=1)


@pytest.mark.regression
async def test_response_elapsed_time(posts_client: BaseAPIClient) -> None:
    """
    Regression test: verify response time is within acceptable bounds.

    Demonstrates:
    - response.elapsed_ms for performance assertions
    """
    response = await posts_client.get("/posts/1")

    assert response.elapsed_ms > 0
    # Performance gate: should respond within 10 seconds
    assert response.elapsed_ms < 10_000


# ---------------------------------------------------------------------------
# Tests — Authentication strategies
# ---------------------------------------------------------------------------


@pytest.mark.unit
async def test_bearer_token_auth_headers() -> None:
    """
    Unit test: BearerTokenAuth adds the correct Authorization header.

    Demonstrates:
    - BearerTokenAuth strategy
    - Direct header inspection
    """
    auth = BearerTokenAuth(token="test-jwt-token-abc123")
    headers = await auth.get_auth_headers()

    assert headers["Authorization"] == "Bearer test-jwt-token-abc123"


@pytest.mark.unit
async def test_api_key_auth_headers() -> None:
    """
    Unit test: APIKeyAuth adds the API key in the specified header.

    Demonstrates:
    - APIKeyAuth with a custom header name
    """
    auth = APIKeyAuth(api_key="sk_test_123456", header_name="X-API-Key")
    headers = await auth.get_auth_headers()

    assert headers["X-API-Key"] == "sk_test_123456"


@pytest.mark.unit
async def test_basic_auth_headers() -> None:
    """
    Unit test: BasicAuth encodes credentials as Base64.

    Demonstrates:
    - BasicAuth strategy
    - Presence of Authorization header
    """
    auth = BasicAuth(username="admin", password="secret")
    headers = await auth.get_auth_headers()

    assert "Authorization" in headers
    assert headers["Authorization"].startswith("Basic ")


@pytest.mark.unit
async def test_custom_header_auth() -> None:
    """
    Unit test: CustomHeaderAuth injects arbitrary headers.

    Demonstrates:
    - CustomHeaderAuth for non-standard auth schemes
    """
    auth = CustomHeaderAuth(headers={"X-Tenant-ID": "tenant-42", "X-API-Version": "v2"})
    headers = await auth.get_auth_headers()

    assert headers["X-Tenant-ID"] == "tenant-42"
    assert headers["X-API-Version"] == "v2"


@pytest.mark.unit
async def test_composite_auth_merges_headers() -> None:
    """
    Unit test: CompositeAuth merges headers from multiple strategies.

    Demonstrates:
    - CompositeAuth for combining authentication strategies
    """
    auth = CompositeAuth(
        [
            BearerTokenAuth(token="jwt-abc"),
            CustomHeaderAuth(headers={"X-Tenant-ID": "tenant-1"}),
        ]
    )
    headers = await auth.get_auth_headers()

    assert headers["Authorization"] == "Bearer jwt-abc"
    assert headers["X-Tenant-ID"] == "tenant-1"


# ---------------------------------------------------------------------------
# Tests — set_* convenience methods on BaseAPIClient
# ---------------------------------------------------------------------------


@pytest.mark.unit
async def test_set_bearer_token_on_client(context: BrowserContext) -> None:
    """
    Unit test: set_bearer_token() configures the client's auth strategy.

    Demonstrates:
    - Programmatic auth configuration after client creation
    - This test does need a context to create a BaseAPIClient
    """
    client = BaseAPIClient(context.request, BASE_URL)
    client.set_bearer_token("runtime-token-xyz")

    headers = await client._auth_strategy.get_auth_headers()
    assert headers["Authorization"] == "Bearer runtime-token-xyz"


@pytest.mark.unit
async def test_set_api_key_on_client(context: BrowserContext) -> None:
    """
    Unit test: set_api_key() configures the client's auth strategy.
    """
    client = BaseAPIClient(context.request, BASE_URL)
    client.set_api_key("api-key-value", header_name="X-API-Key")

    headers = await client._auth_strategy.get_auth_headers()
    assert headers["X-API-Key"] == "api-key-value"
