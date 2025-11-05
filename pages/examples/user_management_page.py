"""
Example Page Object for a User Management module.

This demonstrates proper POM pattern where all selectors and methods
for the user module are contained in this page class.
"""

from pages.standard_web_page import StandardWebPage
from playwright.async_api import Page


class UserManagementPage(StandardWebPage):
    """
    Page Object for User Management module.
    
    Contains all selectors and methods specific to user CRUD operations.
    Tests should only call these methods, not interact with page directly.
    """
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # Module-specific selectors
        self.create_user_button = 'a:has-text("Create User")'
        self.edit_button = 'a[title="Edit"]'
        self.view_button = 'a[title="View"]'
        
        # Form field selectors
        self.username_input = 'input[name="username"]'
        self.email_input = 'input[name="email"]'
        self.first_name_input = 'input[name="first_name"]'
        self.last_name_input = 'input[name="last_name"]'
        self.role_select = 'select[name="role"]'
        self.is_active_checkbox = 'input[name="is_active"]'
        
        # Override base selectors for this module
        self.submit_button_selector = 'button[type="submit"]'
        self.delete_button_selector = 'a[title="Delete"]'
        self.confirm_delete_button_selector = 'button:has-text("Confirm")'
        self.filter_button_selector = 'button:has-text("Filter")'
        self.clear_filters_selector = 'button:has-text("Clear Filters")'
        self.table_selector = '#users-table'
        self.title_selector = 'h1:has-text("User Management")'
        
    async def navigate_to_module(self, base_url: str) -> None:
        """Navigate to the user management module."""
        await self.page.goto(f"{base_url}/users")
        await self.is_visible(self.title_selector)
    
    async def navigate_to_create_form(self) -> None:
        """Navigate to the create user form."""
        await self.page.click(self.create_user_button)
        await self.page.wait_for_load_state("domcontentloaded")
    
    async def create_user(self, user_data: dict) -> None:
        """
        Create a new user with the provided data.
        
        Args:
            user_data: Dictionary with user information
                Expected keys: username, email, first_name, last_name, role, is_active
        
        Example:
            user_data = {
                'username': 'john_doe',
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'role': 'Admin',
                'is_active': True
            }
        """
        await self.navigate_to_create_form()
        
        # Build form data with module-specific selectors
        form_data = {
            self.username_input: user_data.get('username', ''),
            self.email_input: user_data.get('email', ''),
            self.first_name_input: user_data.get('first_name', ''),
            self.last_name_input: user_data.get('last_name', ''),
            self.role_select: user_data.get('role', ''),
            self.is_active_checkbox: user_data.get('is_active', True),
        }
        
        await self.fill_data(form_data)
        await self.page.click(self.submit_button_selector)
        await self.page.wait_for_load_state("domcontentloaded")
    
    async def search_user(self, search_filters: dict) -> None:
        """
        Search for users using filters.
        
        Args:
            search_filters: Dictionary with filter criteria
                Example: {'username': 'john', 'role': 'Admin'}
        """
        filter_data = {}
        
        if 'username' in search_filters:
            filter_data[self.username_input] = search_filters['username']
        if 'email' in search_filters:
            filter_data[self.email_input] = search_filters['email']
        if 'role' in search_filters:
            filter_data[self.role_select] = search_filters['role']
        
        await self.search_with_filters(filter_data)
    
    async def edit_user(self, new_data: dict) -> None:
        """
        Edit an existing user.
        
        Assumes you're on a page where the edit button is visible.
        
        Args:
            new_data: Dictionary with updated user information
        """
        await self.page.click(self.edit_button)
        await self.page.wait_for_load_state("domcontentloaded")
        
        # Build form data for editing
        form_data = {}
        if 'username' in new_data:
            form_data[self.username_input] = new_data['username']
        if 'email' in new_data:
            form_data[self.email_input] = new_data['email']
        if 'first_name' in new_data:
            form_data[self.first_name_input] = new_data['first_name']
        if 'last_name' in new_data:
            form_data[self.last_name_input] = new_data['last_name']
        if 'role' in new_data:
            form_data[self.role_select] = new_data['role']
        if 'is_active' in new_data:
            form_data[self.is_active_checkbox] = new_data['is_active']
        
        await self.edit_item(form_data)
    
    async def view_user_details(self) -> None:
        """Navigate to user detail view."""
        await self.page.click(self.view_button)
        await self.page.wait_for_load_state("domcontentloaded")
    
    async def delete_user(self) -> None:
        """Delete a user."""
        await self.delete_item()
    
    async def validate_user_in_table(self, user_data: dict) -> None:
        """
        Validate that a user appears in the table with correct data.
        
        Args:
            user_data: Dictionary with expected user data to validate
        """
        await self.validate_table_data(user_data)
    
    async def validate_user_details(self, expected_data: dict) -> None:
        """
        Validate user details in the detail view.
        
        Args:
            expected_data: Dictionary with expected user information
        """
        validation_data = {}
        
        if 'username' in expected_data:
            validation_data['label[name="username"]'] = expected_data['username']
        if 'email' in expected_data:
            validation_data['label[name="email"]'] = expected_data['email']
        if 'full_name' in expected_data:
            validation_data['label[name="full_name"]'] = expected_data['full_name']
        if 'role' in expected_data:
            validation_data['label[name="role"]'] = expected_data['role']
        
        await self.validate_record_information_in_details_view(validation_data)
    
    async def verify_success_message(self, message: str) -> None:
        """
        Verify that a success message is displayed.
        
        Args:
            message: Expected success message text
        """
        await self.check_message(message)
    
    async def apply_filters_and_validate(self, filters: dict) -> None:
        """
        Apply filters and validate results in table.
        
        Args:
            filters: Dictionary with filter criteria
        """
        await self.search_user(filters)
        await self.validate_user_in_table(filters)
    
    async def clear_all_filters(self, filter_fields: dict) -> None:
        """
        Clear all applied filters and validate they're cleared.
        
        Args:
            filter_fields: Dictionary with filter field selectors
        """
        await self.clean_filters(filter_fields)
