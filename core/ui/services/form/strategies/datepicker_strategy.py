import logging

from core.ui.components.datepicker import DatePickerComponent
from core.ui.services.form.base_strategy import BaseFieldStrategy
from core.ui.services.form.field import Field

logger = logging.getLogger(__name__)


class DatepickerStrategy(BaseFieldStrategy):

    async def can_handle(self, field: Field) -> bool:
        """Determines if this strategy can handle the given field."""
        return field.input_type == "date"

    async def fill(self, field: Field, value: str) -> None:
        """Fills the date picker with the specified date value."""
        if not isinstance(value, str):
            raise ValueError(f"Date picker requires str value, got {type(value).__name__}")
        component = DatePickerComponent(field.locator.page, field.selector)
        await component.set_date(value)

    async def clear_and_validate(self, field: Field) -> None:
        """Clears and validates the date picker value."""
        component = DatePickerComponent(field.locator.page, field.selector)
        await component.clear_and_validate()

    async def validate_in_edit_view(self, field: Field, expected_value: str) -> None:
        """Validate the date picker has the expected value in edit view.

        Args:
            field: The field to validate
            expected_value: The expected date value (e.g., '2024-12-31')
        """
        if not isinstance(expected_value, str):
            raise ValueError(
                f"Date picker requires str value for validation, got {type(expected_value).__name__}"
            )
        component = DatePickerComponent(field.locator.page, field.selector)
        await component.validate(expected_value)
