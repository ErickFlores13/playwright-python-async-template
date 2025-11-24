import logging
from typing import Union
from core.services.form_filling.base_strategy import BaseFieldStrategy
from core.services.form_filling.field import Field
from core.componentes.file import FileComponent

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

    async def clear(self, field: Field) -> None:
        """Clear the file input."""
        component = FileComponent(field.locator.page, field.selector)
        await component.clear()

