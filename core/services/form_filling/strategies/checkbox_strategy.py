from core.services.form_filling.base_strategy import BaseFieldStrategy
from core.services.form_filling.field import Field
from core.components.checkbox import CheckboxComponent

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
