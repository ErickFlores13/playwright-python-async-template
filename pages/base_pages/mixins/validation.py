import logging
from playwright.async_api import Page, expect, TimeoutError as PlaywrightTimeoutError
from typing import Literal
from utils.exceptions import (
    ElementNotFoundError, 
    ValidationError,
    ConfigurationError,
)

logger = logging.getLogger(__name__)

class ValidationMixin:
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

    async def validate_edit_view_item_information(self, data_validate: dict) -> None:
        """
        Validates the values of fields in the edit view against the expected data.

        This method iterates over a dictionary of expected values, comparing them with the
        actual values displayed in the form fields of the edit view. Supports various field types
        including text inputs, checkboxes, radio buttons, selects, and complex structures like lists or sets.

        Args:
            data_validate (dict): A dictionary where keys are field selectors and values are the
                                expected values for validation. Values can be:
                                    - str, int, float: for text or number fields
                                    - bool: for checkboxes or radio buttons
                                    - list: for multiple expected values in inputs or nested structures
                                    - set: for verifying visible options in Select2 elements

        Behavior:
            1. Iterates through each field in `data_validate`.
            2. Retrieves the actual value from the page.
            3. Compares actual vs expected:
                - `<SELECT>`: checks that the selected option matches expected.
                - `<INPUT>`:
                    - Checkbox/Radio: validates checked state.
                    - Number/Text: validates value (supports list of expected values).
                - `<SPAN>` with set: checks visibility of each option (useful for Select2).
                - Nested lists: recursively validates each nested item.
            4. Raises an assertion error if any field does not match the expected value.

        Notes:
            - Assumes the user is already on the edit view of the record.
            - Ensure the field selectors in `data_validate` match the actual DOM elements.
            - Useful for validating both simple and complex form structures.

        Example:
            data_validate = {
                'input[name="title"]': 'Test Title',
                'input[name="year"]': '2023',
                'input[name="is_active"]': True,
                'select[name="genre"]': 'Action',
                'span.select2-results': {'Option1', 'Option2'}
            }

            await validate_edit_view_item_information(data_validate)
        """
        for field_name, expected_value in data_validate.items():
            field_input = self.page.locator(field_name)
            tag_name = await field_input.evaluate('el => el.tagName')
            
            if tag_name == 'SELECT':
                await expect(field_input).to_contain_text(expected_value)
            
            elif tag_name == 'INPUT':
                input_type = await field_input.evaluate('el => el.type')
                
                if input_type == 'checkbox':
                    if expected_value:
                        await expect(field_input).to_be_checked()
                    else:
                        await expect(field_input).not_to_be_checked()
                elif input_type == 'radio':
                    if expected_value:
                        await expect(field_input).to_be_checked()
                    else:
                        await expect(field_input).not_to_be_checked()
                elif input_type == 'number':
                    actual_value = await field_input.input_value()
                    assert float(actual_value) == float(expected_value), f"Expected '{expected_value}', but got '{actual_value}'"
                else:
                    if isinstance(expected_value, list):
                        for value in expected_value:
                            await expect(field_input).to_have_value(value)
                    else:
                        await expect(field_input).to_have_value(expected_value)

            elif tag_name == 'SPAN' and isinstance(expected_value, set):
                for option in expected_value:
                    option_locator = self.page.locator(f'.select2-results__option:has-text("{option}")')
                    await expect(option_locator).to_be_visible()

            elif isinstance(expected_value, list):
                for fila_data in expected_value:
                    await self.validate_edit_view_item_information(fila_data)

    async def validate_record_information_in_details_view(self, data_validate: dict) -> None:
        """
        Validates the displayed values of a record in the details view page against expected data.

        This method iterates over a dictionary of expected values, comparing them with the actual
        values displayed on the details view page. Supports multiple field types including text,
        numeric values, checkboxes, and nested structures like sets or dicts for complex fields (e.g., Select2).

        Args:
            data_validate (dict): A dictionary where keys are field selectors and values are the expected values.
                                Supported value types:
                                    - str, int, float: for single value fields.
                                    - bool: for checkbox fields.
                                    - set: for verifying multiple visible options.
                                    - dict: for nested structures, such as Select2 with multiple sub-values.

        Behavior:
            1. Iterates through each field in `data_validate`.
            2. Retrieves the current value(s) from the page using the appropriate locator(s):
                - Checks text-based elements: `label`, `td`, `p`, `th`, `li`.
                - Checks checkboxes for expected checked state.
                - Handles nested dicts or multiple expected values.
            3. Raises an assertion error if any actual value does not match the expected value.

        Notes:
            - Assumes the user is already on the details view page of the record.
            - Ensure that field selectors in `data_validate` correspond exactly to elements in the DOM.
            - Useful for validating both simple and complex details views.

        Example:
            data_validate = {
                'label[name="title"]': 'Test Title',
                'td[name="year"]': '2023',
                'p[name="status"]': {'Active', 'Pending'},
                'input[name="is_active"]': True,
                'select[name="genre"]': {'Action', 'Drama'}
            }

            await validate_record_information_in_details_view(data_validate)
        """
        async def _validate_text(value: str):
            """Reusable internal function to validate text in different elements."""
            label = self.page.locator('label', has_text=value).first
            td = self.page.locator('td', has_text=value).first
            p = self.page.locator('p', has_text=value).first
            th = self.page.locator('th', has_text=value).first
            li = self.page.locator('li', has_text=value).first

            final_locator = label.or_(td).or_(p).or_(th).or_(li)
            locator_count = await final_locator.count()

            if locator_count > 1:
                for i in range(locator_count):
                    await expect(final_locator.nth(i)).to_contain_text(value)
            else:
                await expect(final_locator.first).to_contain_text(value)

        # Iterate over all fields to validate
        for field_selector, expected_value in data_validate.items():

            # Case 1: multiple values (set)
            if isinstance(expected_value, set):
                for value in expected_value:
                    await _validate_text(value)

            # Case 2: nested dict (e.g. select2 fields)
            elif isinstance(expected_value, dict):
                for sub_selector, sub_values in expected_value.items():
                    values = sub_values if isinstance(sub_values, list) else [sub_values]
                    for value in values:
                        await _validate_text(value)

            # Case 3: boolean (checkbox)
            elif isinstance(expected_value, bool):
                checkbox = self.page.locator(field_selector)
                if expected_value:
                    await expect(checkbox).to_be_checked()
                else:
                    await expect(checkbox).not_to_be_checked()

            # Case 4: single string or numeric value
            elif expected_value:
                await _validate_text(str(expected_value))

    async def validate_item_toggle(self, toggle_selector: str, validation_type: Literal["enabled", "disabled"]) -> None:
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

    async def check_message(self, message: str, 
                            message_selector: str, 
                            continue_button_selector: str = None) -> None:
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