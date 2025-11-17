import logging
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from utils.exceptions import (
    ElementNotFoundError, 
    ConfigurationError,
)

logger = logging.getLogger(__name__)

class ContentMixin:
    """
    Generic base page with overridable playwright methods that allow a custom-made test automation.
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

        Notes:
            - Waits for the element to be visible before retrieving the text.
        """
        try:
            await self.page.wait_for_selector(selector)
            element = self.page.locator(selector)
            
            if not await element.is_visible():
                raise ElementNotFoundError(selector, timeout=5000)
                
            return await element.inner_text()
        except PlaywrightTimeoutError as e:
            raise ElementNotFoundError(selector) from e
        except Exception as e:
            raise RuntimeError(f"Error while getting text for selector '{selector}': {e}") from e

    async def scroll_into_view(self, selector: str) -> None:
        """
        Scrolls the specified element into view.

        Args:
            selector (str): Selector of the element to scroll into view.

        Raises:
            ElementNotFoundError: if element is not found.

        Notes:
            - Ensures the element is visible in the viewport for interactions.
        """
        try:
            await self.page.wait_for_selector(selector)
            element = self.page.locator(selector)
            await element.scroll_into_view_if_needed()
        except PlaywrightTimeoutError as e:
            raise ElementNotFoundError(selector) from e
        except Exception as e:
            raise RuntimeError(f"Error while scrolling into view for selector '{selector}': {e}") from e