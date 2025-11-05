"""
Example test demonstrating basic login functionality.

This test shows how to use the LoginPage class to test login
functionality for any web application.

To run this test:
    pytest tests/examples/test_login_example.py --headed
"""

import pytest
from pages.login_page import LoginPage
from utils.config import Config


@pytest.mark.asyncio
class TestLoginExamples:
    """Example test class demonstrating login functionality."""
    
    async def test_successful_login(self, page):
        """
        Test successful login with valid credentials.
        
        This is a basic example showing how to use the LoginPage class.
        Adapt the selectors in LoginPage to match your application.
        """
        login_page = LoginPage(page)
        
        # Navigate to your application's login page
        base_url = Config.get_base_url()
        await page.goto(f"{base_url}/login")
        
        # Perform login
        username = Config.get_test_username()
        password = Config.get_test_password()
        
        await login_page.login(username, password)
        
        # Verify login was successful
        # Note: Customize this check based on your application
        # Examples:
        # - Check for user menu: await login_page.is_logged_in('[data-testid="user-menu"]')
        # - Check URL changed: assert '/dashboard' in page.url
        # - Check welcome message: await page.locator('text=Welcome').is_visible()
        
        # For this example, we just check we're not on the login page anymore
        is_logged_in = await login_page.is_logged_in()
        assert is_logged_in, "User should be logged in"
    
    async def test_login_with_invalid_credentials(self, page):
        """
        Test login with invalid credentials shows error message.
        
        This example demonstrates how to test negative scenarios.
        """
        login_page = LoginPage(page)
        
        base_url = Config.get_base_url()
        await page.goto(f"{base_url}/login")
        
        # Try to login with invalid credentials
        await login_page.login("invalid_user", "wrong_password")
        
        # Verify error message is shown
        # Note: Customize the error selector in LoginPage to match your application
        has_error = await login_page.verify_login_error()
        assert has_error, "Error message should be displayed for invalid credentials"
    
    async def test_change_user_session(self, page):
        """
        Test switching between different user sessions.
        
        This example shows how to test user switching functionality.
        """
        login_page = LoginPage(page)
        base_url = Config.get_base_url()
        
        # Login as first user
        await login_page.change_user(
            "user1@example.com",
            "password1",
            f"{base_url}/login"
        )
        
        # Verify first user is logged in
        # Add your verification logic here
        
        # Logout (if your app supports it)
        # await login_page.logout('[data-testid="logout-button"]')
        
        # Login as second user
        await login_page.change_user(
            "user2@example.com", 
            "password2",
            f"{base_url}/login"
        )
        
        # Verify second user is logged in
        # Add your verification logic here


@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.asyncio
class TestLoginWithCustomSelectors:
    """
    Example showing how to customize login selectors for your specific application.
    """
    
    async def test_login_with_custom_selectors(self, page):
        """
        Demonstrate how to use custom selectors for your application.
        """
        login_page = LoginPage(page)
        
        # Customize selectors for your application
        login_page.username_selector = '#email'  # Your app uses email field
        login_page.password_selector = '#password'
        login_page.submit_button_selector = 'button.login-btn'
        login_page.error_message_selector = '.error-text'
        
        base_url = Config.get_base_url()
        await page.goto(f"{base_url}/login")
        
        # Now use the login page with your custom selectors
        await login_page.login("user@example.com", "password123")
        
        # Verify login based on your application's behavior
        assert await login_page.is_logged_in('[data-testid="dashboard"]')
