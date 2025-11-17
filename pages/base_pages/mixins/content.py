import logging
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from utils.exceptions import (ElementNotFoundError)

logger = logging.getLogger(__name__)

class ContentMixin:
    """
    Mixin for Playwright page content manipulation and retrieval.

    Provides generic, reusable async methods for interacting with and extracting content from web elements.
    Designed to be used as part of a modular Page Object Model for test automation.

    Features:
        - Retrieve text content, inner HTML, or attributes from elements with visibility ensured.
        - Scroll elements into view for reliable interaction.

    Requirements:
        - Requires an initialized Playwright Page instance (self.page).
        - Should be composed with other mixins in a page object class.

    Exception Handling:
        - Raises ElementNotFoundError if a targeted element is not found or not visible.
    """


    async def get_text(self, selector: str) -> str:
        """
        Returns the text content of the specified element after ensuring it is visible.

        Args:
            selector (str): Selector of the element.

        Returns:
            str: Text content of the element.

        Raises:
            ElementNotFoundError: If the element is not found or not visible within the timeout.

        Notes:
            - Uses _wait_for_visible_element to ensure visibility before retrieving text.
        """
        logger.debug(f"Attempting to get text from element: {selector}")
        element = await self._wait_for_visible_element(selector)
        logger.debug(f"Successfully retrieved text from element: {selector}")
        return await element.inner_text()
    

    async def get_attribute(self, selector: str, attribute: str) -> str:
        """
        Returns the value of the specified attribute from the element after ensuring it is visible.

        Args:
            selector (str): Selector of the element.
            attribute (str): Name of the attribute.

        Returns:
            str: Value of the attribute.

        Raises:
            ElementNotFoundError: If the element is not found or not visible within the timeout.

        Notes:
            - Uses _wait_for_visible_element to ensure visibility before retrieving the attribute value.
        """
        logger.debug(f"Getting attribute '{attribute}' from element: {selector}")
        element = await self._wait_for_visible_element(selector)
        attribute_value = await element.get_attribute(attribute)
        logger.debug(f"Successfully retrieved attribute '{attribute}' from element: {selector} (value: {attribute_value})")
        return attribute_value


    async def scroll_into_view(self, selector: str) -> None:
        """
        Scrolls the specified element into view after ensuring it is visible.

        Args:
            selector (str): Selector of the element to scroll into view.

        Raises:
            ElementNotFoundError: If the element is not found or not visible within the timeout.

        Notes:
            - Uses _wait_for_visible_element to ensure visibility before scrolling.
        """
        logger.debug(f"Attempting to scroll element into view: {selector}")
        element = await self._wait_for_visible_element(selector)
        logger.debug(f"Successfully scrolled element into view: {selector}")
        await element.scroll_into_view_if_needed()
        
    
    async def get_html(self, selector: str) -> str:
        """
        Returns the inner HTML of the specified element after ensuring it is visible.

        Args:
            selector (str): Selector of the element.

        Returns:
            str: Inner HTML of the element.

        Raises:
            ElementNotFoundError: If the element is not found or not visible within the timeout.

        Notes:
            - Uses _wait_for_visible_element to ensure visibility before retrieving inner HTML.
        """
        logger.debug(f"Getting inner HTML from element: {selector}")
        element = await self._wait_for_visible_element(selector)
        html = await element.inner_html()
        logger.debug(f"Inner HTML: {html}")
        return html
        
        
    async def _wait_for_visible_element(self, selector: str):
        """
        Waits for the element matching the selector to be visible and returns its locator.

        Args:
            selector (str): Selector of the element to wait for.

        Returns:
            Locator: Playwright locator for the visible element.

        Raises:
            ElementNotFoundError: If the element is not found or not visible within the timeout.

        Notes:
            - Uses Playwright's wait_for_selector with state="visible" for robust visibility checks.
        """
        try:
            await self.page.wait_for_selector(selector, state="visible")
            return self.page.locator(selector)
        except PlaywrightTimeoutError as e:
            raise ElementNotFoundError(selector) from e