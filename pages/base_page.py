import asyncio
import logging
from playwright.async_api import Page, expect, Locator, TimeoutError as PlaywrightTimeoutError
from typing import Literal, Union
from utils.exceptions import (
    ElementNotFoundError, 
    Select2Error, 
    ValidationError,
    ConfigurationError,
    DatabaseError,
    RedisError
)

logger = logging.getLogger(__name__)

class BasePage:
    """
    Generic base page with overridable playwright methods that allow a custom-made test automation.
    """

    def __init__(self, page: Page):
        if not page:
            raise ConfigurationError(
                config_key="page",
                message="Page instance cannot be None or empty"
            )
            
        self.page = page
        # Default Select2 configuration - override in subclasses as needed
        self.use_select2 = True  # Enable Select2 by default
        self.remove_options_selector = 'button[title="Remove all items"]'
        self.searcher_selector = '.select2-search__field'
        self.select2_indicator = 'data-select2-id'
        
        # Validate Select2 configuration
        self._validate_select2_config()

    def _validate_select2_config(self) -> None:
        """
        Validates Select2 configuration parameters.
        
        Raises:
            ConfigurationError: if Select2 configuration is invalid.
        """
        if self.use_select2:
            if not isinstance(self.remove_options_selector, str) or not self.remove_options_selector.strip():
                raise ConfigurationError(
                    config_key="remove_options_selector",
                    message="Select2 remove_options_selector must be a non-empty string"
                )
            
            if not isinstance(self.searcher_selector, str) or not self.searcher_selector.strip():
                raise ConfigurationError(
                    config_key="searcher_selector",
                    message="Select2 searcher_selector must be a non-empty string"
                )
            
            if not isinstance(self.select2_indicator, str) or not self.select2_indicator.strip():
                raise ConfigurationError(
                    config_key="select2_indicator",
                    message="Select2 select2_indicator must be a non-empty string"
                )

    async def fill_data(self, data: dict) -> None:
        """
        Populates form fields with provided data for creation, editing, or filtering.

        Args:
            data (dict): Dictionary where keys are field selectors and values are the values to fill in.

        Supported field types:
            - Text inputs, textareas, date/time inputs: fills the value.
            - Checkboxes: checks/unchecks based on boolean value.
            - Radio buttons: checks the option matching the value.
            - File inputs: uploads the specified file.
            - Buttons: handles single click or list of actions.
            - Select elements: selects the option matching the text.
            - Select2 elements: handles clicks, typing, and selecting options (if use_select2=True).

        Configuration:
            Select2 behavior is controlled by class attributes set during initialization.
            See __init__ method documentation for configuration examples.

        Raises:
            ElementNotFoundError: if field element is not found.
            ValidationError: if field validation fails.
            Select2Error: if Select2 operations fail.

        Notes:
            - Assumes the user is already on the form page.
            - Selectors in the data dictionary must match actual DOM elements.
            - If use_select2=False, all select elements are treated as native HTML selects.
        """
        for field_name, value in data.items():
            try:
                field_input = self.page.locator(field_name)
                
                # Check if element exists and is visible
                if not await field_input.is_visible():
                    raise ElementNotFoundError(field_name, timeout=5000)
                
                tag_name = await field_input.evaluate('el => el.tagName')
                input_type = await field_input.evaluate('el => el.type')
                idselect2 = None
                if self.use_select2:
                    idselect2 = await field_input.evaluate('el => el.getAttribute("data-select2-id")')      

                if input_type == 'file':
                    if not isinstance(value, (str, list)):
                        raise ValidationError(field_name, f"File input expects string or list, got {type(value).__name__}")
                    await field_input.set_input_files(value)

                elif input_type == 'radio':
                    if await field_input.evaluate('el => el.value') == value:
                        await field_input.check()

                elif input_type == 'checkbox':
                    if not isinstance(value, bool):
                        raise ValidationError(field_name, f"Checkbox expects boolean, got {type(value).__name__}")
                    if value:  
                        await field_input.check()
                    else:
                        await field_input.uncheck()

                elif input_type == 'button':
                    await self._handle_button(field_input, value)

                elif tag_name == 'SELECT' and (not self.use_select2 or not idselect2):
                    # Use native select handling if Select2 is disabled OR if no Select2 ID is found
                    await self._handle_select(field_input, value)

                elif tag_name == 'INPUT' or tag_name == 'TEXTAREA' or input_type == 'datetime-local' or input_type == 'date' or input_type == 'time':
                    if not isinstance(value, (str, int, float)):
                        raise ValidationError(field_name, f"Input field expects string, int, or float, got {type(value).__name__}")
                    await field_input.fill(str(value))

                elif self.use_select2:
                    # Only try Select2 handling if explicitly enabled
                    await self._handle_select2(field_input, value)
                
                else:
                    # Fallback to native select for any remaining select elements
                    if tag_name == 'SELECT':
                        await self._handle_select(field_input, value)
                    else:
                        # For any other element type, try to fill as text
                        if not isinstance(value, (str, int, float)):
                            raise ValidationError(field_name, f"Field expects string, int, or float, got {type(value).__name__}")
                        await field_input.fill(str(value))
                        
            except (ElementNotFoundError, ValidationError, Select2Error):
                raise
            except Exception as e:
                logger.error(f"Unexpected error filling field '{field_name}': {e}")
                raise ValidationError(field_name, f"Unexpected error: {str(e)}") from e

    async def _handle_button(self, field_input: Locator, value: Union[list, str]) -> None:
        """
        Handles clicking buttons during form filling.

        Args:
            field_input (Locator): Playwright locator of the button.
            value (str | list): 
                - str: simple click.
                - list: each item is a dict representing nested actions or rows to fill.

        Notes:
            - If the value is a list, checks if row already exists before clicking.
        """
        if isinstance(value, list):
            for fila_data in value:
                row_exists = False
                for selector_key, selector_value in fila_data.items():
                    row_locator = self.page.locator(selector_key)

                    if await row_locator.is_visible():
                        row_exists = True
                        break
                
                if not row_exists:
                    await field_input.click()
                
                await self.fill_data(fila_data)
        else:
            await field_input.click()
    
    async def _handle_select(self, field_input: Locator, value: str) -> None:
        """
        Selects an option in a native <select> element based on visible text.

        Args:
            field_input (Locator): Playwright locator for the select element.
            value (str): Text of the option to select.

        Raises:
            ElementNotFoundError: if no matching option is found.
            ValidationError: if the select element is not valid or accessible.
        """
        try:
            await self.page.wait_for_load_state('networkidle')
            
            # Validate that the select element exists and is visible
            if not await field_input.is_visible():
                selector = await field_input.evaluate('el => el.tagName + (el.id ? "#" + el.id : "") + (el.className ? "." + el.className.replace(/ /g, ".") : "")')
                raise ElementNotFoundError(selector, timeout=5000)
            
            new_value = await field_input.evaluate(
                """(select, val) => {
                    const option = Array.from(select.options).find(o => o.textContent.includes(val));
                    return option ? option.value : null;
                }""",
                value
            )

            if new_value is not None:
                await field_input.select_option(new_value)
            else:
                selector = await field_input.evaluate('el => el.tagName + (el.id ? "#" + el.id : "") + (el.className ? "." + el.className.replace(/ /g, ".") : "")')
                raise ValidationError(message=f'No option containing "{value}" found in select element {selector}')
                
        except PlaywrightTimeoutError as e:
            selector = await field_input.evaluate('el => el.tagName + (el.id ? "#" + el.id : "") + (el.className ? "." + el.className.replace(/ /g, ".") : "")')
            raise ElementNotFoundError(selector, timeout=5000) from e
        except Exception as e:
            if not isinstance(e, (ElementNotFoundError, ValidationError)):
                logger.error(f"Unexpected error in _handle_select: {e}")
                raise ValidationError(message=f"Failed to handle select element: {str(e)}") from e
            raise
        
    async def _handle_select2_options(self, input_value: str) -> None:
        """
        Handles selecting an individual option in a Select2 dropdown.

        Args:
            input_value (str): Option value to select. If empty string, clears the selection.

        Raises:
            Select2Error: if Select2 operations fail.
            ElementNotFoundError: if required Select2 elements are not found.

        Notes:
            - Uses class attributes for Select2 selectors.
            - Falls back to pressing Enter if option is not clickable.
        """
        try:
            if input_value == '':
                remove_value_locator = self.page.locator(self.remove_options_selector).first
                if await remove_value_locator.is_visible():
                    await self.page.click(self.remove_options_selector)
                else:
                    await self.page.keyboard.press('Escape')
            else:
                search_input = self.page.locator(self.searcher_selector).first
                
                # Validate that the search input exists
                if not await search_input.is_visible():
                    raise Select2Error(
                        selector=self.searcher_selector,
                        operation="search_input_visibility",
                        message="Select2 search input is not visible"
                    )
                
                await search_input.fill(input_value)
                option_locator = self.page.locator(f'.select2-results__option:has-text("{input_value}")').first
                
                try:
                    await option_locator.wait_for(timeout=10000)
                    if await option_locator.is_visible():
                        await option_locator.click()
                    else:
                        logger.warning(f"Select2 option '{input_value}' not visible, using keyboard fallback")
                        await self.page.wait_for_timeout(1000)
                        await self.page.keyboard.press('Enter')
                except PlaywrightTimeoutError:
                    raise Select2Error(
                        selector=f'.select2-results__option:has-text("{input_value}")',
                        operation="option_selection",
                        message=f"Option '{input_value}' not found in Select2 dropdown within timeout"
                    )
                    
        except Select2Error:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in _handle_select2_options: {e}")
            raise Select2Error(
                selector=self.searcher_selector,
                operation="option_handling",
                message=f"Unexpected error during Select2 option handling: {str(e)}"
            ) from e

    async def _handle_select2(self, field_input: Locator, value: Union[str, list, dict, set]) -> None:
        """
        Handles interaction with Select2 dropdowns.

        Args:
            field_input (Locator): Playwright locator of the Select2 field.
            value (str | list | set | dict): Value(s) to select. Supports nested dict for complex inputs.
            
        Raises:
            Select2Error: if Select2 operations fail.
            ElementNotFoundError: if Select2 element is not found.
            
        Notes:
            - Uses class attributes for Select2 selectors.
        """
        try:
            # Validate that the Select2 field exists and is clickable
            if not await field_input.is_visible():
                selector = await field_input.evaluate('el => el.tagName + (el.id ? "#" + el.id : "") + (el.className ? "." + el.className.replace(/ /g, ".") : "")')
                raise ElementNotFoundError(selector, timeout=5000)
            
            await field_input.click()

            if isinstance(value, dict):
                for selector_to_write, input_values in value.items():
                    input_values = input_values if isinstance(input_values, list) else [input_values]

                    for input_value in input_values:
                        if selector_to_write == self.remove_options_selector:
                            continue

                        try:
                            await self.page.locator(selector_to_write).fill(input_value)
                            await self._handle_select2_options(input_value)
                        except Exception as e:
                            raise Select2Error(
                                selector=selector_to_write,
                                operation="nested_fill",
                                message=f"Failed to fill nested Select2 field with value '{input_value}': {str(e)}"
                            ) from e

            elif isinstance(value, (set, list)):
                for input_value in value:
                    await self._handle_select2_options(input_value)

            else:
                await self._handle_select2_options(value)
                
        except (Select2Error, ElementNotFoundError):
            raise
        except Exception as e:
            selector = await field_input.evaluate('el => el.tagName + (el.id ? "#" + el.id : "") + (el.className ? "." + el.className.replace(/ /g, ".") : "")')
            logger.error(f"Unexpected error in _handle_select2: {e}")
            raise Select2Error(
                selector=selector,
                operation="select2_handling",
                message=f"Unexpected error during Select2 handling: {str(e)}"
            ) from e
            
    async def edit_item(self, new_data: dict) -> None:
        """
        Edits an existing item by clearing current values and filling in new data, then submits the form.

        Args:
            new_data (dict): Dictionary where keys are field selectors and values are the new data 
                            to input for each field.

        Example:
            await edit_item({
                'input[name="title"]': 'New Title',
                'select[name="genre"]': 'Drama'
            })

        Notes:
            - Always clears existing field values before populating new data.
            - Includes a 1-second wait between clearing and filling to ensure proper rendering.
        """
        # Always create empty dict to clear existing form data
        empty_dict = self._create_empty_dict(new_data)
        await self.fill_data(empty_dict)
        
        await self.page.wait_for_timeout(1000)
        await self.fill_data(new_data)

    def _create_empty_dict(self, original_dict: dict) -> dict:
        """
        Creates a dictionary structure matching the original, but with all values cleared.

        Args:
            original_dict (dict): Dictionary representing the fields to clear.

        Returns:
            dict: New dictionary with same keys, but values set to empty strings, empty lists, 
                or empty dicts recursively for nested structures.
                
        Notes:
            - Uses class attributes for Select2 configuration.
        """
        new_dict = {}

        for key, value in original_dict.items():
            if isinstance(value, dict):
                if self.select2_indicator in value:
                    new_dict[key] = {self.remove_options_selector: ""}
                else:
                    new_dict[key] = self._create_empty_dict(value)
            elif isinstance(value, list):
                new_dict[key] = []
            else:
                new_dict[key] = ''
        return new_dict

    async def handle_toggle_action(self, toggle_selector: str, action: Literal["enable", "disable"]) -> None:
        """
        Enables or disables an item by interacting with a toggle switch.

        Args:
            toggle_selector (str): Selector for the toggle switch element.
            action (Literal["enable", "disable"]): Specifies whether to enable or disable the item.
                - "enable": checks the toggle switch.
                - "disable": unchecks the toggle switch.

        Behavior:
            1. Waits for the toggle switch to be visible.
            2. Checks or unchecks the toggle switch based on the `action` argument.

        Notes:
            - Assumes that the toggle switch is present and interactable.
        
        Example:
            await handle_toggle_action('input[type="checkbox"]', "disable")
            await handle_toggle_action('input[type="checkbox"]', "enable")
        """
        if action == "enable":
            await self.page.check(toggle_selector)
        if action == "disable":
            await self.page.uncheck(toggle_selector)

        await self.page.wait_for_load_state("domcontentloaded")

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

    async def check_message(self, message: str, modal_message_selector: str, 
                           continue_button_selector: str = None) -> None:
        """
        Verifies that a message appears on the page and clicks the continue button if visible.

        Args:
            message (str): The expected message text.
            modal_message_selector (str): Selector for the element containing the message.
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
            # Check if modal message element exists
            modal_element = self.page.locator(modal_message_selector)
            if not await modal_element.is_visible():
                raise ElementNotFoundError(modal_message_selector, timeout=5000)
            
            await expect(modal_element).to_contain_text(message)

            if continue_button_selector:
                continue_button = self.page.locator(continue_button_selector)
                if await continue_button.is_visible():
                    await self.page.click(continue_button_selector)
                else:
                    logger.warning(f"Continue button '{continue_button_selector}' not visible, skipping click")
                    
        except PlaywrightTimeoutError as e:
            raise ElementNotFoundError(modal_message_selector, timeout=5000) from e
        except AssertionError as e:
            raise ValidationError(
                field=modal_message_selector,
                message=f"Expected message '{message}' not found in element"
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error in check_message: {e}")
            raise ValidationError(
                field=modal_message_selector,
                message=f"Unexpected error during message validation: {str(e)}"
            ) from e

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

    async def wait_for_selector(self, selector: str, time_sleep: float = 0.05, timeout: int = 30000) -> None:
        """
        Waits for an element to appear on the page.
        
        Args:
            selector (str): Element selector to wait for.
            time_sleep (float): Additional sleep time after element appears.
            timeout (int): Timeout in milliseconds.
            
        Raises:
            ElementNotFoundError: if element is not found within timeout.
        """
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            await asyncio.sleep(time_sleep)
        except PlaywrightTimeoutError as e:
            logger.error(f"Element not found: {selector}")
            raise ElementNotFoundError(selector, timeout=timeout) from e

    async def is_hidden(self, selector: str) -> None:
        """Verifies that an element is hidden on the page."""
        await expect(self.page.locator(selector)).to_be_hidden()   
                
    async def remove_required_attribute(self, selector: str) -> None:
        """Removes the 'required' attribute from the specified element."""
        await self.wait_for_selector(selector)
        await self.page.eval_on_selector(selector, "el => el.removeAttribute('required')")

    async def remove_max_length_attribute(self, selector: str) -> None:
        """Removes the 'maxlength' attribute from the specified element."""
        await self.wait_for_selector(selector)
        await self.page.eval_on_selector(selector, "el => el.removeAttribute('maxlength')")

    async def remove_min_length_attribute(self, selector: str) -> None:
        """Removes the 'minlength' attribute from the specified element."""
        await self.wait_for_selector(selector)
        await self.page.eval_on_selector(selector, "el => el.removeAttribute('minlength')")

    async def remove_max_attribute(self, selector: str) -> None:
        """Removes the 'max' attribute from the specified element."""
        await self.wait_for_selector(selector)
        await self.page.eval_on_selector(selector, "el => el.removeAttribute('max')")

    async def remove_min_attribute(self, selector: str) -> None:
        """Removes the 'min' attribute from the specified element."""
        await self.wait_for_selector(selector)
        await self.page.eval_on_selector(selector, "el => el.removeAttribute('min')")

    async def remove_accept_attribute(self, selector: str) -> None:
        """Removes the 'accept' attribute from the specified element."""
        await self.wait_for_selector(selector)
        await self.page.eval_on_selector(selector, "el => el.removeAttribute('accept')")

    async def remove_type_attribute(self, selector: str) -> None:
        """Removes the 'type' attribute from the specified element."""
        await self.wait_for_selector(selector)
        await self.page.eval_on_selector(selector, "el => el.removeAttribute('type')")

    async def remove_pattern_attribute(self, selector: str) -> None:
        """Removes the 'pattern' attribute from the specified element."""
        await self.wait_for_selector(selector)
        await self.page.eval_on_selector(selector, "el => el.removeAttribute('pattern')")

    async def remove_disabled_attribute(self, selector: str) -> None:
        """Removes the 'disabled' attribute from the specified element."""
        await self.wait_for_selector(selector)
        await self.page.eval_on_selector(selector, "el => el.removeAttribute('disabled')")

    async def change_type_attribute(self, selector: str) -> None:
        """
        Changes the 'type' attribute of the specified element to 'text'.

        Args:
            selector (str): Selector of the element whose 'type' attribute will be changed.
        """
        await self.wait_for_selector(selector)
        await self.page.eval_on_selector(selector, "el => el.setAttribute('type', 'text')")

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
            await self.wait_for_selector(selector)
            element = self.page.locator(selector)
            
            if not await element.is_visible():
                raise ElementNotFoundError(selector, timeout=5000)
                
            return await element.inner_text()
        except PlaywrightTimeoutError as e:
            raise ElementNotFoundError(selector, timeout=30000) from e
        except Exception as e:
            if not isinstance(e, ElementNotFoundError):
                logger.error(f"Unexpected error getting text from '{selector}': {e}")
                raise ElementNotFoundError(selector, timeout=5000) from e
            raise

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
            await self.wait_for_selector(selector)
            element = self.page.locator(selector)
            await element.scroll_into_view_if_needed()
        except Exception as e:
            if not isinstance(e, ElementNotFoundError):
                logger.error(f"Error scrolling element '{selector}' into view: {e}")
                raise ElementNotFoundError(selector, timeout=5000) from e
            raise

    async def execute_with_database_error_handling(self, operation_name: str, operation_func, *args, **kwargs):
        """
        Executes a database operation with proper error handling.
        
        Args:
            operation_name (str): Name of the database operation for error reporting.
            operation_func: Function to execute.
            *args: Arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.
            
        Raises:
            DatabaseError: if database operation fails.
            
        Returns:
            Result of the operation function.
        """
        try:
            return await operation_func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Database operation '{operation_name}' failed: {e}")
            raise DatabaseError(operation=operation_name, message=str(e)) from e

    async def execute_with_redis_error_handling(self, operation_name: str, operation_func, *args, **kwargs):
        """
        Executes a Redis operation with proper error handling.
        
        Args:
            operation_name (str): Name of the Redis operation for error reporting.
            operation_func: Function to execute.
            *args: Arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.
            
        Raises:
            RedisError: if Redis operation fails.
            
        Returns:
            Result of the operation function.
        """
        try:
            return await operation_func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Redis operation '{operation_name}' failed: {e}")
            raise RedisError(operation=operation_name, message=str(e)) from e

    async def take_screenshot(self, name: str = None) -> str:
        """
        Takes a screenshot of the current page.

        Args:
            name (str, optional): Custom name for the screenshot file.

        Returns:
            str: Path to the saved screenshot file.
        """
        from datetime import datetime
        import os
        
        if not name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"screenshot_{timestamp}"
        
        screenshots_dir = "screenshots"
        os.makedirs(screenshots_dir, exist_ok=True)
        
        screenshot_path = os.path.join(screenshots_dir, f"{name}.png")
        await self.page.screenshot(path=screenshot_path, full_page=True)
        
        logger.info(f"Screenshot saved: {screenshot_path}")
        return screenshot_path

    async def wait_for_page_load(self, timeout: int = 30000) -> None:
        """
        Waits for the page to fully load including network requests.

        Args:
            timeout (int): Timeout in milliseconds (default: 30000).
            
        Raises:
            ElementNotFoundError: if page doesn't load within timeout.
        """
        try:
            await self.page.wait_for_load_state("networkidle", timeout=timeout)
            await self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
            logger.info("Page loaded successfully")
        except PlaywrightTimeoutError as e:
            logger.error(f"Page load timeout: {e}")
            await self.take_screenshot("page_load_timeout")
            raise ElementNotFoundError("page", timeout=timeout) from e
        except Exception as e:
            logger.error(f"Unexpected page load error: {e}")
            await self.take_screenshot("page_load_error")
            raise ElementNotFoundError("page", timeout=timeout) from e

    async def highlight_element(self, selector: str, duration: int = 2000) -> None:
        """
        Highlights an element by adding a colored border (useful for debugging).

        Args:
            selector (str): Selector of the element to highlight.
            duration (int): Duration to keep the highlight in milliseconds.
        """
        await self.page.locator(selector).evaluate(
            """(element, duration) => {
                element.style.border = '3px solid red';
                element.style.backgroundColor = 'yellow';
                setTimeout(() => {
                    element.style.border = '';
                    element.style.backgroundColor = '';
                }, duration);
            }""",
            duration
        ) 

    async def double_click(self, selector: str, timeout: int = 30000) -> None:
        """Double-clicks an element."""
        try:
            await self.page.locator(selector).dblclick()
        except PlaywrightTimeoutError as e:
            raise ElementNotFoundError(selector, timeout=timeout) from e

    async def right_click(self, selector: str, timeout: int = 30000) -> None:
        """Right-clicks an element to open context menu."""
        try:
            await self.page.locator(selector).click(button="right")
        except PlaywrightTimeoutError as e:
            raise ElementNotFoundError(selector, timeout=timeout) from e

    async def hover(self, selector: str, timeout: int = 30000) -> None:
        """Hovers over an element."""
        try:
            await self.page.locator(selector).hover()
        except PlaywrightTimeoutError as e:
            raise ElementNotFoundError(selector, timeout=timeout) from e

    async def drag_and_drop(self, source_selector: str, target_selector: str) -> None:
        """Drags element from source to target."""
        try:
            source = self.page.locator(source_selector)
            target = self.page.locator(target_selector)
            await source.drag_to(target)
        except Exception as e:
            logger.error(f"Drag and drop failed: {e}")
            raise ValidationError(
                field=f"{source_selector} -> {target_selector}",
                message=f"Drag and drop operation failed: {str(e)}"
            ) from e
        
    async def switch_to_new_tab(self) -> None:
        """Switches to the newest opened tab."""
        try:
            # Wait for new page to open
            async with self.page.context.expect_page() as new_page_info:
                pass
            new_page = await new_page_info.value
            await new_page.wait_for_load_state()
            self.page = new_page
        except Exception as e:
            logger.error(f"Failed to switch to new tab: {e}")
            raise ValidationError("tab_switch", f"Tab switch failed: {str(e)}") from e

    async def close_current_tab(self) -> None:
        """Closes current tab and switches to previous one."""
        try:
            context = self.page.context
            pages = context.pages
            if len(pages) > 1:
                await self.page.close()
                self.page = pages[-2]  # Switch to previous tab
            else:
                logger.warning("Cannot close last remaining tab")
        except Exception as e:
            raise ValidationError("tab_close", f"Failed to close tab: {str(e)}") from e

    async def refresh_page(self) -> None:
        """Refreshes the current page."""
        try:
            await self.page.reload()
            await self.wait_for_page_load()
        except Exception as e:
            raise ValidationError("page_refresh", f"Page refresh failed: {str(e)}") from e

    async def go_back(self) -> None:
        """Navigates back in browser history."""
        try:
            await self.page.go_back()
            await self.wait_for_page_load()
        except Exception as e:
            raise ValidationError("navigation_back", f"Back navigation failed: {str(e)}") from e

    async def go_forward(self) -> None:
        """Navigates forward in browser history."""
        try:
            await self.page.go_forward()
            await self.wait_for_page_load()
        except Exception as e:
            raise ValidationError("navigation_forward", f"Forward navigation failed: {str(e)}") from e