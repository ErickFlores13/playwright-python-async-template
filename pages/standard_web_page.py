from playwright.async_api import Page, expect
from pages.base_page import BasePage
from utils.consts import FilterType, ButtonOperations, ValidationType
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
        self.cancel_selector = 'button:has-text("Cancelar")'
        self.cancel_form_selector = 'a:has-text("Cancelar")'
        self.clear_filters_selector = 'a:has-text("Borrar filtros")'
        self.delete_button_selector = 'a[title="Eliminar"]'
        self.enable_button_selector = 'input[title="Habilitar"]'
        self.table_selector = '#ipi-table'
        self.no_datos_selector = 'td:has-text("No hay datos disponibles")'
        self.back_button = 'a:has-text("Volver")'
        self.title_selector = 'h1:has-text("Título de la página")'  # Update with actual title text
        

    async def validate_table_data(self, data_filters: dict) -> None:
        """
        Validates that the table displays rows matching the specified filter data.

        This method searches with the provided filters and checks that each 
        row in the table is visible and contains the expected values.

        Args:
            data_filters (dict): Dictionary where keys are column identifiers 
                                (or logical names) and values are the expected text 
                                to be present in the row's cells.

        Raises:
            AssertionError: If a row or cell does not match the expected data.

        Example:
            >>> await self.validate_table_data({'Name': 'John', 'Status': 'Active'})
        """
        await self.search_with_filters(data_filters)

        table_locator = self.page.locator(self.table_selector)
        await expect(table_locator).to_be_visible()

        rows = await table_locator.locator('tbody tr').all()
        for row in rows:
            await expect(row).to_be_visible()
            for key, value in data_filters.items():
                cell_locator = row.locator(f'td:has-text("{value}")')
                await expect(cell_locator).to_be_visible()
        

    async def validate_no_data_in_table(self, data_filters: dict) -> None:
        """
        Validates that the table shows no data for the given filters.

        Searches with the provided filters and checks that the table displays 
        the "No data available" message or equivalent.

        Args:
            data_filters (dict): Dictionary with the filter criteria to apply.

        Raises:
            AssertionError: If the table contains data rows.

        Example:
            await self.validate_no_data_in_table({'Status': 'Inactive'})
        """
        await self.search_with_filters(data_filters)
        await self.is_visible(self.no_datos_selector)


    async def fields_validations(
    self,
    data: dict,
    field_selector: str,
    validation_type: Literal[
        "max_length", "min_length", "max", "min",
        "data_type", "required", "pattern", "disabled"
    ]
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

        Raises:
            ValueError: If an invalid validation_type is passed.

        Example:
            >>> await self.fields_validations(
                    field_selector="input[name='username']", 
                    data={'username': 'testuser'}, 
                    validation_type='max'
                )
        """
        await self.remove_attributes(field_selector, validation_type)
        await self.page.wait_for_timeout(1000)
        await self.fill_data(data)
        await self.page.click(self.submit_button_selector)


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
                
        
    async def filter_with_specific_field(self, selector: str, value: str) -> None:
        """
        Applies a filter to a specific field and triggers the search.

        Args:
            selector (str): CSS selector of the filter input field.
            value (str): Value to enter in the filter field.

        Example:
            >>> await self.filter_with_specific_field("input[name='username']", "John")
        """
        data_filter = {selector: value}
        await self.search_with_filters(data_filter)
        

    async def validate_filter(self, filter_type, view_to_validate, data_filters=None) -> None:
        """
        Validates different filter operations based on the specified filter type.

        Args:
            filter_type (str): Type of filter validation to perform. 
                            Supported values: 'EMPTY', 'INVALID', 'CLEAR' (FilterType enum values)
            view_to_validate (Callable): Method that navigates to the view where the filter will be applied.
            data_filters (dict, optional): Dictionary of filter fields and values, used for invalid or clear validations.

        Example:
            >>> await self.validate_filter(FilterType.EMPTY.value, self.goto_index_view)
        """
        #Validate the usage of the Enum
        if not isinstance(filter_type, FilterType):
            raise TypeError(f"Expected FilterType, got {type(filter_type).__name__}")

        filter_actions = {
            FilterType.EMPTY.value: lambda: self.filter_with_empty_filters(view_to_validate),
            FilterType.INVALID.value: lambda: self.validate_invalid_filters(view_to_validate, data_filters),
            FilterType.CLEAR.value: lambda: self.validate_clear_filters(view_to_validate, data_filters),
        }

        action = filter_actions.get(filter_type)
        if action:
            await action()


    async def filter_with_empty_filters(self, view_to_validate: Callable[[], Any]) -> None:
        """
        Applies the filter with no values entered and triggers the search.

        Args:
            view_to_validate (Callable): Method that navigates to the page where the filter is applied.
        """
        await view_to_validate()
        await self.page.click(self.filter_button_selector)


    async def validate_invalid_filters(self, view_to_validate: Callable[[], Any], data_filters: dict) -> None:
        """
        Validates that using invalid filter values returns an empty table.

        Args:
            view_to_validate (Callable): Method that navigates to the page where the filter is applied.
            data_filters (dict): Dictionary of invalid filters to apply.
        """
        await view_to_validate()
        await self.search_with_filters(data_filters, self.filter_button_selector)
        await self.validate_no_data_in_table(data_filters)


    async def validate_clear_filters(self, view_to_validate: Callable[[], Any], data_filters: dict) -> None:
        """
        Validates that the "Clear Filters" button works correctly by ensuring
        all filters are reset after being cleared.

        Args:
            view_to_validate (Callable): Method that navigates to the page where the filter is applied.
            data_filters (dict): Dictionary of filters applied before clearing.
        """
        await view_to_validate()
        await self.search_with_filters(data_filters, self.filter_button_selector)
        await self.clean_filters(data_filters)


    async def clean_filters(self, data_filters: dict) -> None:
        """
        Clears all applied filters and verifies that all specified filter fields are empty.

        Steps:
            1. Clicks the "Clear Filters" button.
            2. Verifies that all fields specified in `data_filters` are empty.

        Args:
            data_filters (dict): Dictionary containing selectors of filter fields to verify.

        Raises:
            AssertionError: If any field still contains a value after clearing.
        """
        await self.page.click(self.clear_filters_selector)

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

    async def cancel_create_operation(self, goto_create_method: Callable[..., Any]) -> None:
        """
        Navigates to the create form, clicks the cancel button, and validates
        that the user is redirected back to the index page.

        Args:
            goto_create_method (Callable[..., Any]): Method that navigates to the create form.
        """
        await goto_create_method()
        await self.page.click(self.cancel_form_selector)
        await self._validate_redirect_to_index()

    async def cancel_edit_operation(self, goto_edit_method: Callable[..., Any], data: dict = None) -> None:
        """
        Navigates to the edit form, clicks the cancel button, and optionally validates
        that the edit view still contains the original data.

        Args:
            goto_edit_method (Callable[..., Any]): Method that navigates to the edit form.
            data (Dict[str, Any] | None): Optional dictionary with expected data to validate.
        """
        await goto_edit_method()
        await self.page.click(self.cancel_form_selector)
        if data:
            await self.validate_edit_view_item_information(data, self)

    async def cancel_delete_operation(self, search_method: Callable[..., Any], data: dict = None) -> None:
        """
        Searches for a record, opens the delete modal, clicks cancel,
        and validates that the record still exists.

        Args:
            search_method (Callable[..., Any]): Method used to search the record.
            data (Dict[str, Any] | None): Optional dictionary with expected data to validate.
        """
        await search_method()
        await self.wait_for_selector(self.delete_button_selector)
        await self.page.locator(self.delete_button_selector).first.click()
        await self.wait_for_selector(self.cancel_selector)
        await self.page.click(self.cancel_selector)
        if data:
            await self.validate_edit_view_item_information(data, self)

    async def cancel_enable_operation(self, search_method: Callable[..., Any], data: dict = None) -> None:
        """
        Searches for a disabled record, opens the enable confirmation, clicks cancel,
        and validates that the record remains disabled.

        Args:
            search_method (Callable[..., Any]): Method used to search the record.
            data (Dict[str, Any] | None): Optional dictionary with expected data to validate.
        """
        import inspect

        sig = inspect.signature(search_method)
        if 'is_disabled' in sig.parameters:
            await search_method(is_disabled=True)
        else:
            await search_method()

        await self.wait_for_selector(self.enable_button_selector)
        await self.page.locator(self.enable_button_selector).first.click()
        await self.page.click(self.cancel_selector)
        if data:
            await self.validate_edit_view_item_information(data, self)

    async def back_create_operation(self, goto_create_method: Callable[..., Any]) -> None:
        """
        Navigates to the create form, clicks the back button, and validates
        that the user is redirected to the index view.

        Args:
            goto_create_method (Callable[..., Any]): Method that navigates to the create form.
        """
        await goto_create_method()
        await self.page.click(self.back_button)
        await self._validate_redirect_to_index()

    async def back_edit_operation(self, goto_edit_method: Callable[..., Any]) -> None:
        """
        Navigates to the edit form, clicks the back button, and validates
        that the user is redirected to the index view.

        Args:
            goto_edit_method (Callable[..., Any]): Method that navigates to the edit form.
        """
        await goto_edit_method()
        await self.page.click(self.back_button)
        await self._validate_redirect_to_index()

    async def back_detail_operation(self, goto_detail_method: Callable[..., Any]) -> None:
        """
        Navigates to the detail view, clicks the back button, and validates
        that the user is redirected to the index view.

        Args:
            goto_detail_method (Callable[..., Any]): Method that navigates to the detail view.
        """
        await goto_detail_method()
        await self.page.click(self.back_button)
        await self._validate_redirect_to_index()

    async def back_delete_operation(self, goto_disabled_method: Callable[..., Any]) -> None:
        """
        Navigates to the 'Disabled Records' view, clicks the back button,
        and validates that the user is redirected to the index view.

        Args:
            goto_disabled_method (Callable[..., Any]): Method that navigates to the disabled view.
        """
        await goto_disabled_method()
        await self.page.click(self.back_button)
        await self._validate_redirect_to_index()

    async def _validate_redirect_to_index(self) -> None:
        """Helper to validate that the title of the module it's visible"""
        if self.title_selector:
            await expect(self.page.locator(self.title_selector)).to_be_visible()