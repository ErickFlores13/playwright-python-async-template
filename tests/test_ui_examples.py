"""
UI Testing Examples - Playwright Python Async Template

This module demonstrates common BasePage methods using pure Page Object Model (POM) design.
All examples use DemoPage - NO hardcoded selectors in tests.

Each test showcases a specific BasePage capability while maintaining clean, readable code.

Author: Erick Guadalupe Félix Flores
License: MIT
"""

import pytest
from playwright.async_api import Page
from pages.login_page import LoginPage
from pages.examples.demo_page import DemoPage


# ============================================================================
# EXAMPLE 1: Data Generation Pattern (RECOMMENDED APPROACH)
# ============================================================================

@pytest.mark.asyncio
async def test_data_generation_pattern(page: Page):
    """
    Demonstrates: generate_demo_data() pattern - THE PROFESSIONAL WAY.
    
    This is the recommended approach for handling form data:
    - Centralizes data in Page Object
    - Uses TestDataGenerator for random data
    - Supports kwargs for overrides
    - Reusable across create/search/validate
    """
    demo_page = DemoPage(page)
    await page.goto("https://example.com/users")
    
    # Generate random data
    await demo_page.generate_demo_data()
    
    # Use in form
    await demo_page.fill_data(demo_page.data)
    
    # Override specific fields
    await demo_page.generate_demo_data(
        first_name="John",
        email="john@example.com"
    )


# ============================================================================
# EXAMPLE 2: Login with Page Object
# ============================================================================

@pytest.mark.asyncio
async def test_login_workflow(page: Page):
    """
    Demonstrates: Using LoginPage for authentication.
    
    Shows proper POM - no selectors exposed in test.
    """
    login_page = LoginPage(page)
    
    # Login
    await login_page.login(
        username="admin@example.com",
        password="password123",
        base_url="https://example.com/login"
    )
    
    # Verify login success
    is_logged_in = await login_page.is_user_logged_in()
    assert is_logged_in, "Login failed"


# ============================================================================
# EXAMPLE 3: Element Visibility Checks
# ============================================================================

@pytest.mark.asyncio
async def test_element_visibility(page: Page):
    """
    Demonstrates: is_visible(), is_hidden(), wait_for_selector()
    """
    demo_page = DemoPage(page)
    await page.goto("https://example.com/dashboard")
    
    # Check visibility
    is_visible = await demo_page.is_user_profile_visible()
    assert is_visible, "User profile should be visible"
    
    # Check loading complete
    is_loaded = await demo_page.is_loading_complete()
    assert is_loaded, "Page should be fully loaded"
    
    # Wait for specific content
    await demo_page.wait_for_dashboard_content()


# ============================================================================
# EXAMPLE 4: Checkbox State Verification
# ============================================================================

@pytest.mark.asyncio
async def test_checkbox_state(page: Page):
    """
    Demonstrates: is_checked() method.
    """
    demo_page = DemoPage(page)
    await page.goto("https://example.com/settings")
    
    # Check if checkbox is checked
    is_active = await demo_page.is_active_status_checked()
    print(f"Active status: {is_active}")


# ============================================================================
# EXAMPLE 5: Text Extraction
# ============================================================================

@pytest.mark.asyncio
async def test_get_text(page: Page):
    """
    Demonstrates: get_text() method for extracting element text.
    """
    demo_page = DemoPage(page)
    await page.goto("https://example.com/profile")
    
    # Get username
    username = await demo_page.get_username_text()
    assert username == "testuser", f"Expected 'testuser', got '{username}'"
    
    # Get error message (if present)
    await page.goto("https://example.com/error-page")
    error = await demo_page.get_error_message()
    print(f"Error: {error}")


# ============================================================================
# EXAMPLE 6: Screenshots
# ============================================================================

@pytest.mark.asyncio
async def test_screenshots(page: Page):
    """
    Demonstrates: take_screenshot() method.
    """
    demo_page = DemoPage(page)
    await page.goto("https://example.com/dashboard")
    
    # Capture screenshot
    screenshot_path = await demo_page.take_screenshot("dashboard_view")
    print(f"Screenshot saved: {screenshot_path}")
    
    # Capture error state
    await page.goto("https://example.com/error")
    await demo_page.take_screenshot("error_state")


# ============================================================================
# EXAMPLE 7: Mouse Actions
# ============================================================================

@pytest.mark.asyncio
async def test_mouse_interactions(page: Page):
    """
    Demonstrates: hover(), double_click(), right_click(), drag_and_drop()
    """
    demo_page = DemoPage(page)
    await page.goto("https://example.com/interactive")
    
    # Hover to reveal menu
    await demo_page.hover_over_menu()
    
    # Double-click file
    await demo_page.double_click_file()
    
    # Right-click for context menu
    await demo_page.right_click_for_context_menu()
    
    # Drag and drop
    await demo_page.drag_item_to_zone()


# ============================================================================
# EXAMPLE 8: Tab Management
# ============================================================================

@pytest.mark.asyncio
async def test_new_tab_handling(page: Page):
    """
    Demonstrates: switch_to_new_tab(), close_current_tab()
    """
    demo_page = DemoPage(page)
    await page.goto("https://example.com")
    
    # Open new tab
    async with page.context.expect_page() as new_page_info:
        await demo_page.click_new_tab_link()
    
    # Switch to new tab
    await demo_page.switch_to_new_tab()
    await demo_page.wait_for_page_heading()
    
    # Close tab
    await demo_page.close_current_tab()


# ============================================================================
# EXAMPLE 9: Page Navigation
# ============================================================================

@pytest.mark.asyncio
async def test_navigation(page: Page):
    """
    Demonstrates: go_back(), refresh_page()
    """
    demo_page = DemoPage(page)
    
    # Navigate through pages
    await page.goto("https://example.com/page1")
    await page.goto("https://example.com/page2")
    
    # Go back
    await demo_page.go_back()
    
    # Refresh
    await demo_page.refresh_page()


# ============================================================================
# EXAMPLE 10: Dialog Handling
# ============================================================================

@pytest.mark.asyncio
async def test_confirmation_dialogs(page: Page):
    """
    Demonstrates: handle_confirmation_dialog() for alerts/confirms
    """
    demo_page = DemoPage(page)
    await page.goto("https://example.com/actions")
    
    # Accept deletion
    dialog_text = await demo_page.confirm_deletion(accept=True)
    print(f"Dialog: {dialog_text}")
    
    # Dismiss cancel action
    await demo_page.handle_cancel_dialog(expected_text="Are you sure?")


# ============================================================================
# EXAMPLE 11: File Downloads
# ============================================================================

@pytest.mark.asyncio
async def test_file_download(page: Page):
    """
    Demonstrates: download_file() method
    """
    demo_page = DemoPage(page)
    await page.goto("https://example.com/reports")
    
    # Download file
    file_path = await demo_page.download_report_file(filename="report.pdf")
    assert "report.pdf" in file_path
    print(f"Downloaded to: {file_path}")


# ============================================================================
# EXAMPLE 12: Cookie Management
# ============================================================================

@pytest.mark.asyncio
async def test_cookies(page: Page):
    """
    Demonstrates: set_cookie(), get_cookie()
    """
    demo_page = DemoPage(page)
    await page.goto("https://example.com")
    
    # Set cookie
    await demo_page.set_session_cookie(token="abc123xyz", domain="example.com")
    
    # Get cookie
    cookie = await demo_page.get_session_cookie()
    assert cookie["value"] == "abc123xyz"


# ============================================================================
# EXAMPLE 13: Local Storage
# ============================================================================

@pytest.mark.asyncio
async def test_local_storage(page: Page):
    """
    Demonstrates: set_local_storage(), get_local_storage(), clear_local_storage()
    """
    demo_page = DemoPage(page)
    await page.goto("https://example.com")
    
    # Save preferences
    await demo_page.save_user_preferences('{"theme": "dark", "lang": "en"}')
    
    # Load preferences
    prefs = await demo_page.load_user_preferences()
    print(f"Preferences: {prefs}")
    
    # Clear all storage
    await demo_page.clear_all_storage()


# ============================================================================
# EXAMPLE 14: Scroll Actions
# ============================================================================

@pytest.mark.asyncio
async def test_scrolling(page: Page):
    """
    Demonstrates: scroll_into_view() with element interaction
    """
    demo_page = DemoPage(page)
    await page.goto("https://example.com/long-page")
    
    # Scroll and interact
    await demo_page.scroll_to_footer_and_subscribe()


# ============================================================================
# EXAMPLE 15: Complete CRUD Workflow
# ============================================================================

@pytest.mark.asyncio
async def test_complete_crud_workflow(page: Page):
    """
    Demonstrates: Full CRUD workflow with data generation pattern.
    
    This is the GOLD STANDARD for production tests:
    - Clean, readable business logic
    - Zero selector exposure
    - Reusable data generation
    - High-level workflow methods
    """
    demo_page = DemoPage(page)
    await page.goto("https://example.com/users")
    
    # CREATE
    await demo_page.create_demo_record(
        first_name="Jane",
        last_name="Doe",
        role="Manager"
    )
    
    # READ/SEARCH
    await demo_page.search_demo_record()
    await demo_page.validate_demo_table_data()
    
    # VALIDATE DETAILS
    await demo_page.validate_demo_details()
    
    # UPDATE (preserves existing fields, updates only specified)
    await demo_page.edit_demo_record(
        role="Senior Manager",
        department="Operations"
    )
    
    # DELETE
    await demo_page.delete_demo_record()
    await demo_page.validate_demo_not_in_table()


# ============================================================================
# NOTE: For complete BasePage method documentation, see pages/base_page.py
# ============================================================================
# 
# This file demonstrates the most commonly used methods. BasePage includes 70+ methods:
# - Attribute manipulation (remove_required_attribute, etc.)
# - Advanced Select2 handling
# - Modal operations
# - Complex table operations
# - File upload validation
# - Session storage methods
# - And much more...
# 
# ============================================================================
# RECOMMENDED PATTERNS
# ============================================================================
# 
# 1. Data Generation (Examples 1, 15):
#    - Use generate_*_data() for all form operations
#    - Centralize test data in Page Objects
#    - Leverage TestDataGenerator for randomization
# 
# 2. Pure POM (All examples):
#    - NEVER hardcode selectors in tests
#    - ALL interactions through Page Object methods
#    - Tests read like business requirements
# 
# 3. High-Level Methods (Example 15):
#    - Combine operations into workflow methods
#    - Keep tests focused on "what" not "how"
#    - Maximize reusability
# 
# See: pages/examples/demo_page.py for complete implementation
# ============================================================================
