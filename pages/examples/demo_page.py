"""
Demo Page - Page Object for UI Testing Examples

This Page Object demonstrates common BasePage methods following pure POM principles.
All selectors are encapsulated - tests should NEVER see selectors directly.

This module serves two purposes:
1. Data generation pattern for CRUD operations (generate_demo_data)
2. Examples of common BasePage methods (visibility, text, mouse actions, etc.)

Author: Erick Guadalupe Félix Flores
License: MIT
"""

from playwright.async_api import Page
from pages.standard_web_page import StandardWebPage
from utils.test_helpers import TestDataGenerator
from typing import Optional, Callable
import random


class DemoPage(StandardWebPage):
    """
    Demo page for UI testing examples and data generation pattern.
    
    Demonstrates:
    - Data generation pattern (generate_demo_data)
    - Common BasePage methods (visibility, text extraction, mouse actions, etc.)
    - Pure POM design (no selectors exposed to tests)
    """
    
    # ========== Form Input Selectors ==========
    first_name_input_selector = "input[name='firstName']"
    last_name_input_selector = "input[name='lastName']"
    email_input_selector = "input[name='email']"
    phone_input_selector = "input[name='phone']"
    role_select_selector = "select[name='role']"
    department_select_selector = "select[name='department']"
    status_checkbox_selector = "input[name='active']"
    notes_textarea_selector = "textarea[name='notes']"
    
    # ========== Search/Filter Selectors ==========
    filter_first_name_input_selector = "input[name='filterFirstName']"
    filter_last_name_input_selector = "input[name='filterLastName']"
    filter_email_input_selector = "input[name='filterEmail']"
    filter_role_select_selector = "select[name='filterRole']"
    search_button_selector = "button.search"
    
    # ========== Table & Validation Selectors ==========
    table_selector = "table.demo-table, table.users-table, table"
    no_data_message_selector = ".no-data-message, .empty-state, .no-results"
    confirm_delete_button_selector = "button.confirm-delete, button.confirm"
    
    # ========== Example/Demo UI Element Selectors ==========
    user_profile_selector = ".user-profile"
    username_display_selector = ".username"
    loading_spinner_selector = ".loading-spinner"
    dashboard_content_selector = ".dashboard-content"
    error_message_selector = ".error-message"
    menu_item_selector = ".menu-item"
    file_item_selector = ".file-item"
    context_menu_trigger_selector = ".context-menu-trigger"
    draggable_item_selector = ".draggable-item"
    drop_zone_selector = ".drop-zone"
    new_tab_link_selector = "a[target='_blank']"
    page_heading_selector = "h1"
    delete_button_selector = "button.delete"
    cancel_button_selector = "button.cancel"
    download_button_selector = "button.download-report"
    footer_content_selector = ".footer-content"
    footer_subscribe_button_selector = ".footer-subscribe-button"
    details_button_selector = "button.details, a.details, .action-details"
    
    def __init__(self, page: Page):
        """Initialize DemoPage."""
        super().__init__(page)
        self.page = page
        
        # Store generated data as class attributes
        self.data: Optional[dict] = None
        self.data_filters: Optional[dict] = None
        self.data_validate: Optional[dict] = None
    
    async def generate_demo_data(self, **kwargs) -> None:
        """
        Generates data dictionaries for demo/user tests.
        
        This method populates self.data, self.data_filters, and self.data_validate
        with random or specified data for creating, filtering, and validating records.
        
        Uses TestDataGenerator utility class for random data generation.
        
        Args:
            **kwargs: Allows overriding default values for any field, such as
                     'first_name', 'last_name', 'email', 'role', etc.
        
        Example:
            # Generate all dictionaries with random data
            >>> await demo_page.generate_demo_data()
            >>> await demo_page.fill_data(demo_page.data)
            >>> await demo_page.search_with_filters(demo_page.data_filters)
            >>> await demo_page.validate_record_information_in_details_view(demo_page.data_validate)
            
            # Override specific fields with random defaults for others
            >>> await demo_page.generate_demo_data(
            ...     first_name="John",
            ...     email="john@example.com",
            ...     role="Admin"
            ... )
        """
        # Generate or use provided values using TestDataGenerator
        first_name = kwargs.get('first_name', TestDataGenerator.random_string(8).title())
        last_name = kwargs.get('last_name', TestDataGenerator.random_string(10).title())
        email = kwargs.get('email', TestDataGenerator.random_email())
        phone = kwargs.get('phone', TestDataGenerator.random_phone())
        role = kwargs.get('role', random.choice(['User', 'Admin', 'Manager']))
        department = kwargs.get('department', random.choice(['Engineering', 'Sales', 'Marketing', 'HR']))
        active = kwargs.get('active', True)
        notes = kwargs.get('notes', f"Auto-generated demo user - {TestDataGenerator.random_string(15)}")
        
        # Create data dictionary (for fill_data)
        self.data = {
            self.first_name_input_selector: first_name,
            self.last_name_input_selector: last_name,
            self.email_input_selector: email,
            self.phone_input_selector: phone,
            self.role_select_selector: role,
            self.department_select_selector: department,
            self.status_checkbox_selector: active,
            self.notes_textarea_selector: notes,
        }
        
        # Create filter dictionary (for search_with_filters)
        self.data_filters = {
            self.filter_first_name_input_selector: first_name,
            self.filter_last_name_input_selector: last_name,
            self.filter_email_input_selector: email,
            self.filter_role_select_selector: role,
        }
        
        self.data_validate = self.data.copy()  # validate_record_information_in_details_view searches by text values
    
    # ========== High-Level Workflow Methods ==========
    
    async def create_demo_record(self, **kwargs) -> None:
        """
        Create a demo record with the standard workflow.
        
        Generates data, fills form, and submits.
        
        Args:
            **kwargs: Field overrides for demo data
        
        Example:
            ### Happy path - random data
            >>> await demo_page.create_demo_record()
            
            ### Custom record with specific values
            >>> await demo_page.create_demo_record(
            ...     first_name="Admin",
            ...     email="admin@example.com",
            ...     role="Administrator"
            ... )
        """
        await self.generate_demo_data(**kwargs)
        await self.create_item_workflow(self.data)
    
    async def search_demo_record(self, **kwargs) -> None:
        """
        Search for demo records with specified criteria.
        
        If no kwargs provided, uses self.data_filters from last generate_demo_data() call.
        
        Args:
            **kwargs: Search criteria (generates new filters if provided)
        
        Example:
            # Search with last generated data
            >>> await demo_page.generate_demo_data()
            >>> await demo_page.create_demo_record()
            >>> await demo_page.search_demo_record()  # Uses self.data_filters
            
            # Search with custom criteria
            >>> await demo_page.search_demo_record(first_name="John", role="Admin")
        """
        if kwargs:
            await self.generate_demo_data(**kwargs)
        
        await self.search_with_filters(self.data_filters)
    
    async def edit_demo_record(self, **kwargs) -> None:
        """
        Edit existing demo record with new data.
        
        This method:
        1. Generates new data with kwargs
        2. Searches for the record using data_filters
        3. Edits the record with the new data
        
        Args:
            **kwargs: Fields to update
        
        Example:
            >>> await demo_page.edit_demo_record(
            ...     first_name="Updated Name",
            ...     role="Manager"
            ... )
        """
        await self.generate_demo_data(**kwargs)
        await self.search_with_filters(self.data_filters)
        await self.edit_item_workflow(self.data)
    
    async def validate_demo_details(self) -> None:
        """
        Validate demo record details in details view.
        
        This method:
        1. Clicks the details button to open details view
        2. Validates the record using self.data_validate
        
        Uses self.data_validate from the last generate_demo_data() call.
        The record must exist (created previously) to be validated.
        
        Example:
            >>> await demo_page.generate_demo_data()
            >>> await demo_page.create_demo_record()
            >>> await demo_page.search_demo_record()
            >>> await demo_page.validate_demo_details()  # Clicks details and validates
        """
        await self.page.click(self.details_button_selector)
        await self.validate_record_information_in_details_view(self.data_validate)
    
    async def validate_demo_table_data(self) -> None:
        """
        Validate that demo data appears in table after search.
        
        Uses self.data_filters from the last generate_demo_data() call to verify
        that the record appears in the search results table.
        
        Example:
            >>> await demo_page.generate_demo_data()
            >>> await demo_page.create_demo_record()
            >>> await demo_page.search_demo_record()
            >>> await demo_page.validate_demo_table_data()  # Verify in table
        """
        await self.validate_table_data(
            data_filters=self.data_filters,
            filter_button_selector=self.search_button_selector,
            table_selector=self.table_selector
        )
    
    async def validate_demo_not_in_table(self) -> None:
        """
        Validate that demo data does NOT appear in table (e.g., after deletion).
        
        Uses self.data_filters to search and verifies no results found.
        Useful for validating delete operations.
        
        Example:
            >>> await demo_page.delete_demo_record()
            >>> await demo_page.validate_demo_not_in_table()  # Verify deleted
        """
        await self.validate_no_data_in_table(
            data_filters=self.data_filters,
            filter_button_selector=self.search_button_selector,
            no_data_selector=self.no_data_message_selector
        )
    
    async def delete_demo_record(self) -> None:
        """
        Delete demo record with confirmation.
        
        Clicks delete button and confirms the deletion dialog.
        
        Example:
            >>> await demo_page.generate_demo_data()
            >>> await demo_page.create_demo_record()
            >>> await demo_page.search_demo_record()
            >>> await demo_page.delete_demo_record()
            >>> await demo_page.validate_demo_not_in_table()
        """
        await self.delete_item(
            delete_button_selector=self.delete_button_selector,
            confirm_delete_button_selector=self.confirm_delete_button_selector
        )
    
    # ========================================================================
    # EXAMPLE METHODS - Common BasePage Operations
    # ========================================================================
    # These methods demonstrate common BasePage functionality while following
    # pure POM principles. Tests call these methods - never touch selectors directly.
    # ========================================================================
    
    async def is_user_profile_visible(self) -> bool:
        """Check if user profile section is visible."""
        return await self.is_visible(self.user_profile_selector)
    
    async def is_loading_complete(self) -> bool:
        """Check if page loading is complete (spinner hidden)."""
        return await self.is_hidden(self.loading_spinner_selector)
    
    async def is_active_status_checked(self) -> bool:
        """Check if active status checkbox is checked."""
        return await self.is_checked(self.status_checkbox_selector)
    
    async def wait_for_dashboard_content(self, timeout: int = 30000) -> None:
        """Wait for dashboard content to load."""
        await self.wait_for_selector(self.dashboard_content_selector, timeout=timeout)
    
    async def get_username_text(self) -> str:
        """Get username display text."""
        return await self.get_text(self.username_display_selector)
    
    async def get_error_message(self) -> str:
        """Get error message text."""
        return await self.get_text(self.error_message_selector)
    
    async def hover_over_menu(self) -> None:
        """Hover over menu item to reveal dropdown."""
        await self.hover(self.menu_item_selector)
    
    async def double_click_file(self) -> None:
        """Double-click file item to open."""
        await self.double_click(self.file_item_selector)
    
    async def right_click_for_context_menu(self) -> None:
        """Right-click to open context menu."""
        await self.right_click(self.context_menu_trigger_selector)
    
    async def drag_item_to_zone(self) -> None:
        """Drag item to drop zone."""
        await self.drag_and_drop(
            source_selector=self.draggable_item_selector,
            target_selector=self.drop_zone_selector
        )
    
    async def click_new_tab_link(self) -> None:
        """Click link that opens in new tab."""
        await self.page.click(self.new_tab_link_selector)
    
    async def wait_for_page_heading(self) -> None:
        """Wait for page heading to appear."""
        await self.wait_for_selector(self.page_heading_selector)
    
    async def confirm_deletion(self, accept: bool = True) -> str:
        """
        Handle delete confirmation dialog.
        
        Args:
            accept: True to confirm, False to cancel
            
        Returns:
            Dialog message text
        """
        return await self.handle_confirmation_dialog(
            trigger_action=lambda: self.page.click(self.delete_button_selector),
            accept=accept
        )
    
    async def handle_cancel_dialog(self, expected_text: str = "Are you sure?") -> str:
        """
        Handle cancel confirmation dialog.
        
        Args:
            expected_text: Expected dialog text
            
        Returns:
            Dialog message text
        """
        return await self.handle_confirmation_dialog(
            trigger_action=lambda: self.page.click(self.cancel_button_selector),
            accept=False,
            dialog_text=expected_text
        )
    
    async def download_report_file(self, filename: str = "report.pdf") -> str:
        """
        Download report file.
        
        Args:
            filename: Expected filename
            
        Returns:
            Path to downloaded file
        """
        return await self.download_file(
            download_trigger_selector=self.download_button_selector,
            expected_filename=filename
        )
    
    async def set_session_cookie(self, token: str, domain: str = "example.com") -> None:
        """
        Set session token cookie.
        
        Args:
            token: Session token value
            domain: Cookie domain
        """
        await self.set_cookie(
            name="session_token",
            value=token,
            domain=domain,
            path="/",
            expires=1735689600
        )
    
    async def get_session_cookie(self) -> Optional[dict]:
        """Get session token cookie value."""
        return await self.get_cookie("session_token")
    
    async def save_user_preferences(self, preferences_json: str) -> None:
        """
        Save user preferences to local storage.
        
        Args:
            preferences_json: JSON string of preferences
        """
        await self.set_local_storage("user_preferences", preferences_json)
    
    async def load_user_preferences(self) -> Optional[str]:
        """Load user preferences from local storage."""
        return await self.get_local_storage("user_preferences")
    
    async def scroll_to_footer_and_subscribe(self) -> None:
        """Scroll to footer and click subscribe button."""
        await self.scroll_into_view(self.footer_content_selector)
        await self.page.click(self.footer_subscribe_button_selector)
