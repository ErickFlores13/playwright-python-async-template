"""
Example Page Object for Authentication module.

Extends the base LoginPage with additional authentication-related methods.
"""

from pages.login_page import LoginPage
from playwright.async_api import Page


class AuthenticationPage(LoginPage):
    """
    Page Object for Authentication module.
    
    Includes login, logout, password reset, and user profile operations.
    """
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # Override selectors for your specific application
        self.username_selector = 'input[name="username"]'
        self.password_selector = 'input[name="password"]'
        self.submit_button_selector = 'button[type="submit"]'
        self.error_message_selector = '.error-message'
        
        # Additional authentication selectors
        self.logout_button = 'a:has-text("Logout")'
        self.forgot_password_link = 'a:has-text("Forgot Password")'
        self.reset_email_input = 'input[name="email"]'
        self.reset_submit_button = 'button:has-text("Send Reset Link")'
        self.profile_menu = '[data-testid="user-menu"]'
        self.profile_link = 'a:has-text("Profile")'
        
    async def navigate_to_login(self, base_url: str) -> None:
        """Navigate to the login page."""
        await self.page.goto(f"{base_url}/login")
        await self.page.wait_for_load_state("domcontentloaded")
    
    async def perform_login(self, username: str, password: str, base_url: str = None) -> None:
        """
        Perform complete login flow.
        
        Args:
            username: User's username or email
            password: User's password
            base_url: Optional base URL to navigate to first
        """
        if base_url:
            await self.navigate_to_login(base_url)
        
        await self.login(username, password)
    
    async def perform_logout(self) -> None:
        """Perform logout operation."""
        await self.logout(self.logout_button)
    
    async def verify_login_success(self, success_indicator: str = None) -> bool:
        """
        Verify that login was successful.
        
        Args:
            success_indicator: Optional selector for element that appears after login
            
        Returns:
            True if logged in successfully
        """
        return await self.is_logged_in(success_indicator or self.profile_menu)
    
    async def verify_login_failure(self, expected_error: str = None) -> bool:
        """
        Verify that login failed with an error message.
        
        Args:
            expected_error: Optional specific error message to check
            
        Returns:
            True if error is displayed
        """
        return await self.verify_login_error(expected_error)
    
    async def initiate_password_reset(self, email: str) -> None:
        """
        Initiate password reset process.
        
        Args:
            email: Email address for password reset
        """
        await self.page.click(self.forgot_password_link)
        await self.page.fill(self.reset_email_input, email)
        await self.page.click(self.reset_submit_button)
        await self.page.wait_for_load_state("domcontentloaded")
    
    async def navigate_to_profile(self) -> None:
        """Navigate to user profile page."""
        await self.page.click(self.profile_menu)
        await self.page.click(self.profile_link)
        await self.page.wait_for_load_state("domcontentloaded")
    
    async def verify_user_is_on_login_page(self) -> bool:
        """
        Check if currently on the login page.
        
        Returns:
            True if on login page
        """
        return 'login' in self.page.url.lower()
