import logging
from playwright.async_api import expect, Page, Locator
from typing import Union
from core.utils.playwright_utils import resolve_locator
from core.utils.exceptions import ConfigurationError

logger = logging.getLogger(__name__)

class ElementState:
    """
    Service for verifying the state of web elements.
    Provides methods to check visibility, checked status, value presence, and hidden state.
    Designed to be used as part of a modular Page Object Model for test automation.
    """

    def __init__(self, page: Page):
        if not page:
            raise ConfigurationError(
                config_key="page",
                message="Page instance cannot be None or empty"
            )
        self.page = page

    async def is_visible(self, selector: Union[str, Locator], timeout: float = 30000) -> None:
        """
        Verifies that an element is visible on the page.

        Args:
            selector (Union[str, Locator]): Selector or Locator for the element.
            timeout (float, optional): Maximum time to wait for the element to be visible.

        Raises:
            playwright.async_api.TimeoutError: If the element does not become visible within the timeout.
        
        - Example:
            await self.is_visible("#submit-button", timeout=5000)
        """
        logger.debug(f"Checking visibility for element: {selector}")
        await expect(resolve_locator(self.page, selector)).to_be_visible(timeout=timeout)
        logger.debug(f"Element is visible: {selector}")

    async def is_not_visible(self, selector: Union[str, Locator], timeout: float = 30000) -> None:
        """
        Verifies that an element is not visible on the page.

        Args:
            selector (Union[str, Locator]): Selector or Locator for the element.
            timeout (float, optional): Maximum time to wait for the element to be not visible.
        
        Raises:
            playwright.async_api.TimeoutError: If the element does not become not visible within the timeout.
        
        - Example:
            await self.is_not_visible("#loading-spinner", timeout=5000)
        """
        logger.debug(f"Checking if element is not visible: {selector}")
        await expect(resolve_locator(self.page, selector)).not_to_be_visible(timeout=timeout)
        logger.debug(f"Element is not visible: {selector}")

    async def is_checked(self, selector: Union[str, Locator], timeout: float = 30000) -> None:
        """
        Verifies that a checkbox or radio button is checked.
        
        Args:
            selector (Union[str, Locator]): Selector or Locator for the checkbox or radio button.
            timeout (float, optional): Maximum time to wait for the element to be checked.

        Raises:
            playwright.async_api.TimeoutError: If the element does not become checked within the timeout.

        - Example:
            await self.is_checked("#agree-terms", timeout=5000)
        """
        logger.debug(f"Checking if element is checked: {selector}")
        await expect(resolve_locator(self.page, selector)).to_be_checked(timeout=timeout)
        logger.debug(f"Element is checked: {selector}")

    async def have_value(self, selector: Union[str, Locator], value: str, timeout: float = 30000) -> None:
        """
        Verifies that an input element has the expected value.
        
        Args:
            selector (Union[str, Locator]): Selector or Locator for the input element.
            value (str): Expected value of the input element.
            timeout (float, optional): Maximum time to wait for the element to have the expected value.

        Raises:
            playwright.async_api.TimeoutError: If the element does not have the expected value within the timeout.

        - Example:
            await self.have_value("#username", "test_user", timeout=5000)
        """
        logger.debug(f"Checking if element '{selector}' has value: '{value}'")
        await expect(resolve_locator(self.page, selector)).to_have_value(value, timeout=timeout)
        logger.debug(f"Element '{selector}' has the expected value: '{value}'")

    async def is_hidden(self, selector: Union[str, Locator], timeout: float = 30000) -> None:
        """
        Verifies that an element is hidden on the page.

        Args:
            selector (Union[str, Locator]): Selector or Locator for the element.
            timeout (float, optional): Maximum time to wait for the element to be hidden.

        Raises:
            playwright.async_api.TimeoutError: If the element does not become hidden within the timeout.

        - Example:
            await self.is_hidden("#popup-ad", timeout=5000)
        """
        logger.debug(f"Checking if element is hidden: {selector}")
        await expect(resolve_locator(self.page, selector)).to_be_hidden(timeout=timeout)   
        logger.debug(f"Element is hidden: {selector}")