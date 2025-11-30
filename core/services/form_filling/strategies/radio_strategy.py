import logging
from typing import Any
from core.services.form_filling.base_strategy import BaseFieldStrategy
from core.services.form_filling.field import Field
from core.components.radio import RadioComponent

logger = logging.getLogger(__name__)

class RadioStrategy(BaseFieldStrategy):

    async def can_handle(self, field: Field) -> bool:
        """Determine if this strategy can handle the given field."""
        logger.debug(f"[RadioStrategy] Checking if can handle field {field.selector}")
        return field.input_type == "radio"

    async def fill(self, field: Field, value: Any) -> None:
        """Fill the radio field with the given value."""
        component = RadioComponent(field.locator.page, field.selector)
        await component.select(str(value))

    async def clear(self, field: Field) -> None:
        # Radios cannot be 'cleared' in the traditional sense; there is no unselect option.
        return
