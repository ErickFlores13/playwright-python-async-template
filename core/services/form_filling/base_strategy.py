from typing import Any
from abc import ABC, abstractmethod
from core.services.form_filling.field import Field


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