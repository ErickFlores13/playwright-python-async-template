import logging
from playwright.async_api import Page, Locator, TimeoutError as PlaywrightTimeoutError
from typing import Literal, Union
from utils.exceptions import (
    ElementNotFoundError, 
    Select2Error, 
    ValidationError,
    ConfigurationError,
)

logger = logging.getLogger(__name__)

class FormFillingMixin:
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

    # ============================================================================
    # FORM FILLING & DATA INPUT
    # ============================================================================

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
        if not isinstance(data, dict):
            raise TypeError(f"fill_data expects a dict, got {type(data).__name__}")
        
        for selector, value in data.items():
            try:
                field_input = self.page.locator(selector)
                
                # Check if element exists and is visible
                if not await field_input.is_visible():
                    raise ElementNotFoundError(selector, timeout=5000)
                
                tag_name = await field_input.evaluate('el => el.tagName')
                input_type = await field_input.evaluate('el => el.type')
                idselect2 = None
                if self.use_select2:
                    idselect2 = await field_input.evaluate('el => el.getAttribute("data-select2-id")')      

                if input_type == 'file':
                    if not isinstance(value, (str, list)):
                        raise ValidationError(selector, f"File input expects string or list, got {type(value).__name__}")
                    await field_input.set_input_files(value)

                elif input_type == 'radio':
                    if await field_input.evaluate('el => el.value') == value:
                        await field_input.check()

                elif input_type == 'checkbox':
                    if not isinstance(value, bool):
                        raise ValidationError(selector, f"Checkbox expects boolean, got {type(value).__name__}")
                    if value:  
                        try:
                            await field_input.check()
                        except Exception as e:
                            raise ValidationError(selector, f"Failed to check checkbox: {str(e)}") from e
                    else:
                        try:
                            await field_input.uncheck()
                        except Exception as e:
                            raise ValidationError(selector, f"Failed to uncheck checkbox: {str(e)}") from e

                elif input_type == 'button':
                    await self._handle_button(field_input, value, selector)

                elif tag_name == 'SELECT' and (not self.use_select2 or not idselect2):
                    # Use native select handling if Select2 is disabled OR if no Select2 ID is found
                    await self._handle_select(field_input, value, selector)

                elif tag_name == 'INPUT' or tag_name == 'TEXTAREA' or input_type == 'datetime-local' or input_type == 'date' or input_type == 'time':
                    if not isinstance(value, (str, int, float)):
                        raise ValidationError(selector, f"Input field expects string, int, or float, got {type(value).__name__}")
                    await field_input.fill(str(value))

                elif self.use_select2:
                    # Only try Select2 handling if explicitly enabled
                    await self._handle_select2(field_input, value, selector)
                
                else:
                    # Fallback to native select for any remaining select elements
                    if tag_name == 'SELECT':
                        await self._handle_select(field_input, value, selector)
                    else:
                        # For any other element type, try to fill as text
                        if not isinstance(value, (str, int, float)):
                            raise ValidationError(selector, f"Field expects string, int, or float, got {type(value).__name__}")
                        await field_input.fill(str(value))
                        
            except (ElementNotFoundError, ValidationError, Select2Error):
                raise
            except Exception as e:
                raise ValidationError(selector, f"Unexpected error: {str(e)}") from e

    async def _handle_button(self, field_input: Locator, value: Union[list, str], selector: str) -> None:
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
            for data in value:
                row_exists = False
                for selector_key, selector_value in data.items():
                    row_locator = self.page.locator(selector_key)

                    if await row_locator.is_visible():
                        row_exists = True
                        break
                
                if not row_exists:
                    try:
                        await field_input.click()
                    except PlaywrightTimeoutError as e:
                        raise ElementNotFoundError(selector_key, timeout=5000) from e
                    except Exception as e:
                        raise ValidationError(selector, f"Unexpected error: {str(e)}") from e

                await self.fill_data(data)
        else:
            try:
                await field_input.click()
            except PlaywrightTimeoutError as e:
                raise ElementNotFoundError(selector, timeout=5000) from e
            except Exception as e:
                raise ValidationError(selector, f"Unexpected error: {str(e)}") from e

    async def _handle_select(self, field_input: Locator, value: str, selector: str) -> None:
        """
        Selects an option in a native <select> element based on visible text.

        Args:
            field_input (Locator): Playwright locator for the select element.
            value (str): Text of the option to select.

        Raises:
            ElementNotFoundError: if no matching option is found.
            ValidationError: if the select element is not valid or accessible.
        """
        logger.info(f'Selecting option "{value}" on selector {selector}')

        try:
            await self.wait_for_page_load()

            # Validate visibility
            logger.debug(f"Checking visibility for {selector}")
            if not await field_input.is_visible():
                logger.warning(f"Select element {selector} is not visible")
                raise ElementNotFoundError(selector, timeout=5000)

            # Extract option value
            new_value = await field_input.evaluate(
                """(select, val) => {
                    const option = Array.from(select.options).find(o => o.textContent.includes(val));
                    return option ? option.value : null;
                }""",
                value
            )

            logger.debug(f'Computed select option value for "{value}" = {new_value}')

            if new_value is not None:
                try:
                    await field_input.select_option(new_value)
                    logger.info(f'Successfully selected "{value}" on {selector}')
                except PlaywrightTimeoutError as e:
                    raise ElementNotFoundError(selector, timeout=5000) from e
                except Exception as e:
                    raise ValidationError(selector, f"Failed to select option: {str(e)}") from e
            else:
                logger.warning(f'No option containing "{value}" found on {selector}')
                raise ValidationError(
                    message=f'No option containing "{value}" found in select element {selector}'
                )

        except PlaywrightTimeoutError as e:
            raise ElementNotFoundError(selector, timeout=5000) from e

        except Exception as e:
            logger.error(f"Unexpected error in handle_select: {e}")
            if not isinstance(e, (ElementNotFoundError, ValidationError)):
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
            raise Select2Error(
                selector=selector,
                operation="select2_handling",
                message=f"Unexpected error during Select2 handling: {str(e)}"
            ) from e
    
    # ============================================================================
    # FORM EDITING & UPDATES
    # ============================================================================
            
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

    # ============================================================================
    # TOGGLE & SWITCH HANDLING
    # ============================================================================

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