"""
Example tests for generic web applications using proper POM pattern.

This module demonstrates how to test modern SPAs (React, Vue, Angular)
and generic web applications using Page Object Model pattern.

To run these tests:
    pytest tests/examples/test_generic_webapp_example.py --headed
"""

import pytest
from pages.examples.spa_products_page import SPAProductsPage
from utils.config import Config


@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.asyncio
class TestReactAppExamples:
    """
    Examples for testing React applications using POM.
    
    Tests only call page object methods, no direct page interaction.
    """
    
    async def test_navigate_spa(self, page):
        """
        Test navigation in a React SPA.
        
        Uses page object methods for navigation and verification.
        """
        # Initialize page object
        spa_page = SPAProductsPage(page)
        base_url = Config.get_base_url()
        
        # Navigate to app using page object method
        await spa_page.navigate_to_app(base_url)
        
        # Navigate to products using page object method (client-side routing)
        await spa_page.navigate_to_products()
    
    async def test_add_product_to_cart(self, page):
        """
        Test adding product to cart in React app.
        
        All interactions through page object methods.
        """
        # Initialize page object
        spa_page = SPAProductsPage(page)
        base_url = Config.get_base_url()
        
        # Navigate using page object methods
        await spa_page.navigate_to_app(base_url)
        await spa_page.navigate_to_products()
        
        # Add product to cart using page object method
        await spa_page.add_product_to_cart(product_index=0)
        
        # Verify cart updated using page object method
        cart_updated = await spa_page.verify_cart_updated()
        assert cart_updated, "Cart should be updated after adding product"
    
    async def test_submit_form_in_spa(self, page):
        """
        Test form submission in React/Vue app.
        
        Form interaction through page object method.
        """
        # Initialize page object
        spa_page = SPAProductsPage(page)
        base_url = Config.get_base_url()
        
        # Navigate
        await spa_page.navigate_to_app(base_url)
        
        # Submit form using page object method
        product_data = {
            'name': 'New Product',
            'price': '29.99',
            'category': 'Electronics',
        }
        await spa_page.submit_product_form(product_data)
        
        # Verify success using page object method
        await spa_page.verify_success_notification('Product added successfully')
    
    async def test_infinite_scroll(self, page):
        """
        Test infinite scroll / lazy loading in SPA.
        
        Scroll and count through page object methods.
        """
        # Initialize page object
        spa_page = SPAProductsPage(page)
        base_url = Config.get_base_url()
        
        # Navigate
        await spa_page.navigate_to_app(base_url)
        await spa_page.navigate_to_products()
        
        # Get initial count using page object method
        initial_count = await spa_page.get_product_count()
        
        # Scroll to load more using page object method
        await spa_page.scroll_to_load_more()
        
        # Get new count using page object method
        new_count = await spa_page.get_product_count()
        
        assert new_count > initial_count, "More products should load after scrolling"


@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.asyncio
class TestVueAppExamples:
    """
    Examples for testing Vue.js applications using POM.
    
    Note: Create a dedicated Vue page object similar to SPAProductsPage
    for your specific Vue application.
    """
    
    async def test_vue_reactive_updates(self, page):
        """
        Test Vue's reactive data updates.
        
        In production: create a page object with methods for your Vue components.
        Example structure shown in comments.
        """
        # Initialize your Vue page object
        # vue_page = VueCounterPage(page)
        # base_url = Config.get_base_url()
        
        # Navigate using page object method
        # await vue_page.navigate_to_counter(base_url)
        
        # Get initial count using page object method
        # initial_count = await vue_page.get_counter_value()
        
        # Increment using page object method
        # await vue_page.increment_counter()
        
        # Get new count using page object method
        # new_count = await vue_page.get_counter_value()
        
        # assert new_count == initial_count + 1
        pass


@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.asyncio
class TestGenericWebAppExamples:
    """
    Examples for testing generic web applications using POM.
    
    Create page objects for your specific application modules.
    """
    
    async def test_ajax_form_submission(self, page):
        """
        Test AJAX form submission.
        
        In production: create a page object with form submission methods.
        """
        # Example structure:
        # contact_page = ContactFormPage(page)
        # base_url = Config.get_base_url()
        
        # Navigate using page object method
        # await contact_page.navigate_to_contact(base_url)
        
        # Submit form using page object method
        # form_data = {
        #     'name': 'John Doe',
        #     'email': 'john@example.com',
        #     'message': 'Test message',
        # }
        # await contact_page.submit_contact_form(form_data)
        
        # Verify success using page object method
        # await contact_page.verify_submission_success()
        pass
    
    async def test_file_upload(self, page):
        """
        Test file upload functionality.
        
        In production: implement upload_file() method in your page object.
        """
        # Example structure:
        # upload_page = FileUploadPage(page)
        # base_url = Config.get_base_url()
        
        # Navigate using page object method
        # await upload_page.navigate_to_upload(base_url)
        
        # Upload file using page object method
        # test_file_path = '/path/to/test/file.txt'
        # await upload_page.upload_file(test_file_path)
        
        # Verify upload using page object method
        # await upload_page.verify_upload_success()
        pass
    
    async def test_modal_interaction(self, page):
        """
        Test modal dialog interactions.
        
        In production: implement modal-related methods in your page object.
        """
        # Example structure:
        # product_page = ProductDetailsPage(page)
        # base_url = Config.get_base_url()
        
        # Navigate using page object method
        # await product_page.navigate_to_product(base_url, product_id=1)
        
        # Open modal using page object method
        # await product_page.open_add_to_cart_modal()
        
        # Verify modal is visible using page object method
        # await product_page.verify_modal_visible()
        
        # Confirm action using page object method
        # await product_page.confirm_add_to_cart()
        
        # Verify modal closed and action completed
        # await product_page.verify_modal_closed()
        # await product_page.verify_notification('Added to cart')
        pass


# ============================================================================
# IMPORTANT: Page Object Model (POM) Best Practices
# ============================================================================
#
# 1. CREATE PAGE OBJECTS for each module/page:
#    - pages/examples/user_management_page.py
#    - pages/examples/product_management_page.py
#    - pages/examples/spa_products_page.py
#
# 2. ENCAPSULATE ALL SELECTORS in the page object class
#    - Don't use selectors in test files
#    - All locators should be in the page object
#
# 3. CREATE METHODS for all actions:
#    - navigate_to_module()
#    - create_item(data)
#    - search_items(criteria)
#    - edit_item(data)
#    - delete_item()
#    - verify_success(message)
#
# 4. TEST FILES should ONLY call page object methods:
#    - No page.click(), page.fill(), etc. in tests
#    - Tests should read like business workflows
#    - High-level, readable test code
#
# 5. EXTEND StandardWebPage for CRUD modules:
#    - Inherit from StandardWebPage
#    - Override selectors for your module
#    - Add module-specific methods
#
# Example:
#   # Good (POM pattern)
#   user_page = UserManagementPage(page)
#   await user_page.create_user(user_data)
#   await user_page.verify_success_message("User created")
#
#   # Bad (not POM)
#   await page.goto("http://app.com/users/create")
#   await page.fill("#username", "john")
#   await page.click("button[type='submit']")
#
