from typing import Any
from abc import ABC, abstractmethod
from core.ui.services.form.field import Field


class BaseFieldStrategy(ABC):
    """Base interface for field strategies."""

    @abstractmethod
    async def can_handle(self, field: Field) -> bool:
        """Determine if this strategy can handle the given field."""
        raise NotImplementedError()

    @abstractmethod
    async def fill(self, field: Field, value: Any) -> None:
        """Fill the field with the specified value."""
        raise NotImplementedError()

    @abstractmethod
    async def clear_and_validate(self, field: Field) -> None:
        """Clear the field's value and validate it is cleared."""
        raise NotImplementedError()
    
    @abstractmethod
    async def validate_in_edit_view(self, field: Field, expected_value: Any) -> None:
        """Validate the field's value in the edit view."""
        raise NotImplementedError()