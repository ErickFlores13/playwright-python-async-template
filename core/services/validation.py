import logging
from playwright.async_api import Page, expect
from typing import Literal
from core.utils.exceptions import ConfigurationError

logger = logging.getLogger(__name__)

class Validation:
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
            
            logger.debug(f"[Validation] Validating container {container_selector} contains value '{expected_value}'")

            if isinstance(expected_value, bool):
                checkbox = container.locator('input[type="checkbox"]')
                logger.debug(f"[Validation] Validating checkbox in {container_selector} is {'checked' if expected_value else 'unchecked'}")
                if expected_value:
                    await expect(checkbox).to_be_checked()
                else:
                    await expect(checkbox).not_to_be_checked()
            
            elif isinstance(expected_value, list):
                logger.debug(f"[Validation] Validating container {container_selector} contains multiple values {expected_value}")
                for value in expected_value:
                    await expect(container).to_contain_text(str(value))
            
            else:
                await expect(container).to_contain_text(str(expected_value))

    async def validate_item_toggle(
            self, 
            toggle_selector: str, 
            validation_type: Literal["enabled", "disabled"]
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
            logger.debug(f"[Validation] Validating toggle {toggle_selector} is disabled (unchecked)")
            await expect(self.page.locator(toggle_selector)).not_to_be_checked()

    async def validate_message(
            self, 
            selector: str, 
            expected_text: str, 
            exact: bool = False):
        """Validate a message contains or matches expected text.
        
        Args:
            selector: CSS selector for the message element
            expected_text: Expected text in the message
            exact: If True, requires exact match. If False, partial match (contains)
        """
        message = self.page.locator(selector)
        if exact:
            logger.debug(f"[Validation] Validating message {selector} exactly matches text '{expected_text}'")
            await expect(message).to_have_text(expected_text)
        else:
            logger.debug(f"[Validation] Validating message {selector} contains text '{expected_text}'")
            await expect(message).to_contain_text(expected_text)