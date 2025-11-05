"""
Example tests for non-Django applications (React, Vue, generic web apps).

This module demonstrates how to adapt the framework for modern SPAs
and non-Django web applications.

To run these tests:
    pytest tests/examples/test_generic_webapp_example.py --headed
"""

import pytest
from pages.base_page import BasePage
from utils.config import Config


@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.asyncio
class TestReactAppExamples:
    """
    Examples for testing React applications.
    
    React apps often use:
    - Data attributes like data-testid
    - Dynamic class names
    - Client-side routing
    """
    
    async def test_react_navigation(self, page):
        """
        Example: Navigate through a React SPA.
        """
        base_page = BasePage(page)
        base_url = Config.get_base_url()
        
        # Navigate to React app
        await page.goto(base_url)
        
        # Wait for React to load (wait for app root)
        await page.wait_for_selector('[data-testid="app-root"]', timeout=10000)
        
        # Navigate using React Router links
        await page.click('[data-testid="nav-products"]')
        
        # Verify URL changed (client-side routing)
        await page.wait_for_url('**/products')
        
        # Verify page content loaded
        await base_page.is_visible('[data-testid="products-list"]')
    
    async def test_react_form_submission(self, page):
        """
        Example: Test form submission in React app.
        """
        base_page = BasePage(page)
        base_url = Config.get_base_url()
        
        await page.goto(f"{base_url}/add-product")
        
        # React apps often use data-testid attributes
        form_data = {
            '[data-testid="product-name"]': 'New Product',
            '[data-testid="product-price"]': '29.99',
            '[data-testid="product-category"]': 'Electronics',
        }
        
        await base_page.fill_data(form_data)
        
        # Submit form
        await page.click('[data-testid="submit-button"]')
        
        # Wait for success message (React might show a toast)
        await base_page.is_visible('[data-testid="success-toast"]')
    
    async def test_react_api_integration(self, page):
        """
        Example: Test React app with API calls.
        """
        base_page = BasePage(page)
        base_url = Config.get_base_url()
        
        # Intercept API calls to verify React is making correct requests
        async def handle_route(route):
            # You can mock API responses here
            if 'api/products' in route.request.url:
                await route.fulfill(
                    status=200,
                    content_type='application/json',
                    body='[{"id":1,"name":"Product 1"}]'
                )
        
        await page.route('**/api/**', handle_route)
        
        await page.goto(f"{base_url}/products")
        
        # Verify React rendered the mocked data
        await base_page.is_visible('text=Product 1')


@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.asyncio
class TestVueAppExamples:
    """
    Examples for testing Vue.js applications.
    
    Vue apps often use:
    - v-model for two-way binding
    - Transition effects
    - Vuex for state management
    """
    
    async def test_vue_form_validation(self, page):
        """
        Example: Test Vue form with validation.
        """
        base_page = BasePage(page)
        base_url = Config.get_base_url()
        
        await page.goto(f"{base_url}/register")
        
        # Fill form
        await page.fill('input[name="email"]', 'test@example.com')
        await page.fill('input[name="password"]', 'short')  # Too short
        
        # Trigger validation (blur event often triggers Vue validation)
        await page.focus('input[name="password"]')
        await page.focus('input[name="email"]')
        
        # Check for validation error
        await base_page.is_visible('.error-message:has-text("at least 8 characters")')
    
    async def test_vue_reactive_updates(self, page):
        """
        Example: Test Vue's reactive data updates.
        """
        base_page = BasePage(page)
        base_url = Config.get_base_url()
        
        await page.goto(f"{base_url}/counter")
        
        # Get initial count
        initial_count = await page.locator('[data-count]').inner_text()
        
        # Click increment button
        await page.click('button:has-text("Increment")')
        
        # Wait for Vue to update the DOM
        await page.wait_for_timeout(100)
        
        # Verify count increased
        new_count = await page.locator('[data-count]').inner_text()
        assert int(new_count) == int(initial_count) + 1


@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.asyncio  
class TestGenericWebAppExamples:
    """
    Examples for testing generic web applications (non-framework specific).
    """
    
    async def test_ajax_form_submission(self, page):
        """
        Example: Test AJAX form submission.
        """
        base_page = BasePage(page)
        base_url = Config.get_base_url()
        
        await page.goto(f"{base_url}/contact")
        
        # Fill contact form
        form_data = {
            'input[name="name"]': 'John Doe',
            'input[name="email"]': 'john@example.com',
            'textarea[name="message"]': 'This is a test message',
        }
        
        await base_page.fill_data(form_data)
        
        # Submit form via AJAX
        await page.click('button[type="submit"]')
        
        # Wait for success message (AJAX response)
        await page.wait_for_selector('.success-message', timeout=5000)
        await base_page.is_visible('.success-message:has-text("Message sent")')
    
    async def test_dynamic_content_loading(self, page):
        """
        Example: Test dynamically loaded content (infinite scroll, lazy loading).
        """
        base_page = BasePage(page)
        base_url = Config.get_base_url()
        
        await page.goto(f"{base_url}/gallery")
        
        # Count initial items
        initial_items = await page.locator('.gallery-item').count()
        
        # Scroll to bottom to trigger lazy loading
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        
        # Wait for new items to load
        await page.wait_for_timeout(2000)
        
        # Verify more items loaded
        new_items = await page.locator('.gallery-item').count()
        assert new_items > initial_items, "New items should have loaded"
    
    async def test_modal_interaction(self, page):
        """
        Example: Test modal dialog interactions.
        """
        base_page = BasePage(page)
        base_url = Config.get_base_url()
        
        await page.goto(f"{base_url}/products/1")
        
        # Open modal
        await page.click('button:has-text("Add to Cart")')
        
        # Verify modal is visible
        await base_page.is_visible('.modal')
        await base_page.is_visible('.modal-title:has-text("Confirm")')
        
        # Interact with modal
        await page.click('.modal button:has-text("Confirm")')
        
        # Verify modal closed
        await base_page.is_not_visible('.modal')
        
        # Verify action completed
        await base_page.is_visible('.notification:has-text("Added to cart")')
    
    async def test_file_upload(self, page):
        """
        Example: Test file upload functionality.
        """
        base_page = BasePage(page)
        base_url = Config.get_base_url()
        
        await page.goto(f"{base_url}/upload")
        
        # Create a test file
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write('Test file content')
            test_file_path = f.name
        
        try:
            # Upload file
            await page.set_input_files('input[type="file"]', test_file_path)
            
            # Verify file name appears
            await base_page.is_visible(f'text={os.path.basename(test_file_path)}')
            
            # Submit upload
            await page.click('button:has-text("Upload")')
            
            # Verify success
            await base_page.is_visible('.success:has-text("uploaded successfully")')
        finally:
            # Clean up test file
            os.unlink(test_file_path)
    
    async def test_dropdown_selection(self, page):
        """
        Example: Test dropdown/select interactions.
        """
        base_page = BasePage(page)
        base_url = Config.get_base_url()
        
        await page.goto(f"{base_url}/filter")
        
        # Select from dropdown
        await page.select_option('select[name="category"]', 'electronics')
        
        # Verify selection
        selected_value = await page.input_value('select[name="category"]')
        assert selected_value == 'electronics'
        
        # Click filter button
        await page.click('button:has-text("Apply Filter")')
        
        # Verify filtered results
        await base_page.is_visible('.results:has-text("Electronics")')
    
    async def test_keyboard_navigation(self, page):
        """
        Example: Test keyboard navigation and shortcuts.
        """
        base_page = BasePage(page)
        base_url = Config.get_base_url()
        
        await page.goto(base_url)
        
        # Focus on search input
        await page.focus('input[type="search"]')
        
        # Type search query
        await page.keyboard.type('test query')
        
        # Press Enter to submit
        await page.keyboard.press('Enter')
        
        # Verify search results loaded
        await page.wait_for_url('**/search**')
        await base_page.is_visible('.search-results')
    
    async def test_responsive_design(self, page):
        """
        Example: Test responsive design (mobile view).
        """
        base_page = BasePage(page)
        base_url = Config.get_base_url()
        
        # Set mobile viewport
        await page.set_viewport_size({"width": 375, "height": 667})
        
        await page.goto(base_url)
        
        # Mobile menu should be visible
        await base_page.is_visible('.mobile-menu-toggle')
        
        # Desktop menu should be hidden
        await base_page.is_hidden('.desktop-menu')
        
        # Open mobile menu
        await page.click('.mobile-menu-toggle')
        
        # Verify menu opened
        await base_page.is_visible('.mobile-nav')


@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.asyncio
class TestAPIIntegrationExamples:
    """
    Examples showing how to test API integration without backend testing.
    """
    
    async def test_mock_api_response(self, page):
        """
        Example: Mock API responses to test frontend behavior.
        """
        base_page = BasePage(page)
        base_url = Config.get_base_url()
        
        # Mock successful API response
        await page.route('**/api/users', lambda route: route.fulfill(
            status=200,
            content_type='application/json',
            body='{"users": [{"id": 1, "name": "John Doe"}]}'
        ))
        
        await page.goto(f"{base_url}/users")
        
        # Verify UI rendered mocked data
        await base_page.is_visible('text=John Doe')
    
    async def test_api_error_handling(self, page):
        """
        Example: Test how UI handles API errors.
        """
        base_page = BasePage(page)
        base_url = Config.get_base_url()
        
        # Mock API error response
        await page.route('**/api/products', lambda route: route.fulfill(
            status=500,
            content_type='application/json',
            body='{"error": "Internal Server Error"}'
        ))
        
        await page.goto(f"{base_url}/products")
        
        # Verify error message displayed
        await base_page.is_visible('.error-message:has-text("error")')
