import logging
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from utils.exceptions import (
    ElementNotFoundError, 
    ConfigurationError,
    ElementNotVisibleError,
)

logger = logging.getLogger(__name__)

class ContentMixin:
    """
    Mixin for Playwright page content manipulation and retrieval.

    Provides generic, reusable async methods for interacting with and extracting content from web elements.
    Designed to be used as part of a modular Page Object Model for test automation.

    Features:
        - Retrieve text content from elements with visibility checks.
        - Scroll elements into view for reliable interaction.

    Requirements:
        - Requires an initialized Playwright Page instance (self.page).
        - Should be composed with other mixins in a page object class.

    Exception Handling:
        - Raises ElementNotFoundError for missing or invisible elements.
        - Raises ConfigurationError if instantiated without a valid Page.
        - Wraps unexpected errors in RuntimeError for debugging.
    """

    def __init__(self, page: Page) -> None:
        if not page:
            raise ConfigurationError(
                config_key="page",
                message="Page instance cannot be None or empty"
            )
            
        self.page = page

    async def get_text(self, selector: str) -> str:
        """
        Returns the text content of the specified element.

        Args:
            selector (str): Selector of the element.

        Returns:
            str: Text content of the element.

        Raises:
            ElementNotFoundError: if element is not found or not visible.
            ElementNotVisibleError: if element is not visible.

        Notes:
            - Waits for the element to be visible before retrieving the text.
        """
        logger.debug(f"Attempting to get text from element: {selector}")
        try:
            await self.page.wait_for_selector(selector)
            element = self.page.locator(selector)

            if not await element.is_visible():
                raise ElementNotVisibleError(selector, timeout=5000)
            
            logger.debug(f"Successfully retrieved text from element: {selector}")
            return await element.inner_text()
        except PlaywrightTimeoutError as e:
            raise ElementNotFoundError(selector) from e
        except Exception as e:
            raise RuntimeError(f"Error while getting text for selector '{selector}': {e}") from e
        
    
    async def get_attribute(self, selector: str, attribute: str) -> str:
        """
        Returns the value of the specified attribute from the element.

        Args:
            selector (str): Selector of the element.
            attribute (str): Name of the attribute.

        Returns:
            str: Value of the attribute.

        Raises:
            ElementNotFoundError: if element is not found.
            ElementNotVisibleError: if element is not visible.
        """
        logger.debug(f"Getting attribute '{attribute}' from element: {selector}")
        try:
            await self.page.wait_for_selector(selector)
            element = self.page.locator(selector)

            if not await element.is_visible():
                raise ElementNotVisibleError(selector, timeout=5000)

            attribute_value = await element.get_attribute(attribute)
            logger.debug(f"Successfully retrieved attribute '{attribute}' from element: {selector} (value: {attribute_value})")
            return attribute_value
        except PlaywrightTimeoutError as e:
            raise ElementNotFoundError(selector) from e
        except Exception as e:
            raise RuntimeError(f"Error getting attribute '{attribute}' for selector '{selector}': {e}") from e


    async def scroll_into_view(self, selector: str) -> None:
        """
        Scrolls the specified element into view.

        Args:
            selector (str): Selector of the element to scroll into view.

        Raises:
            ElementNotFoundError: if element is not found.
            ElementNotVisibleError: if element is not visible.

        Notes:
            - Ensures the element is visible in the viewport for interactions.
        """
        logger.debug(f"Attempting to scroll element into view: {selector}")
        try:
            await self.page.wait_for_selector(selector)
            element = self.page.locator(selector)

            if not await element.is_visible():
                raise ElementNotVisibleError(selector, timeout=5000)

            logger.debug(f"Successfully scrolled element into view: {selector}")
            await element.scroll_into_view_if_needed()
        except PlaywrightTimeoutError as e:
            raise ElementNotFoundError(selector) from e
        except Exception as e:
            raise RuntimeError(f"Error while scrolling into view for selector '{selector}': {e}") from e
        
    
    async def get_html(self, selector: str) -> str:
        """
        Returns the inner HTML of the specified element.

        Args:
            selector (str): Selector of the element.

        Returns:
            str: Inner HTML of the element.

        Raises:
            ElementNotFoundError: if element is not found.
            ElementNotVisibleError: if element is not visible.
        """
        logger.debug(f"Getting inner HTML from element: {selector}")
        try:
            await self.page.wait_for_selector(selector)
            element = self.page.locator(selector)

            if not await element.is_visible():
                raise ElementNotVisibleError(selector, timeout=5000)

            html = await element.inner_html()
            logger.debug(f"Inner HTML: {html}")
            return html
            
        except PlaywrightTimeoutError as e:
            raise ElementNotFoundError(selector) from e
        except Exception as e:
            raise RuntimeError(f"Error getting inner HTML for selector '{selector}': {e}") from e