import logging
from typing import Any
from core.services.form_filling.base_strategy import BaseFieldStrategy
from core.services.form_filling.field import Field
from core.componentes.datepicker import DatePickerComponent

logger = logging.getLogger(__name__)

class DatepickerStrategy(BaseFieldStrategy):

    async def can_handle(self, field: Field) -> bool:
        """Determines if this strategy can handle the given field."""
        return field.input_type == "date"

    async def fill(self, field: Field, value: Any) -> None:
        """Fills the date picker with the specified date value."""
        component = DatePickerComponent(field.locator.page, field.selector)
        await component.set_date(str(value))

    async def clear(self, field: Field) -> None:
        """Clears the date picker value."""
        component = DatePickerComponent(field.locator.page, field.selector)
        await component.clear()