"""
Example test demonstrating basic login functionality using proper POM pattern.

This test shows how to use Page Object classes to test login functionality.
The test file only calls methods from the page object, without direct page interaction.

To run this test:
    pytest tests/examples/test_login_example.py --headed
"""

import pytest
from pages.examples.authentication_page import AuthenticationPage
from utils.config import Config


@pytest.mark.asyncio
class TestLoginExamples:
    """
    Example test class demonstrating login functionality with POM pattern.
    
    Tests only call methods from AuthenticationPage, no direct page interaction.
    """
    
    async def test_successful_login(self, page):
        """
        Test successful login with valid credentials.
        
        This demonstrates proper POM: the test calls page object methods only.
        """
        # Initialize page object
        auth_page = AuthenticationPage(page)
        
        # Get credentials from configuration
        base_url = Config.get_base_url()
        username = Config.get_test_username()
        password = Config.get_test_password()
        
        # Perform login using page object method
        await auth_page.perform_login(username, password, base_url)
        
        # Verify login success using page object method
        is_logged_in = await auth_page.verify_login_success()
        assert is_logged_in, "User should be logged in"
    
    async def test_login_with_invalid_credentials(self, page):
        """
        Test login with invalid credentials shows error message.
        
        Demonstrates testing negative scenarios with POM pattern.
        """
        # Initialize page object
        auth_page = AuthenticationPage(page)
        
        base_url = Config.get_base_url()
        
        # Navigate to login page
        await auth_page.navigate_to_login(base_url)
        
        # Try to login with invalid credentials
        await auth_page.perform_login("invalid_user", "wrong_password")
        
        # Verify error is displayed using page object method
        has_error = await auth_page.verify_login_failure()
        assert has_error, "Error message should be displayed for invalid credentials"
    
    async def test_logout_functionality(self, page):
        """
        Test logout functionality.
        
        Shows complete login and logout flow using page object methods.
        """
        # Initialize page object
        auth_page = AuthenticationPage(page)
        
        base_url = Config.get_base_url()
        username = Config.get_test_username()
        password = Config.get_test_password()
        
        # Login using page object method
        await auth_page.perform_login(username, password, base_url)
        
        # Verify logged in
        assert await auth_page.verify_login_success()
        
        # Logout using page object method
        await auth_page.perform_logout()
        
        # Verify redirected to login page
        is_on_login_page = await auth_page.verify_user_is_on_login_page()
        assert is_on_login_page, "Should be redirected to login page after logout"
    
    async def test_password_reset_flow(self, page):
        """
        Test password reset functionality.
        
        Demonstrates testing password reset using page object pattern.
        """
        # Initialize page object
        auth_page = AuthenticationPage(page)
        
        base_url = Config.get_base_url()
        
        # Navigate to login page
        await auth_page.navigate_to_login(base_url)
        
        # Initiate password reset
        await auth_page.initiate_password_reset("user@example.com")
        
        # Verify success message (customize based on your app)
        # This would use a page object method in real implementation


@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.asyncio
class TestLoginWithCustomConfiguration:
    """
    Example showing how to customize page object selectors for your application.
    """
    
    async def test_login_with_custom_selectors(self, page):
        """
        Demonstrate customizing page object selectors.
        
        Shows how to adapt the page object to your specific application.
        """
        # Initialize page object
        auth_page = AuthenticationPage(page)
        
        # Customize selectors for your application
        auth_page.username_selector = '#email'  # Your app uses email field
        auth_page.password_selector = '#password'
        auth_page.submit_button_selector = 'button.login-btn'
        auth_page.profile_menu = '[data-testid="user-menu"]'
        
        base_url = Config.get_base_url()
        
        # Now use the page object with your custom selectors
        await auth_page.perform_login("user@example.com", "password123", base_url)
        
        # Verify login using page object method
        assert await auth_page.verify_login_success('[data-testid="dashboard"]')

