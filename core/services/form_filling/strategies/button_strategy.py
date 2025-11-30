import logging
from typing import Any
from core.services.form_filling.base_strategy import BaseFieldStrategy
from core.services.form_filling.field import Field
from core.components.button import ButtonComponent

logger = logging.getLogger(__name__)


class ButtonStrategy(BaseFieldStrategy):
    """Handles button fields using ButtonComponent."""

    async def can_handle(self, field: Field) -> bool:
        """Determine if this strategy can handle the given field."""
        logger.debug(f"[ButtonStrategy] Checking if can handle field {field.selector} with tag {field.tag}")
        return (
            field.tag == "button" or
            (field.tag == "input" and field.input_type in ["button", "submit"]) or
            (field.tag == "a" and field.input_type == "button")
        )

    async def fill(self, field: Field, value: Any) -> None:
        """Click the button field."""
        logger.debug(f"[ButtonStrategy] Filling button field {field.selector} with value: {value}")
        component = ButtonComponent(field.locator.page, field.selector)
        await component.click()

    async def clear_and_validate(self, field: Field) -> None:
        # Buttons typically do not have a "clear" action
        return
