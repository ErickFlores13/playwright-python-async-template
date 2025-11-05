import asyncio
from playwright.async_api import Page, expect, Locator
from typing import Literal, Union

class BasePage:
    """
    Generic base page with overridable playwright methods that allow a custom-made test automation.
    """

    def __init__(self, page: Page):
        """Inicializa la clase BasePage con una instancia de la página de Playwright.
        
        Args:
            page: Instancia de la página de Playwright.
        """
        self.page = page
        self.delete_button_selector = 'delete_button_selector'
        self.confirm_delete_button_selector = 'confirm_delete_button_selector'
        self.filter_button_selector = 'filter_button_selector'
        self.submit_button_selector = 'submit_button_selector'
        self.toggle_selector = 'toggle_selector'
        self.modal_message_selector = 'modal_selector'
        self.continue_button_selector = 'continue_selector'
        self.remove_options_select2 = 'button[title="Remove all items"]'
        self.searcher_select2_selector = 'searcher_select2_selector'
        self.select2_selector = 'select2_selector'

    async def fill_data(self, data: dict) -> None:
        """
        Populates form fields with provided data for creation, editing, or filtering.

        Args:
            data (dict): Dictionary where keys are field selectors and values are
                        the values to fill in.

        Supported field types:
            - Text inputs, textareas, date/time inputs: fills the value.
            - Checkboxes: checks/unchecks based on boolean value.
            - Radio buttons: checks the option matching the value.
            - File inputs: uploads the specified file.
            - Buttons: handles single click or list of actions.
            - Select elements: selects the option matching the text.
            - Select2 elements: handles clicks, typing, and selecting options.

        Example:
            await fill_data({
                'input[name="username"]': 'john_doe',
                'input[name="accept_terms"]': True,
                'select[name="country"]': 'USA',
                'input[type="file"]': 'path/to/file.txt'
            })
            
            **This fills in the username, checks the terms acceptance, selects a country, and uploads a file.**

        Notes:
            - Assumes the user is already on the form page.
            - Selectors in the data dictionary must match actual DOM elements.
        """
        for field_name, value in data.items():
            field_input = self.page.locator(field_name)
            tag_name = await field_input.evaluate('el => el.tagName')
            input_type = await field_input.evaluate('el => el.type')
            idselect2 = await field_input.evaluate('el => el.getAttribute("data-select2-id")')      

            if input_type == 'file':
                await field_input.set_input_files(value)

            elif input_type == 'radio':
                if await field_input.evaluate('el => el.value') == value:
                    await field_input.check()

            elif input_type == 'checkbox':
                if value:  
                    await field_input.check()
                else:
                    await field_input.uncheck()

            elif input_type == 'button':
                await self._handle_button(field_input, value)

            elif tag_name == 'SELECT' and not idselect2:
                await self._handle_select(field_input, value)

            elif tag_name == 'INPUT' or tag_name == 'TEXTAREA' or input_type == 'datetime-local' or input_type == 'date' or input_type == 'time':
                await field_input.fill(value)

            else:
                await self._handle_select2(field_input, value)
                
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
            Exception: if no matching option is found.
        """
        await self.page.wait_for_load_state('networkidle')
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
            raise Exception(f'No option containing {value} found')
        
    async def _handle_select2(self, field_input: Locator, value: Union[str, list, dict, set]):
        """
        Handles interaction with Select2 dropdowns.

        Args:
            field_input (Locator): Playwright locator of the Select2 field.
            value (str | list | set | dict): Value(s) to select. Supports nested dict for complex inputs.
        """
        await field_input.click()

        if isinstance(value, dict):
            for selector_to_write, input_values in value.items():
                # Asegurar que siempre sea lista
                input_values = input_values if isinstance(input_values, list) else [input_values]

                for input_value in input_values:
                    # Si es el selector especial, omitir esta iteración
                    if selector_to_write == self.remove_options_select2:
                        continue

                    # Resto de los casos: llenar y manejar
                    await self.page.locator(selector_to_write).fill(input_value)
                    await self._handle_select2_options(input_value)

        elif isinstance(value, (set, list)):
            for input_value in value:
                await self._handle_select2_options(input_value)

        else:
            await self._handle_select2_options(value)

    async def _handle_select2_options(self, input_value: str) -> None:
        """
        Handles selecting an individual option in a Select2 dropdown.

        Args:
            input_value (str): Option value to select. If empty string, clears the selection.

        Notes:
            - Waits for options to be visible.
            - Falls back to pressing Enter if option is not clickable.
        """
        if input_value == '':
            remove_value_locator = self.page.locator(self.remove_options_select2).first
            if await remove_value_locator.is_visible():
                await self.page.click(self.remove_options_select2)
            else:
                await self.page.keyboard.press('Escape')
        else:
            search_input = self.page.locator(self.searcher_select2_selector).first
            await search_input.fill(input_value)
            option_locator = self.page.locator(f'.select2-results__option:has-text("{input_value}")').first
            await option_locator.wait_for(timeout=10000)
            if await option_locator.is_visible():
                await option_locator.click()
            else:
                await self.page.wait_for_timeout(1000)
                await self.page.keyboard.press('Enter')

    async def search_with_filters(self, data_filters: dict) -> None:
        """
        Applies the specified filters and initiates a search by clicking the filter button.

        Args:
            data_filters (dict): Dictionary with filter field selectors as keys
                                and filter criteria as values.

        Example:
            await search_with_filters({
                'input[name="genre"]': 'Action',
                'input[name="year"]': '2023'
            })

        Notes:
            - Relies on `fill_data` to populate fields.
            - Expects `self.filter_button_selector` to point to the search/submit button.
        """
        await self.fill_data(data_filters)
        await self.page.click(self.filter_button_selector)
            
    async def edit_item(self, new_data: dict) -> None:
        """
        Edits an existing item by clearing current values and filling in new data, then submits the form.

        Args:
            new_data (dict): Dictionary where keys are field selectors and values are the new data 
                            to input for each field.

        Example:
            await edit_item({
                'input[name="title"]': 'New Title',
                'input[name="year"]': '2023',
                'select[name="genre"]': 'Drama'
            })

        Notes:
            - Clears existing field values before populating new data.
            - Includes a 1-second wait between clearing and filling to ensure proper rendering.
            - Expects `self.submit_button_selector` to point to the form's submit button.
            - Assumes all fields are visible and ready to interact with.
        """
        empty_dict = self._create_empty_dict(new_data)
        await self.fill_data(empty_dict)

        await self.page.wait_for_timeout(1000)
        await self.fill_data(new_data)

        await self.page.click(self.submit_button_selector)

    def _create_empty_dict(self, original_dict: dict) -> None:
        """
        Creates a dictionary structure matching the original, but with all values cleared.

        Args:
            original_dict (dict): Dictionary representing the fields to clear.

        Returns:
            dict: New dictionary with same keys, but values set to empty strings, empty lists, 
                or empty dicts recursively for nested structures.

        Notes:
            - Handles nested dictionaries and lists.
            - For select2 fields, sets the special key to remove existing options.
        """
        new_dict = {}

        for key, value in original_dict.items():
            if isinstance(value, dict):
                if self.select2_selector in value:
                    new_dict[key] = {self.remove_options_select2: ""}
                else:
                    new_dict[key] = self._create_empty_dict(value)
            elif isinstance(value, list):
                new_dict[key] = []
            else:
                new_dict[key] = ''
        return new_dict

    async def delete_item(self) -> None:
        """
        Deletes an item by clicking the delete button and confirming the action.

        This method performs the deletion workflow by interacting with the UI elements responsible 
        for removing an item, including any confirmation dialogs.

        Args:
            None (relies on `self.delete_button_selector` and `self.confirm_delete_button_selector` 
            being defined in the page object).

        Behavior:
            1. Clicks the delete button associated with the item.
            2. Clicks the confirmation button to finalize deletion.

        Notes:
            - Assumes that the delete button and confirmation button are visible and interactable.
            - Designed to work on the page where the item is currently displayed.
            - If there is a modal after the first click, it will handle it automatically.
        """
        # Wait for the delete button to be visible and click it
        await self.page.click(self.delete_button_selector)

        # If there is a modal after clicking the first button, handle with it
        confirm_selector = self.page.locator(self.confirm_delete_button_selector)
        if await confirm_selector.is_visible():
            await self.page.click(self.confirm_delete_button_selector)

        await self.page.wait_for_load_state("domcontentloaded")

    async def handle_toggle_action(self, action: Literal["enable", "disable"]) -> None:
        """
        Enables or disables an item by interacting with a toggle switch.

        This method handles a toggle switch on the page to set the item state according to the
        specified action.

        Args:
            action (Literal["enable", "disable"]): Specifies whether to enable or disable the item.
                - "enable": checks the toggle switch.
                - "disable": unchecks the toggle switch.

        Behavior:
            1. Waits for the toggle switch to be visible.
            2. Checks or unchecks the toggle switch based on the `action` argument.

        Notes:
            - Assumes that the toggle switch is present and interactable.
            - Designed to work with the toggle selector defined as `self.toggle_selector`.
            - Ensure the toggle switch is in the correct initial state if necessary.
        
        Example:
            await handle_toggle_action("disable")
            await handle_toggle_action("enable")
        """
        if action == "enable":
            await self.page.check(self.toggle_selector)
        if action == "disable":
            await self.page.uncheck(self.toggle_selector)

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

    async def validate_item_toggle(self, validation_type: Literal["enabled", "disabled"]) -> None:
        """
        Validates whether a toggle (checkbox) is enabled or disabled.

        Args:
            validation_type (str): "enabled" to check if toggle is checked, "disabled" to check if toggle is unchecked.

        Notes:
            Assumes `self.toggle_selector` points to the toggle element.
        """

        if validation_type == "enabled":
            await expect(self.page.locator(self.toggle_selector)).to_be_checked()
        elif validation_type == "disabled":
            await expect(self.page.locator(self.toggle_selector)).not_to_be_checked()

    async def check_message(self, message:str) -> None:
        """
        Verifies that a message appears on the page and clicks the continue button if visible.

        Args:
            message (str): The expected message text.

        Example:
            await check_message("Operation completed successfully!")

        Notes:
            - Uses `self.modal_message_selector` and `self.continue_button_selector` from the page object.
            - If the continue button is not visible, only verifies the message.
        """
        await expect(self.page.locator(self.modal_message_selector)).to_contain_text(message)

        #If the modal with the message have a continue button selector, clicks it
        continue_button = self.page.locator(self.continue_button_selector)
        if continue_button.is_visible():
            await self.page.click(self.continue_button_selector)

    async def is_visible(self, selector: str) -> None:
        """Verifies that an element is visible on the page."""
        await expect(self.page.locator(selector)).to_be_visible()

    async def is_not_visible(self, selector: str) -> None:
        """Verifies that an element is not visible on the page."""
        await expect(self.page.locator(selector)).not_to_be_visible()

    async def is_checked(self, selector: str) -> None:
        """Verifies that a checkbox or radio button is checked."""
        await expect(self.page.locator(selector)).to_be_checked()

    async def have_value(self, selector: str, value: str) -> None:
        """Verifies that an input element has the expected value."""
        await expect(self.page.locator(selector)).to_have_value(value)

    async def wait_for_selector(self, selector: str, additional_wait: float = 0.05) -> None:
        """
        Waits for an element to appear on the page.
        
        Args:
            selector: CSS selector of the element to wait for
            additional_wait: Additional time in seconds to wait after element appears (default: 0.05)
        """
        await self.page.wait_for_selector(selector)
        await asyncio.sleep(additional_wait)

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

    async def get_selected_index(self, select_selector: str) -> int:
        """
        Gets the index of the currently selected option in a <select> element.

        Args:
            select_selector (str): Selector of the <select> element.

        Returns:
            int: Index of the selected option.
        """
        selected_value = await self.page.locator(select_selector).input_value()
        options = await self.page.locator(f'{select_selector} option').all()

        for index, option in enumerate(options):
            option_value = await option.get_attribute('value')
            if option_value == selected_value:
                return index

    async def hold_click(self, locator: Locator) -> None:
        """
        Simulates a click-and-hold action on the specified element, useful for drag-and-drop.

        Args:
            locator (Locator): Playwright locator of the element to click and hold.
        """
        bounding_box = await locator.bounding_box()
        await self.page.wait_for_timeout(3000)
        await self.page.mouse.move(
            bounding_box['x'] + bounding_box['width'] / 2,
            bounding_box['y'] + bounding_box['height'] / 2
        )
        await self.page.mouse.down()
        await self.page.wait_for_timeout(500)
        await self.page.mouse.up()

    async def get_text(self, selector: str) -> str:
        """
        Returns the text content of the specified element.

        Args:
            selector (str): Selector of the element.

        Returns:
            str: Text content of the element.

        Notes:
            - Waits for the element to be visible before retrieving the text.
        """
        await self.page.wait_for_selector(selector)
        element = self.page.locator(selector)
        return await element.inner_text()

    async def scroll_into_view(self, selector: str) -> None:
        """
        Scrolls the specified element into view.

        Args:
            selector (str): Selector of the element to scroll into view.

        Notes:
            - Ensures the element is visible in the viewport for interactions.
        """
        await self.page.wait_for_selector(selector)
        element = self.page.locator(selector)
        await element.scroll_into_view_if_needed()