import logging
from typing import Any
from core.services.form_filling.base_strategy import BaseFieldStrategy
from core.services.form_filling.field import Field
from core.componentes.input import InputComponent
from core.utils.exceptions import ValidationError

logger = logging.getLogger(__name__)

class InputStrategy(BaseFieldStrategy):
    """Strategy to handle text-like inputs (text, textarea, password, email, search, tel, url, number)."""

    TEXT_INPUT_TYPES = ["text", "textarea", "password", "email", "search", "tel", "url", "number"]

    async def can_handle(self, field: Field) -> bool:
        """Determine if this strategy can handle the given field."""
        return field.input_type in self.TEXT_INPUT_TYPES

    async def fill(self, field: Field, value: Any) -> None:
        """Fill the input field with the provided text value."""
        if not isinstance(value, str):
            raise ValidationError("text", f"Text input requires str, got {type(value).__name__}")
        
        component = InputComponent(field.locator.page, field.selector)
        await component.fill(value)

    async def clear(self, field: Field) -> None:
        """Clear the input field."""
        component = InputComponent(field.locator.page, field.selector)
        await component.clear()
