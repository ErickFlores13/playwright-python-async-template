from playwright.async_api import Page, expect
from pages.base_page import BasePage
from utils.consts import FilterType, ButtonOperations, ValidationType
from utils.exceptions import ElementNotFoundError, ValidationError
from typing import Literal, Callable, Any


class StandardWebPage(BasePage):
    """
    A class that encapsulates interactions with a web page, providing methods for
    form manipulation, data validation, and user interaction.

    This class is designed to facilitate the automation of web interactions using
    Playwright. Each method within this class operates on the current page context
    and assumes that the user is already on the appropriate page or form.

    Attributes:
        page (Page): An instance of the Playwright Page class, representing the current page.
    """
    
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        
    
    async def create_item_workflow(self, 
                                form_data: dict,
                                create_button_selector: str,
                                success_message_selector: str,
                                redirect_wait: bool = True) -> None:
        """Complete create workflow with validation."""
        await self.fill_data(form_data)
        await self.page.click(create_button_selector)
        
        if redirect_wait:
            await self.wait_for_page_load()
        
        if success_message_selector:
            await self.is_visible(success_message_selector)

    async def edit_item_workflow(self,
                            edit_data: dict,
                            edit_button_selector: str,
                            save_button_selector: str,
                            success_message_selector: str) -> None:
        """Complete edit workflow."""
        await self.page.click(edit_button_selector)
        await self.edit_item(edit_data)
        await self.page.click(save_button_selector)
        await self.wait_for_page_load()
        
        if success_message_selector:
            await self.is_visible(success_message_selector)

    async def search_with_filters(self, data_filters: dict, filter_button_selector: str) -> None:
        """
        Applies the specified filters and initiates a search by clicking the filter button.

        Args:
            data_filters (dict): Dictionary with filter field selectors as keys
                                and filter criteria as values.
            filter_button_selector (str): Selector for the search/filter button.

        Example:
            await search_with_filters({
                'input[name="genre"]': 'Action',
                'input[name="year"]': '2023'
            }, 'button[type="submit"]')

        Notes:
            - Relies on `fill_data` to populate fields.
            - Select2 behavior is controlled by class attributes.
        """
        await self.fill_data(data_filters)
        await self.page.click(filter_button_selector)


    async def delete_item(self, delete_button_selector: str, confirm_delete_button_selector: str = None) -> None:
        """
        Deletes an item by clicking the delete button and confirming the action.

        Args:
            delete_button_selector (str): Selector for the delete button.
            confirm_delete_button_selector (str, optional): Selector for the confirmation button.
                                                        If None, no confirmation step is performed.

        Behavior:
            1. Clicks the delete button associated with the item.
            2. If confirmation selector is provided, clicks the confirmation button to finalize deletion.

        Notes:
            - Assumes that the delete button is visible and interactable.
            - If there is a modal after the first click and confirm_delete_button_selector is provided, 
            it will handle it automatically.
        """
        await self.page.click(delete_button_selector)

        if confirm_delete_button_selector:
            confirm_selector = self.page.locator(confirm_delete_button_selector)
            if await confirm_selector.is_visible():
                await self.page.click(confirm_delete_button_selector)

        await self.page.wait_for_load_state("domcontentloaded")


    async def validate_table_data(self, data_filters: dict, filter_button_selector: str, table_selector: str) -> None:
        """
        Validates that the table displays rows matching the specified filter data.

        This method searches with the provided filters and checks that each 
        row in the table is visible and contains the expected values.

        Args:
            data_filters (dict): Dictionary where keys are column identifiers 
                                (or logical names) and values are the expected text 
                                to be present in the row's cells.
            filter_button_selector (str): Selector for the filter/search button.
            table_selector (str): Selector for the table element.

        Raises:
            AssertionError: If a row or cell does not match the expected data.

        Example:
            >>> await self.validate_table_data({'Name': 'John', 'Status': 'Active'}, 'button[type="submit"]', '#data-table')
        """
        await self.search_with_filters(data_filters, filter_button_selector)

        table_locator = self.page.locator(table_selector)
        await expect(table_locator).to_be_visible()

        rows = await table_locator.locator('tbody tr').all()
        for row in rows:
            await expect(row).to_be_visible()
            for key, value in data_filters.items():
                cell_locator = row.locator(f'td:has-text("{value}")')
                await expect(cell_locator).to_be_visible()
        

    async def validate_no_data_in_table(self, data_filters: dict, filter_button_selector: str, no_data_selector: str) -> None:
        """
        Validates that the table shows no data for the given filters.

        Args:
            data_filters (dict): Dictionary with the filter criteria to apply.
            filter_button_selector (str): Selector for the filter/search button.
            no_data_selector (str): Selector for the "no data available" message.

        Example:
            await self.validate_no_data_in_table({'Status': 'Inactive'}, 'button[type="submit"]', 'td:has-text("No data")')
        """
        await self.search_with_filters(data_filters, filter_button_selector)
        await self.is_visible(no_data_selector)


    async def fields_validations(
        self,
        field_selector: str,
        data: dict,
        validation_type: Literal[
            "max_length", "min_length", "max", "min",
            "data_type", "required", "pattern", "disabled"
        ],
        submit_button_selector: str
    ) -> None:
        """
        Validates a form field by removing specified attributes, fills the form, and submits it.

        This method is useful for testing form validations by dynamically removing constraints 
        such as required fields, maxlength, min/max values, patterns, or input types.

        Steps:
            1. Removes the attribute(s) specified in `validation_type`.
            2. Waits 1 second for any DOM updates.
            3. Fills the form with the provided `data`.
            4. Clicks the submit button.

        Args:
            field_selector (str): CSS selector of the field to validate.
            data (dict): Dictionary containing form field selectors and their values to fill.
            validation_type (str | list): Attribute(s) to remove from the field before submission. 
                Allowed values: 
                    - "max_length", "min_length", "max", "min",
                    - "data_type", "required", "pattern", "disabled"
            submit_button_selector (str): Selector for the form submit button.

        Raises:
            ValueError: If an invalid validation_type is passed.

        Example:
            >>> await self.fields_validations(
                    field_selector="input[name='username']", 
                    data={'username': 'testuser'}, 
                    validation_type='max',
                    submit_button_selector='button[type="submit"]'
                )
        """
        await self.remove_attributes(field_selector, validation_type)
        await self.page.wait_for_timeout(1000)
        await self.fill_data(data)
        await self.page.click(submit_button_selector)


    async def remove_attributes(self, field_selector, validation_type) -> None:
        """
        Removes one or more attributes from a form field based on the validation type.

        This is a helper method for `fields_validations` and can be used independently 
        if you need to dynamically manipulate field attributes.

        Args:
            field_selector (str): Selector for the field to modify.
            validation_type (str | list): Attribute(s) to remove. Allowed values:
                - "max_length", "min_length", "max", "min",
                - "data_type", "required", "pattern", "disabled"

        Raises:
            ValueError: If an invalid `validation_type` is provided.

        Example:
            >>> await self.remove_attributes("input[name='username']", "required")
            >>> await self.remove_attributes("input[name='age']", ["min", "max"])
        """
        #Validate the usage of the Enum
        if not isinstance(validation_type, ValidationType):
            raise TypeError(f"Expected ValidatioType, got {type(validation_type).__name__}")

        validation_actions = {
            ValidationType.MAX_LENGTH.value: self.remove_max_length_attribute,
            ValidationType.MIN.value: self.remove_min_length_attribute,
            ValidationType.MAX.value: self.remove_max_attribute,
            ValidationType.MIN.value: self.remove_min_attribute,
            ValidationType.DATA_TYPE.value: self.remove_type_attribute,
            ValidationType.REQUIRED.value: self.remove_required_attribute,
            ValidationType.PATTERN.value: self.remove_pattern_attribute,
            ValidationType.DISABLED.value: self.remove_disabled_attribute,
        }

        if isinstance(validation_type, list):
            for option in validation_type:
                validation_action = validation_actions.get(option)
                if validation_action:
                    await validation_action(field_selector)
                else:
                    raise ValueError(f"Invalid validation_type: {option}")
        else:
            validation_action = validation_actions.get(validation_type)
            if validation_action:
                await validation_action(field_selector)
            else:
                raise ValueError(f"Invalid validation_type: {validation_type}")
                
        
    async def filter_with_specific_field(self, selector: str, value: str, filter_button_selector: str) -> None:
        """
        Applies a filter to a specific field and triggers the search.

        Args:
            selector (str): CSS selector of the filter input field.
            value (str): Value to enter in the filter field.
            filter_button_selector (str): Selector for the filter/search button.

        Example:
            >>> await self.filter_with_specific_field("input[name='username']", "John", 'button[type="submit"]')
        """
        data_filter = {selector: value}
        await self.search_with_filters(data_filter, filter_button_selector)
        

    async def validate_filter(self, filter_type, view_to_validate, filter_button_selector: str, data_filters=None, no_data_selector: str = None, clear_filters_selector: str = None) -> None:
        """
        Validates different filter operations based on the specified filter type.

        Args:
            filter_type (str): Type of filter validation to perform. 
                            Supported values: 'EMPTY', 'INVALID', 'CLEAR' (FilterType enum values)
            view_to_validate (Callable): Method that navigates to the view where the filter will be applied.
            filter_button_selector (str): Selector for the filter/search button.
            data_filters (dict, optional): Dictionary of filter fields and values, used for invalid or clear validations.
            no_data_selector (str, optional): Selector for the "no data available" message (required for INVALID filter type).
            clear_filters_selector (str, optional): Selector for the clear filters button (required for CLEAR filter type).

        Example:
            >>> await self.validate_filter(FilterType.EMPTY.value, self.goto_index_view, 'button[type="submit"]')
        """
        #Validate the usage of the Enum
        if not isinstance(filter_type, FilterType):
            raise TypeError(f"Expected FilterType, got {type(filter_type).__name__}")

        filter_actions = {
            FilterType.EMPTY.value: lambda: self.filter_with_empty_filters(view_to_validate, filter_button_selector),
            FilterType.INVALID.value: lambda: self.validate_invalid_filters(view_to_validate, data_filters, filter_button_selector, no_data_selector),
            FilterType.CLEAR.value: lambda: self.validate_clear_filters(view_to_validate, data_filters, filter_button_selector, clear_filters_selector),
        }

        action = filter_actions.get(filter_type)
        if action:
            await action()


    async def filter_with_empty_filters(self, view_to_validate: Callable[[], Any], filter_button_selector: str) -> None:
        """
        Applies the filter with no values entered and triggers the search.

        Args:
            view_to_validate (Callable): Method that navigates to the page where the filter is applied.
            filter_button_selector (str): Selector for the filter/search button.
        """
        await view_to_validate()
        await self.page.click(filter_button_selector)


    async def validate_invalid_filters(self, view_to_validate: Callable[[], Any], data_filters: dict, filter_button_selector: str, no_data_selector: str) -> None:
        """
        Validates that using invalid filter values returns an empty table.

        Args:
            view_to_validate (Callable): Method that navigates to the page where the filter is applied.
            data_filters (dict): Dictionary of invalid filters to apply.
            filter_button_selector (str): Selector for the filter/search button.
            no_data_selector (str): Selector for the "no data available" message.
        """
        await view_to_validate()
        await self.search_with_filters(data_filters, filter_button_selector)
        await self.validate_no_data_in_table(data_filters, filter_button_selector, no_data_selector)


    async def validate_clear_filters(self, view_to_validate: Callable[[], Any], data_filters: dict, filter_button_selector: str, clear_filters_selector: str) -> None:
        """
        Validates that the "Clear Filters" button works correctly by ensuring
        all filters are reset after being cleared.

        Args:
            view_to_validate (Callable): Method that navigates to the page where the filter is applied.
            data_filters (dict): Dictionary of filters applied before clearing.
            filter_button_selector (str): Selector for the filter/search button.
            clear_filters_selector (str): Selector for the clear filters button.
        """
        await view_to_validate()
        await self.search_with_filters(data_filters, filter_button_selector)
        await self.clean_filters(data_filters, clear_filters_selector)


    async def clean_filters(self, data_filters: dict, clear_filters_selector: str) -> None:
        """
        Clears all applied filters and verifies that all specified filter fields are empty.

        Steps:
            1. Clicks the "Clear Filters" button.
            2. Verifies that all fields specified in `data_filters` are empty.

        Args:
            data_filters (dict): Dictionary containing selectors of filter fields to verify.
            clear_filters_selector (str): Selector for the clear filters button.

        Raises:
            AssertionError: If any field still contains a value after clearing.
        """
        await self.page.click(clear_filters_selector)

        for selector in data_filters.keys():
            await self.is_visible(selector)
            field_value = await self.page.input_value(selector)
            assert field_value == "", f"The field {selector} still contains a value: '{field_value}'"


    async def validate_button_operations(
        self,
        operation_type: str,
        form_method: Callable[..., Any],
        data: dict = None
    ) -> None:
        """
        Validates button operations such as cancel or back actions based on the operation type.

        This method maps different button operation types (defined in the `ButtonOperations` enum)
        to their respective handlers and executes the corresponding validation flow.

        Args:
            operation_type (str): Type of button operation to perform.
            form_method (Callable[..., Any]): Method that navigates to the target form or view.
            data (Dict[str, Any] | None): Optional data to validate record information.

        Raises:
            ValueError: If the provided operation_type is not supported.

        Example:
            >>> await self.validate_button_operations(
                operation_type=ButtonOperations.CANCEL_CREATE.value,
                form_method=self.goto_create_form
            )
        """
        # Validate the usage of the Enum
        if not isinstance(operation_type, ButtonOperations):
            raise TypeError(f"Expected ButtonOperation, got {type(operation_type).__name__}")
        
        operation_actions = {
            ButtonOperations.CANCEL_CREATE.value: lambda: self.cancel_create_operation(form_method),
            ButtonOperations.CANCEL_EDIT.value: lambda: self.cancel_edit_operation(form_method, data),
            ButtonOperations.CANCEL_DELETE.value: lambda: self.cancel_delete_operation(form_method, data),
            ButtonOperations.CANCEL_ENABLE.value: lambda: self.cancel_enable_operation(form_method, data),
            ButtonOperations.BACK_CREATE.value: lambda: self.back_create_operation(form_method),
            ButtonOperations.BACK_EDIT.value: lambda: self.back_edit_operation(form_method),
            ButtonOperations.BACK_DETAIL.value: lambda: self.back_detail_operation(form_method),
            ButtonOperations.BACK_DISABLED.value: lambda: self.back_delete_operation(form_method),
            ButtonOperations.BACK_DETAIL_DISABLED.value: lambda: self.back_detail_operation(form_method),
            ButtonOperations.BACK_COPY.value: lambda: self.back_edit_operation(form_method),
            ButtonOperations.CANCEL_COPY.value: lambda: self.cancel_edit_operation(form_method, data),
        }

        action = operation_actions.get(operation_type)

        if not action:
            valid_ops = list(operation_actions.keys())
            raise ValueError(f"Unsupported operation_type: {operation_type}. Valid options: {valid_ops}")

        await action()

    async def cancel_create_operation(self, goto_create_method: Callable[..., Any], cancel_form_selector: str, title_selector: str = None) -> None:
        """
        Navigates to the create form, clicks the cancel button, and validates
        that the user is redirected back to the index page.

        Args:
            goto_create_method (Callable[..., Any]): Method that navigates to the create form.
            cancel_form_selector (str): Selector for the cancel button in the form.
            title_selector (str, optional): Selector for the page title to validate redirection.
        """
        await goto_create_method()
        await self.page.click(cancel_form_selector)
        await self._validate_redirect_to_index(title_selector)

    async def cancel_edit_operation(self, goto_edit_method: Callable[..., Any], cancel_form_selector: str, data: dict = None) -> None:
        """
        Navigates to the edit form, clicks the cancel button, and optionally validates
        that the edit view still contains the original data.

        Args:
            goto_edit_method (Callable[..., Any]): Method that navigates to the edit form.
            cancel_form_selector (str): Selector for the cancel button in the form.
            data (Dict[str, Any] | None): Optional dictionary with expected data to validate.
        """
        await goto_edit_method()
        await self.page.click(cancel_form_selector)
        if data:
            await self.validate_edit_view_item_information(data, self)

    async def cancel_delete_operation(self, search_method: Callable[..., Any], delete_button_selector: str, cancel_selector: str, data: dict = None) -> None:
        """
        Searches for a record, opens the delete modal, clicks cancel,
        and validates that the record still exists.

        Args:
            search_method (Callable[..., Any]): Method used to search the record.
            delete_button_selector (str): Selector for the delete button.
            cancel_selector (str): Selector for the cancel button in the modal.
            data (Dict[str, Any] | None): Optional dictionary with expected data to validate.
        """
        await search_method()
        await self.wait_for_selector(delete_button_selector)
        await self.page.locator(delete_button_selector).first.click()
        await self.wait_for_selector(cancel_selector)
        await self.page.click(cancel_selector)
        if data:
            await self.validate_edit_view_item_information(data, self)

    async def cancel_enable_operation(self, search_method: Callable[..., Any], enable_button_selector: str, cancel_selector: str, data: dict = None) -> None:
        """
        Searches for a disabled record, opens the enable confirmation, clicks cancel,
        and validates that the record remains disabled.

        Args:
            search_method (Callable[..., Any]): Method used to search the record.
            enable_button_selector (str): Selector for the enable button.
            cancel_selector (str): Selector for the cancel button in the modal.
            data (Dict[str, Any] | None): Optional dictionary with expected data to validate.
        """
        import inspect

        sig = inspect.signature(search_method)
        if 'is_disabled' in sig.parameters:
            await search_method(is_disabled=True)
        else:
            await search_method()

        await self.wait_for_selector(enable_button_selector)
        await self.page.locator(enable_button_selector).first.click()
        await self.page.click(cancel_selector)
        if data:
            await self.validate_edit_view_item_information(data, self)

    async def back_create_operation(self, goto_create_method: Callable[..., Any], back_button_selector: str, title_selector: str = None) -> None:
        """
        Navigates to the create form, clicks the back button, and validates
        that the user is redirected to the index view.

        Args:
            goto_create_method (Callable[..., Any]): Method that navigates to the create form.
            back_button_selector (str): Selector for the back button.
            title_selector (str, optional): Selector for the page title to validate redirection.
        """
        await goto_create_method()
        await self.page.click(back_button_selector)
        await self._validate_redirect_to_index(title_selector)

    async def back_edit_operation(self, goto_edit_method: Callable[..., Any], back_button_selector: str, title_selector: str = None) -> None:
        """
        Navigates to the edit form, clicks the back button, and validates
        that the user is redirected to the index view.

        Args:
            goto_edit_method (Callable[..., Any]): Method that navigates to the edit form.
            back_button_selector (str): Selector for the back button.
            title_selector (str, optional): Selector for the page title to validate redirection.
        """
        await goto_edit_method()
        await self.page.click(back_button_selector)
        await self._validate_redirect_to_index(title_selector)

    async def back_detail_operation(self, goto_detail_method: Callable[..., Any], back_button_selector: str, title_selector: str = None) -> None:
        """
        Navigates to the detail view, clicks the back button, and validates
        that the user is redirected to the index view.

        Args:
            goto_detail_method (Callable[..., Any]): Method that navigates to the detail view.
            back_button_selector (str): Selector for the back button.
            title_selector (str, optional): Selector for the page title to validate redirection.
        """
        await goto_detail_method()
        await self.page.click(back_button_selector)
        await self._validate_redirect_to_index(title_selector)

    async def back_delete_operation(self, goto_disabled_method: Callable[..., Any], back_button_selector: str, title_selector: str = None) -> None:
        """
        Navigates to the 'Disabled Records' view, clicks the back button,
        and validates that the user is redirected to the index view.

        Args:
            goto_disabled_method (Callable[..., Any]): Method that navigates to the disabled view.
            back_button_selector (str): Selector for the back button.
            title_selector (str, optional): Selector for the page title to validate redirection.
        """
        await goto_disabled_method()
        await self.page.click(back_button_selector)
        await self._validate_redirect_to_index(title_selector)

    async def _validate_redirect_to_index(self, title_selector: str = None) -> None:
        """Helper to validate that the title of the module it's visible"""
        if title_selector:
            await expect(self.page.locator(title_selector)).to_be_visible()

    # ========== Advanced Table Operations ==========
    
    async def extract_table_data(self, table_selector: str, headers: list = None) -> list:
        """
        Extracts all data from a table into a structured format.
        
        Args:
            table_selector (str): CSS selector for the table
            headers (list, optional): Custom column headers. If None, extracts from table headers.
            
        Returns:
            List of dictionaries where each dict represents a row with column headers as keys
            
        Example:
            data = await page.extract_table_data('table.data-table')
            # Returns: [{'Name': 'John', 'Email': 'john@example.com'}, ...]
        """
        await self.wait_for_selector(table_selector)
        
        if not headers:
            # Extract headers from table
            header_elements = await self.page.locator(f'{table_selector} thead th, {table_selector} thead td').all()
            headers = []
            for header in header_elements:
                text = await header.inner_text()
                headers.append(text.strip())
        
        # Extract row data
        rows_data = []
        rows = await self.page.locator(f'{table_selector} tbody tr').all()
        
        for row in rows:
            cells = await row.locator('td, th').all()
            row_data = {}
            
            for i, cell in enumerate(cells):
                if i < len(headers):
                    cell_text = await cell.inner_text()
                    row_data[headers[i]] = cell_text.strip()
            
            if row_data:  # Only add non-empty rows
                rows_data.append(row_data)
        
        return rows_data

    async def find_table_row_by_criteria(self, table_selector: str, criteria: dict) -> int:
        """
        Finds the index of a table row that matches the given criteria.
        
        Args:
            table_selector (str): CSS selector for the table
            criteria (dict): Dictionary with column_name: expected_value pairs
            
        Returns:
            int: Zero-based index of the matching row, -1 if not found
            
        Example:
            row_index = await page.find_table_row_by_criteria('table.users', 
                                                           {'Email': 'john@example.com', 'Status': 'Active'})
        """
        table_data = await self.extract_table_data(table_selector)
        
        for index, row in enumerate(table_data):
            match = True
            for column, expected_value in criteria.items():
                if column not in row or row[column] != expected_value:
                    match = False
                    break
            if match:
                return index
        
        return -1

    async def click_table_row_action(self, table_selector: str, row_criteria: dict, action_selector: str) -> None:
        """
        Clicks an action button/link in a specific table row.
        
        Args:
            table_selector (str): CSS selector for the table
            row_criteria (dict): Criteria to find the target row
            action_selector (str): CSS selector for the action within the row (relative to row)
            
        Example:
            await page.click_table_row_action('table.users', 
                                            {'Email': 'john@example.com'}, 
                                            'button.edit')
        """
        row_index = await self.find_table_row_by_criteria(table_selector, row_criteria)
        
        if row_index == -1:
            raise ElementNotFoundError(f"Table row with criteria {row_criteria}", timeout=5000)
        
        row_selector = f'{table_selector} tbody tr:nth-child({row_index + 1})'
        action_element = self.page.locator(f'{row_selector} {action_selector}')
        
        await action_element.click()

    # ========== Smart Pagination Handling ==========
    
    async def extract_all_paginated_data(self, table_selector: str, next_button_selector: str, 
                                       max_pages: int = 50) -> list:
        """
        Extracts data from all pages of a paginated table.
        
        Args:
            table_selector (str): CSS selector for the table
            next_button_selector (str): CSS selector for the "Next" button
            max_pages (int): Maximum pages to process (safety limit)
            
        Returns:
            list: Combined data from all pages
            
        Example:
            all_data = await page.extract_all_paginated_data('table.results', 'button.next')
        """
        all_data = []
        current_page = 1
        
        while current_page <= max_pages:
            # Extract data from current page
            page_data = await self.extract_table_data(table_selector)
            all_data.extend(page_data)
            
            # Check if next button exists and is enabled
            next_button = self.page.locator(next_button_selector)
            
            if not await next_button.count() or not await next_button.is_enabled():
                break
            
            # Click next and wait for page load
            await next_button.click()
            await self.wait_for_page_load()
            
            current_page += 1
        
        return all_data

    async def navigate_to_page(self, page_number: int, page_input_selector: str = None, 
                             page_button_template: str = None) -> None:
        """
        Navigates to a specific page in pagination.
        
        Args:
            page_number (int): Target page number
            page_input_selector (str, optional): Selector for page input field
            page_button_template (str, optional): Template for page button selector (use {page} placeholder)
            
        Example:
            await page.navigate_to_page(5, page_input_selector='input.page-input')
            # OR
            await page.navigate_to_page(5, page_button_template='button[data-page="{page}"]')
        """
        if page_input_selector:
            await self.page.fill(page_input_selector, str(page_number))
            await self.page.keyboard.press('Enter')
        elif page_button_template:
            page_button = page_button_template.format(page=page_number)
            await self.page.click(page_button)
        else:
            raise ValidationError("pagination", "Either page_input_selector or page_button_template must be provided")
        
        await self.wait_for_page_load()

    async def search_across_all_pages(self, search_criteria: dict, table_selector: str, 
                                    next_button_selector: str, max_pages: int = 50) -> list:
        """
        Searches for data matching criteria across all paginated pages.
        
        Args:
            search_criteria (dict): Criteria to match (column: value pairs)
            table_selector (str): CSS selector for the table
            next_button_selector (str): CSS selector for next button
            max_pages (int): Maximum pages to search
            
        Returns:
            list: All matching rows with their page numbers
            
        Example:
            results = await page.search_across_all_pages(
                {'Status': 'Active', 'Department': 'IT'}, 
                'table.employees', 
                'button.next'
            )
        """
        matching_results = []
        current_page = 1
        
        while current_page <= max_pages:
            page_data = await self.extract_table_data(table_selector)
            
            # Check each row against criteria
            for row_index, row in enumerate(page_data):
                match = True
                for column, expected_value in search_criteria.items():
                    if column not in row or row[column] != expected_value:
                        match = False
                        break
                
                if match:
                    result = row.copy()
                    result['_page_number'] = current_page
                    result['_row_index'] = row_index
                    matching_results.append(result)
            
            # Navigate to next page
            next_button = self.page.locator(next_button_selector)
            if not await next_button.count() or not await next_button.is_enabled():
                break
            
            await next_button.click()
            await self.wait_for_page_load()
            current_page += 1
        
        return matching_results