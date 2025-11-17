import logging
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from utils.exceptions import (
    ElementNotFoundError, 
    ValidationError,
    ConfigurationError,
)

logger = logging.getLogger(__name__)

class MouseMixin:
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

    async def double_click(self, selector: str, timeout: int = 30000) -> None:
        """
        Double-clicks an element.

        Args:
            selector (str): Selector for the element to double-click.
            timeout (int): Timeout in milliseconds. Defaults to 30000.

        Raises:
            ElementNotFoundError: If element is not found within timeout.
        """
        try:
            await self.page.locator(selector).dblclick()
        except PlaywrightTimeoutError as e:
            raise ElementNotFoundError(selector, timeout=timeout) from e

    async def right_click(self, selector: str, timeout: int = 30000) -> None:
        """
        Right-clicks an element to open context menu.

        Args:
            selector (str): Selector for the element to right-click.
            timeout (int): Timeout in milliseconds. Defaults to 30000.

        Raises:
            ElementNotFoundError: If element is not found within timeout.
        """
        try:
            await self.page.locator(selector).click(button="right")
        except PlaywrightTimeoutError as e:
            raise ElementNotFoundError(selector, timeout=timeout) from e

    async def hover(self, selector: str, timeout: int = 30000) -> None:
        """
        Hovers over an element.

        Args:
            selector (str): Selector for the element to hover over.
            timeout (int): Timeout in milliseconds. Defaults to 30000.

        Raises:
            ElementNotFoundError: If element is not found within timeout.
        """
        try:
            await self.page.locator(selector).hover()
        except PlaywrightTimeoutError as e:
            raise ElementNotFoundError(selector, timeout=timeout) from e

    async def drag_and_drop(self, source_selector: str, target_selector: str) -> None:
        """
        Drags element from source to target.

        Args:
            source_selector (str): Selector for the element to drag.
            target_selector (str): Selector for the target drop zone.

        Raises:
            ValidationError: If drag and drop operation fails.

        Example:
            await self.drag_and_drop('.draggable-item', '.drop-zone')
        """
        try:
            source = self.page.locator(source_selector)
            target = self.page.locator(target_selector)
            await source.drag_to(target)
        except Exception as e:
            raise ValidationError(
                field=f"{source_selector} -> {target_selector}",
                message=f"Drag and drop operation failed: {str(e)}"
            ) from e