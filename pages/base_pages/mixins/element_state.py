import asyncio
import logging
from playwright.async_api import Page, expect, TimeoutError as PlaywrightTimeoutError
from utils.exceptions import (
    ElementNotFoundError, 
    ValidationError,
    ConfigurationError,
)

logger = logging.getLogger(__name__)

class ElementStateMixin:
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
        
    async def is_visible(self, selector: str) -> None:
        """
        Verifies that an element is visible on the page.
        
        Raises:
            ElementNotFoundError: if element is not found.
            ValidationError: if element is not visible.
        """
        try:
            element = self.page.locator(selector)
            await expect(element).to_be_visible()
        except AssertionError as e:
            raise ValidationError(field=selector, message="Element is not visible") from e
        except Exception as e:
            raise ElementNotFoundError(selector, timeout=5000) from e

    async def is_not_visible(self, selector: str) -> None:
        """
        Verifies that an element is not visible on the page.
        
        Raises:
            ValidationError: if element is unexpectedly visible.
        """
        try:
            element = self.page.locator(selector)
            await expect(element).not_to_be_visible()
        except AssertionError as e:
            raise ValidationError(field=selector, message="Element is unexpectedly visible") from e

    async def is_checked(self, selector: str) -> None:
        """
        Verifies that a checkbox or radio button is checked.
        
        Raises:
            ElementNotFoundError: if element is not found.
            ValidationError: if element is not checked.
        """
        try:
            element = self.page.locator(selector)
            await expect(element).to_be_checked()
        except AssertionError as e:
            raise ValidationError(field=selector, message="Element is not checked") from e
        except Exception as e:
            raise ElementNotFoundError(selector, timeout=5000) from e

    async def have_value(self, selector: str, value: str) -> None:
        """
        Verifies that an input element has the expected value.
        
        Raises:
            ElementNotFoundError: if element is not found.
            ValidationError: if element value doesn't match expected.
        """
        try:
            element = self.page.locator(selector)
            await expect(element).to_have_value(value)
        except AssertionError as e:
            actual_value = await element.input_value()
            raise ValidationError(
                field=selector, 
                message=f"Expected value '{value}', but got '{actual_value}'"
            ) from e
        except Exception as e:
            raise ElementNotFoundError(selector, timeout=5000) from e

    async def is_hidden(self, selector: str) -> None:
        """
        Verifies that an element is hidden on the page.

        Args:
            selector (str): Selector for the element.

        Raises:
            ValidationError: If element is unexpectedly visible.
        """
        await expect(self.page.locator(selector)).to_be_hidden()   