"""
Example tests demonstrating CRUD operations using the framework.

This module shows how to use BasePage and StandardWebPage classes
to test Create, Read, Update, Delete operations in web applications.

To run these tests:
    pytest tests/examples/test_crud_example.py --headed
"""

import pytest
from pages.base_page import BasePage
from pages.standard_web_page import StandardWebPage
from utils.config import Config
from utils.consts import FilterType, ValidationType, ButtonOperations


@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.asyncio
class TestCRUDExamples:
    """
    Example test class demonstrating CRUD operations.
    
    Note: These tests are examples and need to be customized
    with your application's actual selectors and data.
    """
    
    async def test_create_record(self, page):
        """
        Example: Create a new record in your application.
        
        This demonstrates how to:
        1. Navigate to create form
        2. Fill form fields using fill_data
        3. Submit and verify creation
        """
        web_page = StandardWebPage(page)
        base_url = Config.get_base_url()
        
        # Navigate to your application
        await page.goto(f"{base_url}/items")
        
        # Click "Create New" button (customize selector)
        await page.click('a:has-text("Create New")')
        
        # Define form data to fill
        form_data = {
            'input[name="title"]': 'Test Item',
            'input[name="description"]': 'This is a test item',
            'select[name="category"]': 'Category 1',
            'input[name="price"]': '99.99',
            'input[name="is_active"]': True,  # Checkbox
        }
        
        # Fill the form
        await web_page.fill_data(form_data)
        
        # Update submit button selector for your app
        web_page.submit_button_selector = 'button[type="submit"]'
        await page.click(web_page.submit_button_selector)
        
        # Verify success message (customize selector)
        await web_page.check_message("Item created successfully")
    
    async def test_read_and_filter_records(self, page):
        """
        Example: Read and filter records in a table.
        
        This demonstrates how to:
        1. Apply filters to search for records
        2. Validate table data matches filters
        """
        web_page = StandardWebPage(page)
        base_url = Config.get_base_url()
        
        # Navigate to list page
        await page.goto(f"{base_url}/items")
        
        # Update filter button selector for your app
        web_page.filter_button_selector = 'button:has-text("Filter")'
        
        # Define filters
        filters = {
            'input[name="search"]': 'Test Item',
            'select[name="category"]': 'Category 1',
        }
        
        # Apply filters and validate results
        await web_page.validate_table_data(filters)
    
    async def test_update_record(self, page):
        """
        Example: Update an existing record.
        
        This demonstrates how to:
        1. Navigate to edit form
        2. Update specific fields
        3. Submit and verify changes
        """
        web_page = StandardWebPage(page)
        base_url = Config.get_base_url()
        
        # Navigate to list and click edit on first item
        await page.goto(f"{base_url}/items")
        await page.click('a[title="Edit"]')  # Customize selector
        
        # Define new data for update
        update_data = {
            'input[name="title"]': 'Updated Test Item',
            'input[name="price"]': '149.99',
        }
        
        # Update submit button selector
        web_page.submit_button_selector = 'button:has-text("Save")'
        
        # Perform the edit
        await web_page.edit_item(update_data)
        
        # Verify success message
        await web_page.check_message("Item updated successfully")
    
    async def test_delete_record(self, page):
        """
        Example: Delete a record.
        
        This demonstrates how to:
        1. Navigate to record
        2. Click delete and confirm
        3. Verify deletion
        """
        web_page = StandardWebPage(page)
        base_url = Config.get_base_url()
        
        # Navigate to list
        await page.goto(f"{base_url}/items")
        
        # Update delete button selectors for your app
        web_page.delete_button_selector = 'a[title="Delete"]'
        web_page.confirm_delete_button_selector = 'button:has-text("Confirm")'
        
        # Click delete button on first item
        await web_page.delete_item()
        
        # Verify deletion message
        await web_page.check_message("Item deleted successfully")
    
    async def test_validate_record_details(self, page):
        """
        Example: Validate record details in view mode.
        
        This demonstrates how to verify displayed data.
        """
        web_page = StandardWebPage(page)
        base_url = Config.get_base_url()
        
        # Navigate to detail view
        await page.goto(f"{base_url}/items/1")  # Assuming item with ID 1 exists
        
        # Define expected data
        expected_data = {
            'label[name="title"]': 'Test Item',
            'label[name="price"]': '99.99',
            'label[name="category"]': 'Category 1',
        }
        
        # Validate the displayed data
        await web_page.validate_record_information_in_details_view(expected_data)


@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.asyncio
class TestFormValidationExamples:
    """
    Examples demonstrating form validation testing.
    """
    
    async def test_required_field_validation(self, page):
        """
        Example: Test that required fields are enforced.
        """
        web_page = StandardWebPage(page)
        base_url = Config.get_base_url()
        
        await page.goto(f"{base_url}/items/create")
        
        # Update submit button selector
        web_page.submit_button_selector = 'button[type="submit"]'
        
        # Try to submit with empty required field
        form_data = {
            'input[name="title"]': '',  # Required field left empty
            'input[name="price"]': '99.99',
        }
        
        # Test required field validation
        await web_page.fields_validations(
            data=form_data,
            field_selector='input[name="title"]',
            validation_type=ValidationType.REQUIRED
        )
        
        # Verify validation error appears (customize selector)
        error = page.locator('.error:has-text("This field is required")')
        assert await error.is_visible()
    
    async def test_max_length_validation(self, page):
        """
        Example: Test field max length validation.
        """
        web_page = StandardWebPage(page)
        base_url = Config.get_base_url()
        
        await page.goto(f"{base_url}/items/create")
        
        # Update submit button selector
        web_page.submit_button_selector = 'button[type="submit"]'
        
        # Try to submit with too long text
        form_data = {
            'input[name="title"]': 'A' * 500,  # Exceeds max length
        }
        
        # Test max length validation
        await web_page.fields_validations(
            data=form_data,
            field_selector='input[name="title"]',
            validation_type=ValidationType.MAX_LENGTH
        )
        
        # Verify validation error
        error = page.locator('.error:has-text("maximum length")')
        assert await error.is_visible()


@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.asyncio
class TestFilterExamples:
    """
    Examples demonstrating filter testing.
    """
    
    async def test_empty_filters(self, page):
        """
        Example: Test filtering with no criteria.
        """
        web_page = StandardWebPage(page)
        base_url = Config.get_base_url()
        
        async def goto_index():
            await page.goto(f"{base_url}/items")
        
        # Update filter button selector
        web_page.filter_button_selector = 'button:has-text("Filter")'
        
        # Test empty filter behavior
        await web_page.validate_filter(
            filter_type=FilterType.EMPTY,
            view_to_validate=goto_index
        )
    
    async def test_clear_filters(self, page):
        """
        Example: Test clear filters functionality.
        """
        web_page = StandardWebPage(page)
        base_url = Config.get_base_url()
        
        async def goto_index():
            await page.goto(f"{base_url}/items")
        
        # Update selectors
        web_page.filter_button_selector = 'button:has-text("Filter")'
        web_page.clear_filters_selector = 'button:has-text("Clear")'
        
        # Define filters to apply and then clear
        filters = {
            'input[name="search"]': 'Test',
            'select[name="category"]': 'Category 1',
        }
        
        # Test clear filters functionality
        await web_page.validate_filter(
            filter_type=FilterType.CLEAR,
            view_to_validate=goto_index,
            data_filters=filters
        )


@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.asyncio
class TestButtonOperationsExamples:
    """
    Examples demonstrating cancel and back button operations.
    """
    
    async def test_cancel_create_operation(self, page):
        """
        Example: Test cancel button on create form.
        """
        web_page = StandardWebPage(page)
        base_url = Config.get_base_url()
        
        async def goto_create():
            await page.goto(f"{base_url}/items/create")
        
        # Update cancel button selector
        web_page.cancel_form_selector = 'a:has-text("Cancel")'
        web_page.title_selector = 'h1:has-text("Items List")'
        
        # Test cancel operation
        await web_page.validate_button_operations(
            operation_type=ButtonOperations.CANCEL_CREATE,
            form_method=goto_create
        )
    
    async def test_back_button_from_detail(self, page):
        """
        Example: Test back button from detail view.
        """
        web_page = StandardWebPage(page)
        base_url = Config.get_base_url()
        
        async def goto_detail():
            await page.goto(f"{base_url}/items/1")
        
        # Update back button selector
        web_page.back_button = 'a:has-text("Back")'
        web_page.title_selector = 'h1:has-text("Items List")'
        
        # Test back operation
        await web_page.validate_button_operations(
            operation_type=ButtonOperations.BACK_DETAIL,
            form_method=goto_detail
        )
