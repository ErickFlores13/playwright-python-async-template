from typing import Any
from core.services.form_filling.base_strategy import BaseFieldStrategy
from core.services.form_filling.field import Field
from core.components.select2 import Select2Component

class Select2Strategy(BaseFieldStrategy):
    """Handles Select2 fields using Select2Component."""

    async def can_handle(self, field: Field) -> bool:
        """Only handle fields marked as Select2"""
        return field.is_select2

    async def fill(self, field: Field, value: Any) -> None:
        """Fill the Select2 field with the specified value."""
        component = await Select2Component.create(field.locator.page, field.selector)
        if isinstance(value, list):
            for val in value:
                await component.select(str(val))
        elif isinstance(value, str):
            await component.select(str(value))
        else:
            raise TypeError(f"Select2 field expects str or list of str, got {type(value).__name__}")

    async def clear_and_validate(self, field: Field) -> None:
        """Clears the Select2 field and validates it is cleared."""
        component = await Select2Component.create(field.locator.page, field.selector)
        await component.clear_and_validate()

    async def validate_in_edit_view(self, field: Field, expected_value: Any) -> None:
        """Validate the Select2 field has the expected value(s) selected in edit view.
        
        Args:
            field: The field to validate
            expected_value: For single-select, a string. For multi-select, a list of strings.
        """
        component = await Select2Component.create(field.locator.page, field.selector)
        await component.validate(expected_value)