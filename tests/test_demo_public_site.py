"""
Practical example test using a public demo website.

This test demonstrates the framework using a real public website,
so you can run it immediately to see the framework in action.

To run: pytest tests/test_demo_public_site.py --headed
"""

import pytest
from pages.base_page import BasePage
from playwright.async_api import expect


@pytest.mark.asyncio
class TestPublicDemoSite:
    """
    Tests using a public demo website to showcase framework capabilities.
    Uses https://the-internet.herokuapp.com/ as it's a stable testing ground.
    """
    
    async def test_basic_navigation_and_interaction(self, page):
        """
        Test basic navigation and interaction with a public demo site.
        
        This demonstrates:
        - Page navigation
        - Element visibility checking
        - Basic interactions
        """
        base_page = BasePage(page)
        
        # Navigate to the demo site
        await page.goto('https://the-internet.herokuapp.com/')
        
        # Verify page title
        await expect(page).to_have_title('The Internet')
        
        # Check that several links are visible
        await base_page.is_visible('a:has-text("Form Authentication")')
        await base_page.is_visible('a:has-text("Dropdown")')
        await base_page.is_visible('a:has-text("Checkboxes")')
    
    async def test_form_interaction(self, page):
        """
        Test form filling and submission.
        
        This demonstrates the fill_data method with a real form.
        """
        base_page = BasePage(page)
        
        # Navigate to login page
        await page.goto('https://the-internet.herokuapp.com/login')
        
        # Fill login form using fill_data
        await base_page.fill_data({
            '#username': 'tomsmith',
            '#password': 'SuperSecretPassword!',
        })
        
        # Submit form
        await page.click('button[type="submit"]')
        
        # Verify successful login
        await base_page.is_visible('.flash.success')
        await expect(page.locator('.flash.success')).to_contain_text('You logged into a secure area!')
    
    async def test_checkboxes(self, page):
        """
        Test checkbox interaction.
        
        This demonstrates handling checkboxes with fill_data.
        """
        base_page = BasePage(page)
        
        # Navigate to checkboxes page
        await page.goto('https://the-internet.herokuapp.com/checkboxes')
        
        # Get initial state of checkboxes
        checkbox1 = page.locator('input[type="checkbox"]').nth(0)
        checkbox2 = page.locator('input[type="checkbox"]').nth(1)
        
        # Check first checkbox if not checked
        is_checked = await checkbox1.is_checked()
        if not is_checked:
            await checkbox1.check()
        
        # Verify it's now checked
        await expect(checkbox1).to_be_checked()
    
    async def test_dropdown_selection(self, page):
        """
        Test dropdown selection.
        
        This demonstrates handling select elements.
        """
        base_page = BasePage(page)
        
        # Navigate to dropdown page
        await page.goto('https://the-internet.herokuapp.com/dropdown')
        
        # Select an option
        await page.select_option('#dropdown', 'Option 1')
        
        # Verify selection
        selected_value = await page.input_value('#dropdown')
        assert selected_value == '1', "Dropdown should have 'Option 1' selected"
    
    async def test_dynamic_loading(self, page):
        """
        Test waiting for dynamically loaded content.
        
        This demonstrates wait_for_selector functionality.
        """
        base_page = BasePage(page)
        
        # Navigate to dynamic loading page
        await page.goto('https://the-internet.herokuapp.com/dynamic_loading/2')
        
        # Click start button
        await page.click('button:has-text("Start")')
        
        # Wait for the dynamically loaded element
        await base_page.wait_for_selector('#finish', time_sleep=0.1)
        
        # Verify the content
        await expect(page.locator('#finish')).to_contain_text('Hello World!')
    
    async def test_multiple_elements(self, page):
        """
        Test working with multiple elements.
        
        This demonstrates finding and interacting with multiple elements.
        """
        base_page = BasePage(page)
        
        # Navigate to add/remove elements page
        await page.goto('https://the-internet.herokuapp.com/add_remove_elements/')
        
        # Add 3 elements
        for i in range(3):
            await page.click('button:has-text("Add Element")')
        
        # Count added elements
        delete_buttons = page.locator('.added-manually')
        count = await delete_buttons.count()
        assert count == 3, "Should have 3 delete buttons"
        
        # Remove one element
        await delete_buttons.first.click()
        
        # Verify count decreased
        count_after = await delete_buttons.count()
        assert count_after == 2, "Should have 2 delete buttons after deletion"
    
    async def test_hover_interaction(self, page):
        """
        Test hover interactions.
        
        This demonstrates hover functionality.
        """
        base_page = BasePage(page)
        
        # Navigate to hovers page
        await page.goto('https://the-internet.herokuapp.com/hovers')
        
        # Hover over first avatar
        first_avatar = page.locator('.figure').first
        await first_avatar.hover()
        
        # Verify caption appears
        caption = first_avatar.locator('.figcaption')
        await expect(caption).to_be_visible()
        await expect(caption).to_contain_text('name: user1')


@pytest.mark.asyncio
class TestDemoFormValidation:
    """
    Additional examples showing form validation patterns.
    """
    
    async def test_file_upload(self, page):
        """
        Test file upload functionality.
        """
        import tempfile
        import os
        
        base_page = BasePage(page)
        
        # Navigate to file upload page
        await page.goto('https://the-internet.herokuapp.com/upload')
        
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write('Test file content for automation')
            test_file_path = f.name
        
        try:
            # Upload the file
            await page.set_input_files('input[type="file"]', test_file_path)
            
            # Submit upload
            await page.click('#file-submit')
            
            # Verify upload success
            await base_page.is_visible('h3:has-text("File Uploaded!")')
            
            # Verify filename appears
            uploaded_files = page.locator('#uploaded-files')
            await expect(uploaded_files).to_contain_text(os.path.basename(test_file_path))
        finally:
            # Clean up temp file
            os.unlink(test_file_path)
    
    async def test_javascript_alerts(self, page):
        """
        Test handling JavaScript alerts.
        
        This demonstrates alert handling.
        """
        base_page = BasePage(page)
        
        # Navigate to JavaScript alerts page
        await page.goto('https://the-internet.herokuapp.com/javascript_alerts')
        
        # Handle alert dialog
        page.on('dialog', lambda dialog: dialog.accept())
        
        # Click button that triggers alert
        await page.click('button:has-text("Click for JS Alert")')
        
        # Verify result
        result = page.locator('#result')
        await expect(result).to_contain_text('You successfully clicked an alert')


# Instructions for running these tests:
"""
These tests use a public demo website, so you can run them immediately:

1. Run all demo tests:
   pytest tests/test_demo_public_site.py --headed

2. Run specific test:
   pytest tests/test_demo_public_site.py::TestPublicDemoSite::test_form_interaction --headed

3. Run with Allure report:
   pytest tests/test_demo_public_site.py --alluredir=reports/allure-results
   allure serve reports/allure-results

These tests demonstrate:
- Basic navigation and element visibility
- Form filling and submission
- Checkbox handling
- Dropdown selection
- Dynamic content waiting
- Multiple element interaction
- Hover functionality
- File upload
- Alert handling

Use these as templates for your own application tests!
"""
