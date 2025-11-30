import logging
from typing import Any
from core.services.form_filling.base_strategy import BaseFieldStrategy
from core.services.form_filling.field import Field
from core.components.select import SelectComponent

logger = logging.getLogger(__name__)

class SelectStrategy(BaseFieldStrategy):
    """Handles native <select> fields using SelectComponent."""

    async def can_handle(self, field: Field) -> bool:
        """Determine if this strategy can handle the given field."""
        logger.debug(f"[SelectStrategy] Checking if can handle field {field.selector}")
        return field.tag == "select"

    async def fill(self, field: Field, value: Any) -> None:
        """Fill the select field with the given value."""
        component = SelectComponent(field.locator.page, field.selector)
        if isinstance(value, (str)):
            await component.select_by_text(str(value))
        else:
            raise TypeError(f"Select field expects str, got {type(value).__name__}")

    async def clear_and_validate(self, field: Field) -> None:
        """Clear and validate the select field."""
        logger.debug(f"[SelectStrategy] Clearing select field {field.selector}")
        component = SelectComponent(field.locator.page, field.selector)
        await component.clear_and_validate()