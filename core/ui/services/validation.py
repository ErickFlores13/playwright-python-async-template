import logging
from typing import Literal, Union

from playwright.async_api import Page, expect

from core.utils.exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class Validation:
    """
    Service for domain-specific validation and assertions.

    This service provides high-level validation methods for business logic.
    For simple element state checks, use Playwright's expect() directly:
    - await expect(page.locator(selector)).to_be_visible()
    - await expect(page.locator(selector)).to_be_checked()
    - await expect(page.locator(selector)).to_have_value(value)
    """

    def __init__(self, page: Page) -> None:
        if not page:
            raise ConfigurationError(
                config_key="page", message="Page instance cannot be None or empty"
            )

        self.page = page

    # ========== Generic Assertions (moved from ElementState) ==========

    async def assert_visible(self, selector: Union[str], timeout: float = 30000) -> None:
        """
        Assert that an element is visible.

        Args:
            selector: CSS selector for the element
            timeout: Maximum wait time in milliseconds
        """
        logger.debug(f"[Validation] Asserting element is visible: {selector}")
        await expect(self.page.locator(selector)).to_be_visible(timeout=timeout)

    async def assert_not_visible(self, selector: Union[str], timeout: float = 30000) -> None:
        """
        Assert that an element is not visible.

        Args:
            selector: CSS selector for the element
            timeout: Maximum wait time in milliseconds
        """
        logger.debug(f"[Validation] Asserting element is not visible: {selector}")
        await expect(self.page.locator(selector)).not_to_be_visible(timeout=timeout)

    async def assert_checked(self, selector: Union[str], timeout: float = 30000) -> None:
        """
        Assert that a checkbox or radio button is checked.

        Args:
            selector: CSS selector for the checkbox/radio
            timeout: Maximum wait time in milliseconds
        """
        logger.debug(f"[Validation] Asserting element is checked: {selector}")
        await expect(self.page.locator(selector)).to_be_checked(timeout=timeout)

    async def assert_not_checked(self, selector: Union[str], timeout: float = 30000) -> None:
        """
        Assert that a checkbox or radio button is not checked.

        Args:
            selector: CSS selector for the checkbox/radio
            timeout: Maximum wait time in milliseconds
        """
        logger.debug(f"[Validation] Asserting element is not checked: {selector}")
        await expect(self.page.locator(selector)).not_to_be_checked(timeout=timeout)

    async def assert_value(
        self, selector: Union[str], expected_value: str, timeout: float = 30000
    ) -> None:
        """
        Assert that an input element has the expected value.

        Args:
            selector: CSS selector for the input element
            expected_value: Expected value
            timeout: Maximum wait time in milliseconds
        """
        logger.debug(f"[Validation] Asserting element {selector} has value: {expected_value}")
        await expect(self.page.locator(selector)).to_have_value(
            str(expected_value), timeout=timeout
        )

    # ========== Domain-Specific Validations ==========

    async def validate_record_information_in_details_view(self, data_validate: dict) -> None:
        """
        Validates displayed values in detail view containers.

        Selectors MUST point to container elements (e.g., '#div_id_username').
        Validates that the container's text content contains the expected value.

        Args:
            data_validate: Dict mapping container selectors to expected values.

        Example:
            data_validate = {
                '#div_id_username': 'john_doe',       # ← Validates THIS container
                '#div_id_email': 'john@test.com',     # ← Validates THIS container
            }
        """
        for container_selector, expected_value in data_validate.items():
            container = self.page.locator(container_selector)

            logger.debug(
                f"[Validation] Validating container {container_selector} contains value '{expected_value}'"
            )

            if isinstance(expected_value, bool):
                checkbox = container.locator('input[type="checkbox"]')
                logger.debug(
                    f"[Validation] Validating checkbox in {container_selector} is {'checked' if expected_value else 'unchecked'}"
                )
                if expected_value:
                    await expect(checkbox).to_be_checked()
                else:
                    await expect(checkbox).not_to_be_checked()

            elif isinstance(expected_value, list):
                logger.debug(
                    f"[Validation] Validating container {container_selector} contains multiple values {expected_value}"
                )
                for value in expected_value:
                    await expect(container).to_contain_text(str(value))

            else:
                await expect(container).to_contain_text(str(expected_value))

    async def validate_item_toggle(
        self, toggle_selector: str, validation_type: Literal["enabled", "disabled"]
    ) -> None:
        """
        Validates whether a toggle (checkbox) is enabled or disabled.

        Args:
            toggle_selector (str): Selector for the toggle element.
            validation_type (str): "enabled" to check if toggle is checked, "disabled" to check if toggle is unchecked.
        """

        if validation_type == "enabled":
            logger.debug(f"[Validation] Validating toggle {toggle_selector} is enabled (checked)")
            await expect(self.page.locator(toggle_selector)).to_be_checked()
        elif validation_type == "disabled":
            logger.debug(
                f"[Validation] Validating toggle {toggle_selector} is disabled (unchecked)"
            )
            await expect(self.page.locator(toggle_selector)).not_to_be_checked()

    async def validate_message(self, selector: str, expected_text: str, exact: bool = False):
        """Validate a message contains or matches expected text.

        Args:
            selector: CSS selector for the message element
            expected_text: Expected text in the message
            exact: If True, requires exact match. If False, partial match (contains)
        """
        message = self.page.locator(selector)
        if exact:
            logger.debug(
                f"[Validation] Validating message {selector} exactly matches text '{expected_text}'"
            )
            await expect(message).to_have_text(expected_text)
        else:
            logger.debug(
                f"[Validation] Validating message {selector} contains text '{expected_text}'"
            )
            await expect(message).to_contain_text(expected_text)
