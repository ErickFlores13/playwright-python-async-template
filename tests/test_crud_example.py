"""
Complete CRUD Example
=====================

Demonstrates a full end-to-end CRUD workflow combining UI and API testing.

UI target: https://the-internet.herokuapp.com (free public test site)
API target: https://jsonplaceholder.typicode.com (free fake REST API)

This example shows the recommended patterns for:
- Page Object Model with BasePage
- TestDataGenerator for consistent, random test data
- API client + service client pattern
- Hybrid tests that mix UI navigation with API verification

Run::

    pytest tests/test_crud_example.py -v
"""

import pytest
import pytest_asyncio
from playwright.async_api import BrowserContext, Page
from pydantic import BaseModel

from core.api.base_client import BaseAPIClient
from core.ui.base_page import BasePage
from utils.test_helpers import TestDataGenerator

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class Post(BaseModel):
    """JSONPlaceholder post."""

    userId: int
    id: int
    title: str
    body: str


# ---------------------------------------------------------------------------
# Page Objects
# ---------------------------------------------------------------------------


class LoginPage(BasePage):
    """Heroku test app login page."""

    username_input = "#username"
    password_input = "#password"
    submit_button = '[type="submit"]'

    async def login(self, username: str, password: str) -> None:
        """Fill and submit login form."""
        await self.fill_data(
            {
                self.username_input: username,
                self.password_input: password,
            }
        )
        await self.page.click(self.submit_button)
        await self.wait.wait_for_page_load()


class SecurePage(BasePage):
    """Heroku secure area page."""

    heading = "h2"
    logout_link = "a[href='/logout']"

    async def get_heading(self) -> str:
        """Return the page heading text."""
        return await self.page.locator(self.heading).inner_text()

    async def logout(self) -> None:
        """Click the logout link."""
        await self.page.click(self.logout_link)
        await self.wait.wait_for_page_load()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def api_client(context: BrowserContext) -> BaseAPIClient:
    """API client for JSONPlaceholder."""
    return BaseAPIClient(context.request, base_url="https://jsonplaceholder.typicode.com")


# ---------------------------------------------------------------------------
# CRUD Tests — API layer
# ---------------------------------------------------------------------------


@pytest.mark.regression
async def test_api_create_read_update_delete(api_client: BaseAPIClient) -> None:
    """
    Regression test: full CRUD lifecycle via REST API.

    Demonstrates:
    - POST → validate created resource
    - GET → validate retrieved resource
    - PUT → validate full update
    - PATCH → validate partial update
    - DELETE → validate removal
    """
    # --- CREATE ---
    title = TestDataGenerator.random_string(12)
    body = TestDataGenerator.random_string(50)

    create_resp = await api_client.post(
        "/posts",
        data={"title": title, "body": body, "userId": 1},
        expected_status=201,
    )
    assert create_resp.status_code == 201
    created_id = create_resp.data["id"]

    # --- READ (list) ---
    list_resp = await api_client.get("/posts", params={"userId": 1})
    assert list_resp.is_success
    api_client.validation.validate_list_length(list_resp.data, min_length=1)

    # --- READ (single) ---
    read_resp = await api_client.get("/posts/1")
    post = api_client.validation.validate_schema(read_resp.data, Post)
    assert post.id == 1

    # --- UPDATE (full) ---
    updated_title = TestDataGenerator.random_string(12)
    put_resp = await api_client.put(
        "/posts/1",
        data={"id": 1, "title": updated_title, "body": body, "userId": 1},
    )
    assert put_resp.is_success
    assert put_resp.data["title"] == updated_title

    # --- UPDATE (partial) ---
    patch_title = TestDataGenerator.random_string(12)
    patch_resp = await api_client.patch("/posts/1", data={"title": patch_title})
    assert patch_resp.is_success
    assert patch_resp.data["title"] == patch_title

    # --- DELETE ---
    del_resp = await api_client.delete(f"/posts/{created_id}", expected_status=200)
    assert del_resp.is_success


# ---------------------------------------------------------------------------
# CRUD Tests — UI layer
# ---------------------------------------------------------------------------


@pytest.mark.regression
async def test_ui_login_and_secure_area(page: Page) -> None:
    """
    Regression test: full UI login → secure area → logout flow.

    Demonstrates:
    - Page Object Model with BasePage
    - fill_data() for forms
    - validation service
    - TestDataGenerator (credentials shown statically for a known app)
    """
    login_page = LoginPage(page)
    await page.goto("https://the-internet.herokuapp.com/login")
    await login_page.wait.wait_for_page_load()

    # Login with known test credentials
    await login_page.login("tomsmith", "SuperSecretPassword!")

    # Assert successful login
    secure = SecurePage(page)
    heading = await secure.get_heading()
    assert "Secure Area" in heading

    # Logout
    await secure.logout()
    assert "/login" in page.url


# ---------------------------------------------------------------------------
# Hybrid Test — UI + API
# ---------------------------------------------------------------------------


@pytest.mark.integration
async def test_hybrid_ui_and_api(page: Page, api_client: BaseAPIClient) -> None:
    """
    Integration test: use UI and API in the same test.

    Demonstrates:
    - UI login to obtain a session
    - Parallel API validation to cross-check backend state
    - Hybrid testing pattern

    The UI part uses the Heroku test site; the API part uses JSONPlaceholder.
    In a real test, both would target the same application.
    """
    # --- Step 1: Log in via UI ---
    login_page = LoginPage(page)
    await page.goto("https://the-internet.herokuapp.com/login")
    await login_page.login("tomsmith", "SuperSecretPassword!")
    assert "/secure" in page.url

    # --- Step 2: Validate backend data via API (simulated cross-check) ---
    response = await api_client.get("/users/1")
    assert response.is_success
    # Simulate: assert that the logged-in user's backend record exists
    api_client.validation.validate_required_fields(
        response.data, ["id", "name", "email"]
    )
    assert response.data["id"] == 1

    # --- Step 3: Create data via API and verify ---
    post_response = await api_client.post(
        "/posts",
        data={
            "title": TestDataGenerator.random_string(10),
            "body": "Hybrid test post",
            "userId": 1,
        },
        expected_status=201,
    )
    assert post_response.status_code == 201

    # --- Step 4: Take screenshot as evidence ---
    base = BasePage(page)
    await base.screenshot.take_screenshot("hybrid_test_evidence")


# ---------------------------------------------------------------------------
# Data Generation Examples (no browser required)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_data_generator_full_suite() -> None:
    """
    Unit test: verify all TestDataGenerator methods return valid data.

    Runs without a browser — demonstrates available generators.
    """
    gen = TestDataGenerator

    # Identity
    assert gen.random_name("first")
    assert gen.random_name("last")
    assert " " in gen.random_name("full")

    # Contact
    assert "@" in gen.random_email()
    assert "@" in gen.random_email("company.com")
    assert "(" in gen.random_phone("us")
    assert gen.random_phone("international").startswith("+1")

    # Credentials
    password = gen.random_password(length=16, include_special=True)
    assert len(password) == 16

    # Dates
    future = gen.random_future_date(max_days=30)
    assert len(future) == 10
    past = gen.random_past_date(max_days=30)
    assert len(past) == 10

    # Numeric
    assert 1 <= gen.random_number(1, 10) <= 10
    price = float(gen.random_price(5.0, 10.0))
    assert 5.0 <= price <= 10.0

    # Misc
    assert gen.random_company_name()
    assert gen.random_url().startswith("https://")
    assert len(gen.random_uuid()) == 36
    assert gen.random_color_hex().startswith("#")

    address = gen.random_address()
    assert "street" in address and "city" in address and "zip_code" in address
