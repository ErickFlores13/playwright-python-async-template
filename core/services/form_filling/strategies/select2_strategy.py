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
        await component.select(str(value))

    async def clear_and_validate(self, field: Field) -> None:
        """Clears the Select2 field and validates it is cleared."""
        component = await Select2Component.create(field.locator.page, field.selector)
        await component.clear_and_validate()