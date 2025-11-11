"""
LoginPage - Generic login page implementation for web applications.

This module provides a flexible login page class that can be customized
for different web applications by overriding selectors and methods.

Author: Erick Guadalupe Félix Flores
License: MIT
"""

from playwright.async_api import Page
from pages.base_page import BasePage


class LoginPage(BasePage):
    """
    Generic login page implementation that can be adapted to different web applications.
    
    Override the selectors in your test setup or create a subclass to match
    your application's specific login form structure.
    """
    
    def __init__(self, page: Page):
        """
        Initialize the LoginPage with a Playwright page instance.
        
        Args:
            page: Playwright Page object
        """
        super().__init__(page)
        self.page = page
        
        # Default selectors - override these in subclasses or via configuration
        self.username_selector = 'input[name="username"]'
        self.password_selector = 'input[name="password"]'
        self.submit_button_selector = 'button[type="submit"]'
        self.error_message_selector = '.error-message, .alert-danger, [role="alert"]'
        self.user_menu_selector = '[data-testid="user-menu"]'  # Common success indicator
        
    async def login(self, username: str, password: str, base_url: str = None) -> Page:
        """
        Perform login operation with provided credentials.
        
        Args:
            username: Username or email for login
            password: Password for login
            base_url: Optional base URL to navigate to before login
            
        Returns:
            Page: The Playwright page object after successful login
            
        Example:
            >>> login_page = LoginPage(page)
            >>> await login_page.login("user@example.com", "password123", "https://example.com/login")
        """
        if base_url:
            await self.page.goto(base_url)
            
        await self.page.fill(self.username_selector, username)
        await self.page.fill(self.password_selector, password)
        await self.page.click(self.submit_button_selector)
        
        # Wait for navigation after login
        await self.page.wait_for_load_state("networkidle")
        
        return self.page
    
    async def change_user(self, username: str, password: str, url: str) -> None:
        """
        Navigate to a specific URL and perform login.
        
        This method is useful when you need to switch users or login to a different
        environment within the same test session.
        
        Args:
            username: Username or email for login
            password: Password for login
            url: The login page URL to navigate to
            
        Example:
            >>> await login_page.change_user("admin@example.com", "admin123", "https://example.com/admin")
        """
        await self.page.goto(url)
        await self.login(username, password)
    
    async def verify_login_error(self, expected_error: str = None) -> bool:
        """
        Verify that a login error message is displayed.
        
        Args:
            expected_error: Optional specific error message to check for
            
        Returns:
            bool: True if error message is visible, False otherwise
            
        Example:
            >>> is_error = await login_page.verify_login_error("Invalid credentials")
        """
        error_element = self.page.locator(self.error_message_selector)
        is_visible = await error_element.is_visible()
        
        if is_visible and expected_error:
            error_text = await error_element.inner_text()
            return expected_error in error_text
            
        return is_visible
    
    async def is_logged_in(self, success_indicator: str = None) -> bool:
        """
        Check if the user is successfully logged in.
        
        Args:
            success_indicator: Optional selector for an element that appears after successful login
                             (e.g., user menu, dashboard element)
            
        Returns:
            bool: True if logged in, False otherwise
            
        Example:
            >>> logged_in = await login_page.is_logged_in('[data-testid="user-menu"]')
        """
        if success_indicator:
            try:
                await self.page.wait_for_selector(success_indicator, timeout=5000)
                return True
            except TimeoutError:
                return False
            except Exception:
                return False
        
        # Default: check if we're not on the login page anymore
        current_url = self.page.url
        return 'login' not in current_url.lower()
    
    async def logout(self, logout_selector: str) -> None:
        """
        Perform logout operation.
        
        Args:
            logout_selector: Selector for the logout button/link
            
        Example:
            >>> await login_page.logout('button[data-testid="logout"]')
        """
        await self.page.click(logout_selector)
        await self.page.wait_for_load_state("networkidle")
    
    async def is_user_logged_in(self) -> bool:
        """
        Check if user is logged in by verifying user menu visibility.
        
        This is a convenience method that checks for the common user menu indicator.
        Override user_menu_selector in __init__ to match your application.
        
        Returns:
            bool: True if user menu is visible (logged in), False otherwise
            
        Example:
            >>> login_page = LoginPage(page)
            >>> await login_page.login("user@example.com", "password123")
            >>> is_logged = await login_page.is_user_logged_in()
            >>> assert is_logged, "Login failed"
        """
        return await self.is_logged_in(self.user_menu_selector)