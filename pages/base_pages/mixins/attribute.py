import logging
from utils.exceptions import ValidationError
from typing import Literal, get_args
from playwright.async_api import Page

logger = logging.getLogger(__name__)

class AttributeMixin:
    """
    Mixin for manipulating HTML element attributes in Playwright tests.
    """

    page: Page

    AttributeType = Literal[
    "required",
    "maxlength",
    "minlength",
    "max",
    "min",
    "accept",
    "type",
    "pattern",
    "disabled"
    ]

    VALID_ATTRIBUTES = set(get_args(AttributeType))

    def _validate_attribute(self, attribute: str):
        if attribute not in self.VALID_ATTRIBUTES:
            raise ValidationError(
                field=attribute,
                message=f"Invalid attribute '{attribute}'. Valid attributes are: {', '.join(self.VALID_ATTRIBUTES)}"
            )

    async def remove_attribute(self, selector: str, attribute: AttributeType, timeout: float = None) -> None:
        """
        Remove an attribute from an element after ensuring it is visible.

        Args:
            selector (str): Selector of the target element.
            attribute (str): The attribute to remove. Common valid values include:
            - "required"
            - "maxlength"
            - "minlength"
            - "max"
            - "min"
            - "accept"
            - "type"
            - "pattern"
            - "disabled"
            timeout (float, optional): Maximum time to wait for the element to be visible.

        Returns:
            None
        
        Raises:
            playwright.async_api.TimeoutError: If the element does not become visible within the timeout.
        
        Example:
            await self.remove_attribute("#email", "required")
        """
        self._validate_attribute(attribute)
        
        logger.debug(f"Removing attribute '{attribute}' from element: {selector}")
        locator = self.page.locator(selector)
        await locator.wait_for(state="visible", timeout=timeout)
        await locator.evaluate(f"el => el.removeAttribute('{attribute}')")
        logger.debug(f"Successfully removed attribute '{attribute}' from element: {selector}")

    async def set_attribute(self, selector: str, attribute: AttributeType, value: str, timeout: float = None) -> None:
        """
        Set an attribute on an element after ensuring it is visible.

        Args:
            selector (str): Selector of the target element.
            attribute (str): The attribute to set. Common valid values include:
            - "required"
            - "maxlength"
            - "minlength"
            - "max"
            - "min"
            - "accept"
            - "type"
            - "pattern"
            - "disabled"
            value (str): The value to set for the attribute.
            timeout (float, optional): Maximum time to wait for the element to be visible.

        Returns:
            None
        """
        self._validate_attribute(attribute)

        logger.debug(f"Setting attribute '{attribute}' to '{value}' on element: {selector}")
        locator = self.page.locator(selector)
        await locator.wait_for(state="visible", timeout=timeout)
        await locator.evaluate(f"el => el.setAttribute('{attribute}', '{value}')")
        logger.debug(f"Successfully set attribute '{attribute}' to '{value}' on element: {selector}")