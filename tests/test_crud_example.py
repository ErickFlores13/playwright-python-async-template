"""
Example tests demonstrating CRUD operations using proper POM pattern.

This module shows how to use Page Object classes to test CRUD operations.
Tests only call methods from page objects, no direct page interaction.

Demonstrates proper Page Object Model where:
- Page objects encapsulate all page interactions
- Tests only call page object methods
- No direct page/locator usage in tests
- Business logic is in page objects

To run these tests:
    pytest tests/test_crud_example.py --headed -v
"""

import pytest
from pages.examples.user_management_page import UserManagementPage
from pages.examples.product_management_page import ProductManagementPage
from pages.examples.basic_form_page import BasicFormPage
from utils.config import Config


# ========== User Management CRUD Tests ==========

@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.user_management
@pytest.mark.asyncio
async def test_create_user(page):
    """
    Test creating a new user using proper POM.
    
    Only uses page object methods, no direct page interaction.
    """
    # Initialize page object
    user_page = UserManagementPage(page)
    
    # Navigate to create page using page object method
    await user_page.navigate_to_create()
    
    # Create user using page object method
    user_data = {
        'username': 'john_doe',
        'email': 'john@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'role': 'user'
    }
    
    result = await user_page.create_user(user_data)
    assert result is True, "User creation should succeed"
    
    # Verify user appears in list
    await user_page.navigate_to_list()
    users = await user_page.get_all_users()
    created_user = next((u for u in users if u.get("username") == "john_doe"), None)
    assert created_user is not None, "Created user should appear in the list"


@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.user_management
@pytest.mark.asyncio
async def test_search_and_validate_user(page):
    """
    Test searching for users and validating results using proper POM.
    
    All search and validation through page object methods.
    """
    # Initialize page object
    user_page = UserManagementPage(page)
    
    # Navigate to list page
    await user_page.navigate_to_list()
    
    # Search using page object method
    search_results = await user_page.search_users("john")
    assert isinstance(search_results, list), "Search should return a list"
    
    # Filter by role using page object method
    role_results = await user_page.filter_by_role("user")
    assert isinstance(role_results, list), "Role filter should return a list"
    
    # Verify results contain expected data
    if len(search_results) > 0:
        first_user = search_results[0]
        assert "john" in first_user.get("username", "").lower() or \
               "john" in first_user.get("first_name", "").lower(), \
               "Search results should contain 'john'"


@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.user_management
@pytest.mark.asyncio
async def test_edit_user(page):
    """
    Test editing an existing user using proper POM.
    
    Edit operation through page object method.
    """
    # Initialize page object
    user_page = UserManagementPage(page)
    
    # Navigate to list and get existing users
    await user_page.navigate_to_list()
    users = await user_page.get_all_users()
    
    if len(users) == 0:
        # Create a user first if none exist
        await user_page.navigate_to_create()
        user_data = {
            'username': 'edit_test_user',
            'email': 'edit@test.com',
            'first_name': 'Edit',
            'last_name': 'Test'
        }
        await user_page.create_user(user_data)
        await user_page.navigate_to_list()
        users = await user_page.get_all_users()
    
    # Get first user for editing
    first_user = users[0]
    user_id = first_user.get("id")
    
    # Edit user using page object method
    updated_data = {
        'email': 'updated@example.com',
        'first_name': 'Updated',
    }
    
    result = await user_page.update_user(user_id, updated_data)
    assert result is True, "User update should succeed"
    
    # Verify the update
    updated_user = await user_page.get_user_by_id(user_id)
    assert updated_user.get("email") == "updated@example.com", "Email should be updated"


@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.user_management
@pytest.mark.asyncio
async def test_view_user_details(page):
    """
    Test viewing user details using proper POM.
    
    Navigation and validation through page object methods.
    """
    # Initialize page object
    user_page = UserManagementPage(page)
    
    # Navigate to list
    await user_page.navigate_to_list()
    
    # Get all users
    users = await user_page.get_all_users()
    assert len(users) > 0, "Should have at least one user"
    
    # Get details for first user
    first_user = users[0]
    user_id = first_user.get("id")
    
    # Get detailed user information using page object method
    user_details = await user_page.get_user_by_id(user_id)
    assert user_details is not None, "Should retrieve user details"
    assert user_details.get("id") == user_id, "User ID should match"
    
    # Validate required fields exist
    required_fields = ["id", "username", "email"]
    for field in required_fields:
        assert field in user_details, f"User details should contain {field}"


@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.user_management
@pytest.mark.asyncio
async def test_delete_user(page):
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


@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.user_management
@pytest.mark.asyncio
async def test_clear_user_filters(page):
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


# ========== Product Management CRUD Tests ==========

@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.product_management
@pytest.mark.asyncio
async def test_create_product(page):
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


@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.product_management
@pytest.mark.asyncio
async def test_search_products(page):
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


@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.product_management
@pytest.mark.asyncio
async def test_update_product(page):
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


@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.product_management
@pytest.mark.asyncio
async def test_view_product_details(page):
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


@pytest.mark.skip(reason="Example test - customize for your application")
@pytest.mark.product_management
@pytest.mark.asyncio
async def test_delete_product(page):
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