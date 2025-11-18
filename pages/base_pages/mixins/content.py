import logging
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import Locator
from utils.exceptions import ElementNotFoundError

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
    """


    async def get_text(self, selector: str , timeout: float = None) -> str:
        """
        Retrieve the text content of an element after ensuring it is visible.

        Args:
            selector (str): Selector of the element.
            timeout (float, optional): Maximum wait time (ms) for the element
                to become visible. Defaults to Playwright's timeout.

        Returns:
            str: The element's text content.

        Raises:
            playwright.async_api.TimeoutError: If the element does not become
                visible within the specified timeout.
        """
        logger.debug(f"Attempting to get text from element: {selector}")

        locator = self.page.locator(selector)
        await locator.wait_for(state="visible", timeout=timeout)

        logger.debug(f"Successfully retrieved text from element: {selector}")
        return await locator.inner_text()
    

    async def get_attribute(self, selector: str, attribute: str, timeout: float = None) -> str:
        """
        Retrieve the value of an attribute from an element after ensuring it is visible.

        Args:
            selector (str): Selector of the target element.
            attribute (str): Attribute name to retrieve.
            timeout (float, optional): Maximum wait time (ms) for the element
                to become visible. Defaults to Playwright's timeout.

        Returns:
            str | None: The attribute value, or None if the attribute does not exist.

        Raises:
            playwright.async_api.TimeoutError: If the element does not become
                visible within the specified timeout.
        """
        logger.debug(f"Getting attribute '{attribute}' from element: {selector}")

        locator = self.page.locator(selector)
        await locator.wait_for(state="visible", timeout=timeout)
        attribute_value = await locator.get_attribute(attribute)

        logger.debug(f"Successfully retrieved attribute '{attribute}' from element: {selector} (value: {attribute_value})")
        return attribute_value


    async def scroll_into_view(self, selector: str, timeout: float = None) -> None:
        """
        Scroll the target element into view after ensuring it is visible.

        Args:
            selector (str): Selector of the element to scroll into view.
            timeout (float, optional): Maximum wait time (ms) for the element
                to become visible. Defaults to Playwright's timeout.

        Raises:
            playwright.async_api.TimeoutError: If the element does not become
                visible within the specified timeout.
        """
        logger.debug(f"Attempting to scroll element into view: {selector}")

        locator = self.page.locator(selector)
        await locator.wait_for(state="visible", timeout=timeout)

        logger.debug(f"Successfully scrolled element into view: {selector}")
        await locator.scroll_into_view_if_needed()
        
    
    async def get_html(self, selector: str, timeout: float = None) -> str:
        """
        Retrieve the inner HTML of an element after ensuring it is visible.

        Args:
            selector (str): Selector of the element.
            timeout (float, optional): Maximum wait time (ms) for the element
                to become visible. Defaults to Playwright's timeout.

        Returns:
            str: The element's inner HTML content.

        Raises:
            playwright.async_api.TimeoutError: If the element does not become
                visible within the specified timeout.
        """
        logger.debug(f"Getting inner HTML from element: {selector}")

        locator = self.page.locator(selector)
        await locator.wait_for(state="visible", timeout=timeout)
        html = await locator.inner_html()

        logger.debug(f"Inner HTML from element {selector}: {html!r}")
        return html