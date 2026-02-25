"""
UI Testing Examples
===================

Demonstrates how to use the framework for browser-based UI automation.

All examples target https://the-internet.herokuapp.com (a free test site)
so they can be run without a private application.

Run::

    pytest tests/test_ui_examples.py -v

Run with visible browser::

    pytest tests/test_ui_examples.py --headed -v
"""

import pytest
from playwright.async_api import Page

from core.ui.base_page import BasePage
from utils.config import Config
from utils.test_helpers import TestDataGenerator

# ---------------------------------------------------------------------------
# Page Objects
# ---------------------------------------------------------------------------


class HerokuLoginPage(BasePage):
    """Login page for https://the-internet.herokuapp.com/login."""

    username_input = "#username"
    password_input = "#password"
    login_button = '[type="submit"]'
    flash_message = "#flash"

    async def login(self, username: str, password: str) -> None:
        """Fill and submit the login form."""
        await self.fill_data(
            {
                self.username_input: username,
                self.password_input: password,
            }
        )
        await self.page.click(self.login_button)
        await self.wait.wait_for_page_load()

    async def get_flash_message(self) -> str:
        """Return the text of the flash notification."""
        return (await self.page.locator(self.flash_message).inner_text()).strip()


class HerokuCheckboxPage(BasePage):
    """Checkboxes demo page."""

    checkbox1 = "input[type='checkbox']:nth-of-type(1)"
    checkbox2 = "input[type='checkbox']:nth-of-type(2)"


class HerokuDropdownPage(BasePage):
    """Dropdown demo page."""

    dropdown = "#dropdown"


class HerokuDynamicContentPage(BasePage):
    """Dynamic content page (demonstrates waiting strategies)."""

    content_rows = ".large-10"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.smoke_test
async def test_successful_login(page: Page) -> None:
    """
    Smoke test: successful login with valid credentials.

    Demonstrates:
    - Page Object Model with BasePage
    - fill_data() for form filling
    - validation service for assertions
    """
    login_page = HerokuLoginPage(page)
    await page.goto("https://the-internet.herokuapp.com/login")
    await login_page.wait.wait_for_page_load()

    await login_page.login("tomsmith", "SuperSecretPassword!")

    # Verify redirect to secure area
    assert "/secure" in page.url
    await login_page.validation.assert_visible(".flash.success")


@pytest.mark.smoke_test
async def test_failed_login(page: Page) -> None:
    """
    Smoke test: failed login with invalid credentials.

    Demonstrates:
    - Negative testing with the framework
    - Flash message validation
    """
    login_page = HerokuLoginPage(page)
    await page.goto("https://the-internet.herokuapp.com/login")

    await login_page.login("wronguser", "wrongpassword")

    flash = await login_page.get_flash_message()
    assert "Your username is invalid" in flash


@pytest.mark.regression
async def test_checkbox_interactions(page: Page) -> None:
    """
    Regression test: checkbox checking and unchecking.

    Demonstrates:
    - Boolean values in fill_data() for checkboxes
    - Validation service assert_checked / assert_not_checked
    """
    await page.goto("https://the-internet.herokuapp.com/checkboxes")
    checkbox_page = HerokuCheckboxPage(page)

    # Check checkbox 1 (initially unchecked)
    await checkbox_page.fill_data({checkbox_page.checkbox1: True})
    await checkbox_page.validation.assert_checked(checkbox_page.checkbox1)

    # Uncheck checkbox 2 (initially checked)
    await checkbox_page.fill_data({checkbox_page.checkbox2: False})
    await checkbox_page.validation.assert_not_checked(checkbox_page.checkbox2)


@pytest.mark.regression
async def test_dropdown_selection(page: Page) -> None:
    """
    Regression test: native <select> dropdown interaction.

    Demonstrates:
    - Auto-detected select strategy via fill_data()
    - Validating the selected value
    """
    await page.goto("https://the-internet.herokuapp.com/dropdown")
    dropdown_page = HerokuDropdownPage(page)

    await dropdown_page.fill_data({dropdown_page.dropdown: "Option 1"})

    selected = await page.locator(f"{dropdown_page.dropdown} option:checked").inner_text()
    assert selected == "Option 1"


@pytest.mark.regression
async def test_page_screenshot_on_demand(page: Page) -> None:
    """
    Regression test: manual screenshot capture.

    Demonstrates:
    - screenshot service usage
    - Evidence capture for reporting
    """
    await page.goto("https://the-internet.herokuapp.com/")
    base = BasePage(page)

    # Take a named screenshot (saved to screenshots/ directory)
    await base.screenshot.take_screenshot("homepage_evidence")


@pytest.mark.regression
async def test_storage_manipulation(page: Page) -> None:
    """
    Regression test: localStorage read/write via Storage service.

    Demonstrates:
    - Storage service for setting and reading localStorage
    """
    await page.goto("https://the-internet.herokuapp.com/")
    base = BasePage(page)

    await base.storage.set_local_storage("test_key", "hello_framework")
    value = await base.storage.get_local_storage("test_key")
    assert value == "hello_framework"


@pytest.mark.regression
async def test_dynamic_content_wait(page: Page) -> None:
    """
    Regression test: waiting for dynamic page content.

    Demonstrates:
    - wait service for page-load events
    - locator count verification
    """
    await page.goto("https://the-internet.herokuapp.com/dynamic_content")
    content_page = HerokuDynamicContentPage(page)

    await content_page.wait.wait_for_page_load()
    rows = page.locator(content_page.content_rows)
    count = await rows.count()
    assert count > 0, "Expected at least one dynamic content row"


@pytest.mark.regression
async def test_tab_window_management(page: Page) -> None:
    """
    Regression test: multi-tab management using TabWindow service.

    Demonstrates:
    - Opening a link that triggers a new tab
    - Closing tabs
    """
    await page.goto("https://the-internet.herokuapp.com/windows")
    base = BasePage(page)

    # Click the link that opens a new window/tab
    new_page = await base.tab_window.wait_for_new_tab_and_switch(
        lambda: page.click("a[href='/windows/new']")
    )

    assert new_page is not None
    await new_page.wait_for_load_state()
    assert "New Window" in await new_page.title()
    await new_page.close()


@pytest.mark.integration
async def test_full_crud_workflow_example(page: Page) -> None:
    """
    Integration test: login → interact → logout workflow.

    Demonstrates a complete end-to-end flow using multiple services.
    """
    login_page = HerokuLoginPage(page)
    await page.goto("https://the-internet.herokuapp.com/login")
    await login_page.login("tomsmith", "SuperSecretPassword!")
    await login_page.validation.assert_visible(".flash.success")

    # Interact with the secure page
    await login_page.validation.assert_visible("h2")
    heading = await page.locator("h2").inner_text()
    assert "Secure Area" in heading

    # Logout
    await page.click("a[href='/logout']")
    await login_page.wait.wait_for_page_load()
    assert "/login" in page.url


@pytest.mark.unit
def test_data_generator_produces_valid_data() -> None:
    """
    Unit test: TestDataGenerator generates correctly-typed values.

    Demonstrates the test data utilities available in utils/test_helpers.py.
    These run without a browser.
    """
    name = TestDataGenerator.random_name()
    assert isinstance(name, str)
    assert len(name) > 0

    email = TestDataGenerator.random_email()
    assert "@" in email

    phone = TestDataGenerator.random_phone("us")
    assert "(" in phone and ")" in phone

    future_date = TestDataGenerator.random_future_date()
    assert len(future_date) == 10  # YYYY-MM-DD

    price = TestDataGenerator.random_price()
    assert float(price) > 0
