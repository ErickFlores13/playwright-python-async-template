"""
Example Page Object for a Product Management module (e-commerce example).

This demonstrates proper POM pattern for a different type of module.
"""

from pages.standard_web_page import StandardWebPage
from playwright.async_api import Page


class ProductManagementPage(StandardWebPage):
    """
    Page Object for Product Management module.
    
    Example for e-commerce or inventory management systems.
    All product-related operations are encapsulated here.
    """
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # Module-specific selectors
        self.add_product_button = 'button:has-text("Add Product")'
        self.edit_button = 'a.edit-product'
        self.view_button = 'a.view-product'
        
        # Form field selectors
        self.product_name_input = 'input[name="name"]'
        self.product_description = 'textarea[name="description"]'
        self.product_price = 'input[name="price"]'
        self.product_sku = 'input[name="sku"]'
        self.product_category = 'select[name="category"]'
        self.product_stock = 'input[name="stock"]'
        self.product_active = 'input[name="is_active"]'
        self.product_featured = 'input[name="is_featured"]'
        
        # Override base selectors
        self.submit_button_selector = 'button:has-text("Save Product")'
        self.delete_button_selector = 'button.delete-product'
        self.confirm_delete_button_selector = 'button:has-text("Yes, Delete")'
        self.filter_button_selector = 'button:has-text("Apply Filters")'
        self.table_selector = '#products-table'
        self.title_selector = 'h1:has-text("Product Management")'
        
    async def navigate_to_products(self, base_url: str) -> None:
        """Navigate to the product management page."""
        await self.page.goto(f"{base_url}/products")
        await self.is_visible(self.title_selector)
    
    async def open_add_product_form(self) -> None:
        """Open the form to add a new product."""
        await self.page.click(self.add_product_button)
        await self.page.wait_for_load_state("domcontentloaded")
    
    async def create_product(self, product_data: dict) -> None:
        """
        Create a new product.
        
        Args:
            product_data: Dictionary with product information
                Example: {
                    'name': 'Widget Pro',
                    'description': 'Premium widget',
                    'price': '99.99',
                    'sku': 'WGT-001',
                    'category': 'Electronics',
                    'stock': '50',
                    'is_active': True,
                    'is_featured': False
                }
        """
        await self.open_add_product_form()
        
        form_data = {
            self.product_name_input: product_data.get('name', ''),
            self.product_description: product_data.get('description', ''),
            self.product_price: product_data.get('price', ''),
            self.product_sku: product_data.get('sku', ''),
            self.product_category: product_data.get('category', ''),
            self.product_stock: product_data.get('stock', ''),
            self.product_active: product_data.get('is_active', True),
            self.product_featured: product_data.get('is_featured', False),
        }
        
        await self.fill_data(form_data)
        await self.page.click(self.submit_button_selector)
        await self.page.wait_for_load_state("domcontentloaded")
    
    async def search_products(self, search_criteria: dict) -> None:
        """
        Search for products using various criteria.
        
        Args:
            search_criteria: Dictionary with search parameters
                Example: {'name': 'Widget', 'category': 'Electronics'}
        """
        filter_data = {}
        
        if 'name' in search_criteria:
            filter_data[self.product_name_input] = search_criteria['name']
        if 'sku' in search_criteria:
            filter_data[self.product_sku] = search_criteria['sku']
        if 'category' in search_criteria:
            filter_data[self.product_category] = search_criteria['category']
        
        await self.search_with_filters(filter_data)
    
    async def update_product(self, updated_data: dict) -> None:
        """
        Update an existing product.
        
        Args:
            updated_data: Dictionary with fields to update
        """
        await self.page.click(self.edit_button)
        await self.page.wait_for_load_state("domcontentloaded")
        
        form_data = {}
        for key in ['name', 'description', 'price', 'sku', 'category', 'stock']:
            if key in updated_data:
                selector = getattr(self, f'product_{key}' if key != 'description' else 'product_description')
                form_data[selector] = updated_data[key]
        
        if 'is_active' in updated_data:
            form_data[self.product_active] = updated_data['is_active']
        if 'is_featured' in updated_data:
            form_data[self.product_featured] = updated_data['is_featured']
        
        await self.edit_item(form_data)
    
    async def delete_product(self) -> None:
        """Delete the current product."""
        await self.delete_item()
    
    async def view_product_details(self) -> None:
        """Navigate to product detail view."""
        await self.page.click(self.view_button)
        await self.page.wait_for_load_state("domcontentloaded")
    
    async def validate_product_in_list(self, product_data: dict) -> None:
        """
        Validate that product appears in the list with correct information.
        
        Args:
            product_data: Expected product data to validate
        """
        await self.validate_table_data(product_data)
    
    async def validate_product_details(self, expected_data: dict) -> None:
        """
        Validate product information in detail view.
        
        Args:
            expected_data: Expected product details
        """
        validation_data = {}
        
        for field in ['name', 'description', 'price', 'sku', 'category', 'stock']:
            if field in expected_data:
                validation_data[f'span[data-field="{field}"]'] = expected_data[field]
        
        await self.validate_record_information_in_details_view(validation_data)
    
    async def verify_operation_success(self, message: str) -> None:
        """
        Verify success message after an operation.
        
        Args:
            message: Expected success message
        """
        await self.check_message(message)
