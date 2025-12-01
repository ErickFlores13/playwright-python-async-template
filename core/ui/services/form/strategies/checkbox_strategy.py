from core.ui.services.form.base_strategy import BaseFieldStrategy
from core.ui.services.form.field import Field
from core.ui.components.checkbox import CheckboxComponent

class CheckboxStrategy(BaseFieldStrategy):
    """Handles single checkbox fields."""

    async def can_handle(self, field: Field) -> bool:
        """Determine if this strategy can handle the given field."""
        return field.tag == "input" and field.input_type == "checkbox"

    async def fill(self, field: Field, value: bool) -> None:
        """`value` must be bool: True=check, False=uncheck"""
        if not isinstance(value, bool):
            raise ValueError(f"[CheckboxStrategy] Value for checkbox must be bool, got {type(value)}")

        component = CheckboxComponent(field.locator.page, field.selector)
        if value:
            await component.check()
        else:
            await component.uncheck()

    async def clear_and_validate(self, field: Field) -> None:
        """Clear the checkbox by unchecking it and validate the action."""
        component = CheckboxComponent(field.locator.page, field.selector)
        await component.uncheck_and_validate()

    async def validate_in_edit_view(self, field: Field, expected_value: bool) -> None:
        """Validate the checkbox has the expected state in edit view.
        
        Args:
            field: The field to validate
            expected_value: True if checkbox should be checked, False if unchecked
        """
        if not isinstance(expected_value, bool):
            raise ValueError(f"[CheckboxStrategy] Value for checkbox validation must be bool, got {type(expected_value)}")
        
        component = CheckboxComponent(field.locator.page, field.selector)
        await component.validate(expected_value)
