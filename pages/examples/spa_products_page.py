"""
Example Page Object for Single Page Applications (React, Vue, Angular).

Demonstrates POM pattern for modern SPAs with client-side routing.
"""

from pages.base_page import BasePage
from playwright.async_api import Page


class SPAProductsPage(BasePage):
    """
    Page Object for a Products page in an SPA application.
    
    Example for React/Vue/Angular applications with client-side routing.
    """
    
    def __init__(self, page: Page):
        super().__init__(page)
        
        # SPA-specific selectors (using data-testid pattern common in SPAs)
        self.app_root = '[data-testid="app-root"]'
        self.nav_products = '[data-testid="nav-products"]'
        self.products_list = '[data-testid="products-list"]'
        self.product_card = '[data-testid="product-card"]'
        self.add_to_cart_button = '[data-testid="add-to-cart"]'
        self.cart_icon = '[data-testid="cart-icon"]'
        self.notification_toast = '[data-testid="notification-toast"]'
        
        # Form selectors
        self.product_name_field = '[data-testid="product-name"]'
        self.product_price_field = '[data-testid="product-price"]'
        self.product_category_field = '[data-testid="product-category"]'
        self.submit_button = '[data-testid="submit-button"]'
    
    async def navigate_to_app(self, base_url: str) -> None:
        """Navigate to the SPA and wait for it to load."""
        await self.page.goto(base_url)
        await self.wait_for_selector(self.app_root)
    
    async def navigate_to_products(self) -> None:
        """Navigate to products page using SPA navigation."""
        await self.page.click(self.nav_products)
        # Wait for URL change (client-side routing)
        await self.page.wait_for_url('**/products')
        await self.is_visible(self.products_list)
    
    async def add_product_to_cart(self, product_index: int = 0) -> None:
        """
        Add a product to cart.
        
        Args:
            product_index: Index of the product to add (default: first product)
        """
        product_cards = self.page.locator(self.product_card)
        await product_cards.nth(product_index).locator(self.add_to_cart_button).click()
        
        # Wait for notification toast
        await self.is_visible(self.notification_toast)
    
    async def verify_cart_updated(self) -> bool:
        """
        Verify that cart icon shows updated count.
        
        Returns:
            True if cart was updated
        """
        cart = self.page.locator(self.cart_icon)
        return await cart.is_visible()
    
    async def submit_product_form(self, product_data: dict) -> None:
        """
        Submit product form in SPA.
        
        Args:
            product_data: Dictionary with product information
        """
        form_data = {
            self.product_name_field: product_data.get('name', ''),
            self.product_price_field: product_data.get('price', ''),
            self.product_category_field: product_data.get('category', ''),
        }
        
        await self.fill_data(form_data)
        await self.page.click(self.submit_button)
        
        # Wait for success notification
        await self.is_visible(self.notification_toast)
    
    async def verify_success_notification(self, message: str) -> None:
        """
        Verify success notification appears with expected message.
        
        Args:
            message: Expected notification message
        """
        notification = self.page.locator(self.notification_toast)
        await self.page.wait_for_selector(self.notification_toast)
        text = await notification.inner_text()
        assert message in text, f"Expected '{message}' in notification"
    
    async def get_product_count(self) -> int:
        """
        Get the number of products displayed.
        
        Returns:
            Number of product cards visible
        """
        return await self.page.locator(self.product_card).count()
    
    async def scroll_to_load_more(self) -> None:
        """Scroll to bottom to trigger lazy loading (infinite scroll)."""
        await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await self.page.wait_for_timeout(2000)  # Wait for new items to load
