import logging
from playwright.async_api import Page, Locator
from typing import Union
from utils.playwright_utils import resolve_locator

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

    page: Page

    async def get_text(self, selector: Union[str, Locator], timeout: float = 30000) -> str:
        """
        Retrieve the text content of an element after ensuring it is visible.

        Args:
            selector (Union[str, Locator]): Selector or Locator of the element.
            timeout (float, optional): Maximum wait time (ms) for the element
                to become visible. Defaults to Playwright's timeout.

        Returns:
            str: The element's text content.

        Raises:
            playwright.async_api.TimeoutError: If the element does not become
                visible within the specified timeout.

        Example:
            text = await page.get_text("#my-element", timeout=5000)
            text = await page.get_text(page.locator(".my-class"))
        """
        logger.debug(f"Attempting to get text from element: {selector}")

        locator = resolve_locator(self.page, selector)
        await locator.wait_for(state="visible", timeout=timeout)

        logger.debug(f"Successfully retrieved text from element: {selector}")
        return await locator.inner_text()
    

    async def get_attribute(self, selector: Union[str, Locator], attribute: str, timeout: float = 30000) -> str:
        """
        Retrieve the value of an attribute from an element after ensuring it is visible.

        Args:
            selector (Union[str, Locator]): Selector or Locator of the target element.
            attribute (str): Attribute name to retrieve.
            timeout (float, optional): Maximum wait time (ms) for the element
                to become visible. Defaults to Playwright's timeout.

        Returns:
            str | None: The attribute value, or None if the attribute does not exist.

        Raises:
            playwright.async_api.TimeoutError: If the element does not become
                visible within the specified timeout.

        Example:
            value = await page.get_attribute("#my-element", "href", timeout=5000)
            value = await page.get_attribute(page.locator(".my-class"), "data-value")
        """
        logger.debug(f"Getting attribute '{attribute}' from element: {selector}")

        locator = resolve_locator(self.page, selector)
        await locator.wait_for(state="visible", timeout=timeout)
        attribute_value = await locator.get_attribute(attribute)

        logger.debug(f"Successfully retrieved attribute '{attribute}' from element: {selector} (value: {attribute_value})")
        return attribute_value


    async def scroll_into_view(self, selector: Union[str, Locator], timeout: float = 30000) -> None:
        """
        Scroll the target element into view after ensuring it is visible.

        Args:
            selector (Union[str, Locator]): Selector or Locator of the element to scroll into view.
            timeout (float, optional): Maximum wait time (ms) for the element
                to become visible. Defaults to Playwright's timeout.

        Returns:
            None

        Raises:
            playwright.async_api.TimeoutError: If the element does not become
                visible within the specified timeout.

        Example:
            await page.scroll_into_view("#my-element", timeout=5000)
            await page.scroll_into_view(page.locator(".my-class"))
        """
        logger.debug(f"Attempting to scroll element into view: {selector}")

        locator = resolve_locator(self.page, selector)
        await locator.wait_for(state="visible", timeout=timeout)

        logger.debug(f"Successfully scrolled element into view: {selector}")
        await locator.scroll_into_view_if_needed()
        
    
    async def get_html(self, selector: Union[str, Locator], timeout: float = 30000) -> str:
        """
        Retrieve the inner HTML of an element after ensuring it is visible.

        Args:
            selector (Union[str, Locator]): Selector or Locator of the element.
            timeout (float, optional): Maximum wait time (ms) for the element
                to become visible. Defaults to Playwright's timeout.

        Returns:
            str: The element's inner HTML content.

        Raises:
            playwright.async_api.TimeoutError: If the element does not become
                visible within the specified timeout.

        Example:
            html = await page.get_html("#my-element", timeout=5000)
            html = await page.get_html(page.locator(".my-class"))
        """
        logger.debug(f"Getting inner HTML from element: {selector}")

        locator = resolve_locator(self.page, selector)
        await locator.wait_for(state="visible", timeout=timeout)
        html = await locator.inner_html()

        logger.debug(f"Inner HTML from element {selector}: {html!r}")
        return html