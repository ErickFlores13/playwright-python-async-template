"""
Generic login page object.

Provides a reusable login page that navigates to a URL and fills
standard username/password credentials. Override selectors in your
own subclass to match the specific application under test.
"""

import logging

from playwright.async_api import Page

from core.ui.base_page import BasePage

logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    """
    Generic login page for common username/password flows.

    Override the selector class attributes in a subclass when your
    application uses different element identifiers.

    Example — default selectors::

        login_page = LoginPage(page)
        await login_page.login("user", "pass", "https://app.example.com/login")

    Example — custom selectors::

        class MyAppLoginPage(LoginPage):
            username_input = '[data-testid="username"]'
            password_input = '[data-testid="password"]'
            login_button   = '[data-testid="submit"]'
    """

    # Override these in a subclass to match your application's selectors.
    username_input: str = "#username"
    password_input: str = "#password"
    login_button: str = '[type="submit"]'

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    async def login(self, username: str, password: str, url: str) -> None:
        """
        Navigate to *url* and perform a username/password login.

        Args:
            username: The username (or email) to log in with.
            password: The corresponding password.
            url: Full URL of the login page (e.g. ``https://app.com/login``).

        Example::

            await login_page.login(
                Config.get_test_username(),
                Config.get_test_password(),
                f"{Config.get_base_url()}/login",
            )
        """
        logger.info(f"Navigating to login page: {url}")
        await self.page.goto(url)
        await self.wait.wait_for_page_load()

        logger.debug(f"Filling credentials for user: {username}")
        await self.fill_data(
            {
                self.username_input: username,
                self.password_input: password,
            }
        )

        await self.page.click(self.login_button)
        await self.wait.wait_for_page_load()
        logger.info("Login submitted successfully")
