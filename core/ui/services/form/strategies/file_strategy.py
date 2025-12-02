import logging
from typing import Union

from core.ui.components.file import FileComponent
from core.ui.services.form.base_strategy import BaseFieldStrategy
from core.ui.services.form.field import Field

logger = logging.getLogger(__name__)


class FileStrategy(BaseFieldStrategy):
    """Handles file input fields using FileComponent."""

    async def can_handle(self, field: Field) -> bool:
        """Determine if this strategy can handle the given field."""
        return field.input_type == "file"

    async def fill(self, field: Field, value: Union[str, list[str]]) -> None:
        """Upload file(s) to the file input."""
        component = FileComponent(field.locator.page, field.selector)

        if isinstance(value, list):
            for file_path in value:
                await component.upload(file_path)
        else:
            await component.upload(value)

    async def clear_and_validate(self, field: Field) -> None:
        """Clear the file input and validate it is cleared."""
        component = FileComponent(field.locator.page, field.selector)
        await component.clear_and_validate()

    async def validate_in_edit_view(self, field: Field, value=None) -> None:
        """Validate that a file has been uploaded to the file input.

        Note: Due to browser security restrictions, we can only verify that
        a file exists, but cannot validate the specific filename matches expected_value.
        This method simply validates that the file input is not empty.

        Args:
            field: The field to validate
        """
        component = FileComponent(field.locator.page, field.selector)
        await component.validate_has_file()
