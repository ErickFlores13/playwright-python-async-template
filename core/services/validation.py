import logging
from playwright.async_api import Page, expect, TimeoutError as PlaywrightTimeoutError
from typing import Literal
from core.utils.exceptions import (
    ElementNotFoundError, 
    ValidationError,
    ConfigurationError,
)

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
            
            if isinstance(expected_value, bool):
                checkbox = container.locator('input[type="checkbox"]')
                if expected_value:
                    await expect(checkbox).to_be_checked()
                else:
                    await expect(checkbox).not_to_be_checked()
            
            elif isinstance(expected_value, list):
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
            await expect(self.page.locator(toggle_selector)).to_be_checked()
        elif validation_type == "disabled":
            await expect(self.page.locator(toggle_selector)).not_to_be_checked()

    async def check_message(
            self, 
            message: str, 
            message_selector: str, 
            continue_button_selector: str = None
            ) -> None:
        """
        Verifies that a message appears on the page and clicks the continue button if visible.

        Args:
            message (str): The expected message text.
            message_selector (str): Selector for the element containing the message.
            continue_button_selector (str, optional): Selector for the continue button.

        Raises:
            ElementNotFoundError: if message element or continue button is not found.
            ValidationError: if message text doesn't match expected.

        Example:
            await check_message("Operation completed successfully!", 
                               ".alert-message", 
                               "button.continue")

        Notes:
            - If continue_button_selector is provided and the button is visible, it will be clicked.
        """
        try:
            message_element = self.page.locator(message_selector)
            await message_element.wait_for(state="visible", timeout=5000)
            await expect(message_element).to_contain_text(message)

            if continue_button_selector:
                try:
                    continue_button = self.page.locator(continue_button_selector)
                    await continue_button.wait_for(state="visible", timeout=5000)
                    await self.page.click(continue_button_selector)
                except PlaywrightTimeoutError as e:
                    raise ElementNotFoundError(continue_button_selector, timeout=5000) from e

        except PlaywrightTimeoutError as e:
            raise ElementNotFoundError(message_selector, timeout=5000) from e          
        except AssertionError as e:
            raise ValidationError(
                field=message_selector,
                message=f"Expected message '{message}' not found in element"
            ) from e
        except Exception as e:
            raise ValidationError(
                field=message_selector,
                message=f"Unexpected error during message validation: {str(e)}"
            ) from e