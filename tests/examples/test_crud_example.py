"""
Example tests demonstrating CRUD operations using proper POM pattern.

This module shows how to use Page Object classes to test CRUD operations.
Tests only call methods from page objects, no direct page interaction.

To run these tests:
    pytest tests/examples/test_crud_example.py --headed
"""

import pytest
from pages.examples.user_management_page import UserManagementPage
from pages.examples.product_management_page import ProductManagementPage
from utils.config import Config


@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.asyncio
class TestUserManagementCRUD:
    """
    Example test class for User Management CRUD operations.
    
    Demonstrates proper POM: tests only call page object methods.
    All selectors and page interactions are in UserManagementPage class.
    """
    
    async def test_create_user(self, page):
        """
        Test creating a new user.
        
        Uses page object method to create user, no direct page interaction.
        """
        # Initialize page object
        user_page = UserManagementPage(page)
        base_url = Config.get_base_url()
        
        # Navigate to module using page object method
        await user_page.navigate_to_module(base_url)
        
        # Create user using page object method
        user_data = {
            'username': 'john_doe',
            'email': 'john@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'Admin',
            'is_active': True,
        }
        await user_page.create_user(user_data)
        
        # Verify success using page object method
        await user_page.verify_success_message("User created successfully")
    
    async def test_search_and_validate_user(self, page):
        """
        Test searching for users and validating results.
        
        All search and validation through page object methods.
        """
        # Initialize page object
        user_page = UserManagementPage(page)
        base_url = Config.get_base_url()
        
        # Navigate to module
        await user_page.navigate_to_module(base_url)
        
        # Search using page object method
        search_filters = {
            'username': 'john_doe',
            'role': 'Admin',
        }
        
        # Apply filters and validate using page object method
        await user_page.apply_filters_and_validate(search_filters)
    
    async def test_edit_user(self, page):
        """
        Test editing an existing user.
        
        Edit operation through page object method.
        """
        # Initialize page object
        user_page = UserManagementPage(page)
        base_url = Config.get_base_url()
        
        # Navigate and search for user
        await user_page.navigate_to_module(base_url)
        await user_page.search_user({'username': 'john_doe'})
        
        # Edit user using page object method
        updated_data = {
            'email': 'john.doe@example.com',
            'role': 'Manager',
        }
        await user_page.edit_user(updated_data)
        
        # Verify success
        await user_page.verify_success_message("User updated successfully")
    
    async def test_view_user_details(self, page):
        """
        Test viewing user details.
        
        Navigation and validation through page object methods.
        """
        # Initialize page object
        user_page = UserManagementPage(page)
        base_url = Config.get_base_url()
        
        # Navigate and search
        await user_page.navigate_to_module(base_url)
        await user_page.search_user({'username': 'john_doe'})
        
        # View details using page object method
        await user_page.view_user_details()
        
        # Validate details using page object method
        expected_data = {
            'username': 'john_doe',
            'email': 'john.doe@example.com',
            'full_name': 'John Doe',
            'role': 'Manager',
        }
        await user_page.validate_user_details(expected_data)
    
    async def test_delete_user(self, page):
        """
        Test deleting a user.
        
        Delete operation through page object method.
        """
        # Initialize page object
        user_page = UserManagementPage(page)
        base_url = Config.get_base_url()
        
        # Navigate and search
        await user_page.navigate_to_module(base_url)
        await user_page.search_user({'username': 'john_doe'})
        
        # Delete using page object method
        await user_page.delete_user()
        
        # Verify success
        await user_page.verify_success_message("User deleted successfully")
    
    async def test_clear_filters(self, page):
        """
        Test clearing search filters.
        
        Filter operations through page object methods.
        """
        # Initialize page object
        user_page = UserManagementPage(page)
        base_url = Config.get_base_url()
        
        # Navigate and apply filters
        await user_page.navigate_to_module(base_url)
        
        filter_fields = {
            user_page.username_input: 'test',
            user_page.role_select: 'Admin',
        }
        
        # Apply and then clear filters using page object methods
        await user_page.search_user({'username': 'test', 'role': 'Admin'})
        await user_page.clear_all_filters(filter_fields)


@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.asyncio
class TestProductManagementCRUD:
    """
    Example test class for Product Management CRUD operations.
    
    Demonstrates POM pattern for a different module type (e-commerce).
    """
    
    async def test_create_product(self, page):
        """
        Test creating a new product.
        
        Uses ProductManagementPage methods only.
        """
        # Initialize page object
        product_page = ProductManagementPage(page)
        base_url = Config.get_base_url()
        
        # Navigate using page object method
        await product_page.navigate_to_products(base_url)
        
        # Create product using page object method
        product_data = {
            'name': 'Widget Pro',
            'description': 'Premium widget for professionals',
            'price': '99.99',
            'sku': 'WGT-PRO-001',
            'category': 'Electronics',
            'stock': '50',
            'is_active': True,
            'is_featured': True,
        }
        await product_page.create_product(product_data)
        
        # Verify using page object method
        await product_page.verify_operation_success("Product created successfully")
    
    async def test_search_products(self, page):
        """
        Test searching for products.
        
        Search and validation through page object methods.
        """
        # Initialize page object
        product_page = ProductManagementPage(page)
        base_url = Config.get_base_url()
        
        # Navigate
        await product_page.navigate_to_products(base_url)
        
        # Search using page object method
        search_criteria = {
            'name': 'Widget',
            'category': 'Electronics',
        }
        await product_page.search_products(search_criteria)
        
        # Validate results using page object method
        await product_page.validate_product_in_list({'name': 'Widget Pro'})
    
    async def test_update_product(self, page):
        """
        Test updating a product.
        
        Update through page object method.
        """
        # Initialize page object
        product_page = ProductManagementPage(page)
        base_url = Config.get_base_url()
        
        # Navigate and search
        await product_page.navigate_to_products(base_url)
        await product_page.search_products({'name': 'Widget Pro'})
        
        # Update using page object method
        updated_data = {
            'price': '149.99',
            'stock': '100',
            'is_featured': False,
        }
        await product_page.update_product(updated_data)
        
        # Verify
        await product_page.verify_operation_success("Product updated successfully")
    
    async def test_view_product_details(self, page):
        """
        Test viewing product details.
        
        Detail view and validation through page object methods.
        """
        # Initialize page object
        product_page = ProductManagementPage(page)
        base_url = Config.get_base_url()
        
        # Navigate and search
        await product_page.navigate_to_products(base_url)
        await product_page.search_products({'sku': 'WGT-PRO-001'})
        
        # View details using page object method
        await product_page.view_product_details()
        
        # Validate using page object method
        expected_data = {
            'name': 'Widget Pro',
            'price': '149.99',
            'sku': 'WGT-PRO-001',
            'stock': '100',
        }
        await product_page.validate_product_details(expected_data)
    
    async def test_delete_product(self, page):
        """
        Test deleting a product.
        
        Delete through page object method.
        """
        # Initialize page object
        product_page = ProductManagementPage(page)
        base_url = Config.get_base_url()
        
        # Navigate and search
        await product_page.navigate_to_products(base_url)
        await product_page.search_products({'sku': 'WGT-PRO-001'})
        
        # Delete using page object method
        await product_page.delete_product()
        
        # Verify
        await product_page.verify_operation_success("Product deleted successfully")


# NOTE: For form validation, button operations, and filter testing,
# implement dedicated methods in your page object classes following
# the same POM pattern shown above. Each page object should encapsulate
# all the logic for its module, and tests should only call those methods.
