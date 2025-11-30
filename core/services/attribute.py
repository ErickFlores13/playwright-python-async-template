import logging
from typing import Literal, Union, get_args

from playwright.async_api import Locator, Page

from core.utils.exceptions import ConfigurationError, ValidationError
from core.utils.playwright_utils import resolve_locator

logger = logging.getLogger(__name__)


class Attribute:
    """
    Service for manipulating HTML attributes on elements.
    Provides methods to set and remove attributes after ensuring element visibility.
    """

    def __init__(self, page: Page):
        if not page:
            raise ConfigurationError(
                config_key="page", message="Page instance cannot be None or empty"
            )
        self.page = page

    AttributeType = Literal[
        # ===== VALIDATION ATTRIBUTES (Current) =====
        "required",
        "maxlength",
        "minlength",
        "max",
        "min",
        "pattern",
        "step",
        # ===== FORM STATE ATTRIBUTES (Current) =====
        "disabled",
        "readonly",
        "checked",
        "selected",
        "multiple",
        # ===== INPUT TYPE ATTRIBUTES (Current) =====
        "type",
        "accept",
        "value",
        # ===== FORM-LEVEL VALIDATION BYPASS (MISSING!) =====
        "novalidate",  # Disable entire form validation
        "formnovalidate",  # Per-button validation bypass
        # ===== FORM SECURITY ATTRIBUTES (MISSING!) =====
        "method",  # POST/GET tampering
        "action",  # Form endpoint tampering
        "formaction",  # Per-button endpoint override
        "form",  # Associate input with different form
        "name",  # Parameter name manipulation
        # ===== UI/UX ATTRIBUTES (MISSING!) =====
        "autocomplete",  # on/off for sensitive fields
        "inputmode",  # Keyboard type hints
        "placeholder",  # Misleading placeholders
        # ===== ARIA ATTRIBUTES (MISSING - Important for accessibility testing!) =====
        "aria-disabled",  # Visual vs functional disabled
        "aria-readonly",  # Visual vs functional readonly
        "aria-required",  # Visual vs functional required
        "aria-invalid",  # Validation state manipulation
    ]

    VALID_ATTRIBUTES = set(get_args(AttributeType))

    def _validate_attribute(self, attribute: str):
        """Validate if the provided attribute is in the list of valid attributes."""
        if attribute not in self.VALID_ATTRIBUTES:
            raise ValidationError(
                field=attribute,
                message=f"Invalid attribute '{attribute}'. Valid attributes are: {', '.join(self.VALID_ATTRIBUTES)}",
            )

    async def remove_attribute(
        self,
        selector: Union[str, Locator],
        attribute: AttributeType,
        timeout: float = 30000,
        wait_for_visibility: bool = True,
    ) -> None:
        """
        Remove an attribute from an element after ensuring it is visible.

        Args:
            selector (Union[str, Locator]): Selector or Locator of the target element.
            attribute (str): The attribute to remove. See AttributeType for full list.
                Includes validation attrs (required, pattern), form security (method, action),
                ARIA attributes (aria-disabled), and more.
            timeout (float, optional): Maximum time to wait for the element to be visible.
            wait_for_visibility (bool, optional): Whether to wait for the element to be visible before removing the attribute.

        Returns:
            None

        Raises:
            playwright.async_api.TimeoutError: If the element does not become visible within the timeout.

        Example:
            await self.remove_attribute("#email", "required")
        """
        self._validate_attribute(attribute)

        logger.debug(f"Removing attribute '{attribute}' from element: {selector}")
        locator = resolve_locator(self.page, selector)

        if wait_for_visibility:
            await locator.wait_for(state="visible", timeout=timeout)
        else:
            await locator.wait_for(state="attached", timeout=timeout)

        await locator.evaluate("(el, [attr]) => el.removeAttribute(attr)", [attribute])
        logger.debug(f"Successfully removed attribute '{attribute}' from element: {selector}")

    async def set_attribute(
        self,
        selector: Union[str, Locator],
        attribute: AttributeType,
        value: str,
        timeout: float = 30000,
        wait_for_visibility: bool = True,
    ) -> None:
        """
        Set an attribute on an element after ensuring it is visible.

        Args:
            selector (Union[str, Locator]): Selector or Locator of the target element.
            attribute (str): The attribute to remove. See AttributeType for full list.
                Includes validation attrs (required, pattern), form security (method, action),
                ARIA attributes (aria-disabled), and more.
            value (str): The value to set for the attribute.
            timeout (float, optional): Maximum time to wait for the element to be visible.
            wait_for_visibility (bool, optional): Whether to wait for the element to be visible before setting the attribute.

        Returns:
            None
        """
        self._validate_attribute(attribute)

        logger.debug(f"Setting attribute '{attribute}' to '{value}' on element: {selector}")
        locator = resolve_locator(self.page, selector)

        if wait_for_visibility:
            await locator.wait_for(state="visible", timeout=timeout)
        else:
            await locator.wait_for(state="attached", timeout=timeout)

        await locator.evaluate(
            "(el, [attr, val]) => el.setAttribute(attr, val)", [attribute, value]
        )
        logger.debug(
            f"Successfully set attribute '{attribute}' to '{value}' on element: {selector}"
        )
