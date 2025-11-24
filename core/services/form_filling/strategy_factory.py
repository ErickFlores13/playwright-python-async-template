import logging
from typing import Dict, Any
from core.services.form_filling.base_strategy import BaseFieldStrategy
from core.services.form_filling.field import Field
from core.services.form_filling.strategies.button_strategy import ButtonStrategy
from core.services.form_filling.strategies.checkbox_strategy import CheckboxStrategy
from core.services.form_filling.strategies.datepicker_strategy import DatepickerStrategy
from core.services.form_filling.strategies.file_strategy import FileStrategy
from core.services.form_filling.strategies.input_strategy import InputStrategy
from core.services.form_filling.strategies.radio_strategy import RadioStrategy
from core.services.form_filling.strategies.select_strategy import SelectStrategy
from core.services.form_filling.strategies.select2_strategy import Select2Strategy
from core.services.form_filling.element_resolver import ElementResolver
from utils.exceptions import FormFillingError

logger = logging.getLogger(__name__)

class StrategyFactory:
    """Factory to get appropriate field strategies based on field properties."""

    def __init__(self, element_resolver: ElementResolver) -> None:
        """Initialize the StrategyFactory with an ElementResolver."""
        # ElementResolver is needed to resolve field properties and the page context
        self.resolver = element_resolver
        self.strategies: list[BaseFieldStrategy] = [
            ButtonStrategy(),
            CheckboxStrategy(),
            DatepickerStrategy(),
            FileStrategy(),
            InputStrategy(),
            RadioStrategy(),
            SelectStrategy(),
            Select2Strategy(),
        ]

    def get_strategy(self, field: Field) -> BaseFieldStrategy:
        """Return the appropriate strategy for a Field."""
        for strategy in self.strategies:
            if strategy.can_handle(field):
                return strategy
        raise ValueError(f"No strategy found for field: {field.selector} ({field.tag}/{field.input_type})")

    async def fill_data(self, data: Dict[str, Any]) -> None:
        """
        Fill multiple fields based on the provided data dictionary.
        Args:
            data (Dict[str, Any]): A dictionary mapping field selectors to values.
        Examples:
            >>> await strategy_factory.fill_data({
            ...     "#username": "testuser",
            ...     "#password": "securepass",
            ...     "#remember-me": True,
            ...     "#profile-picture": "/path/to/pic.jpg",
            ...     "#birthdate": "1990-01-01",
            ...     "#country": "US",
            ...     "#hobbies": ["reading", "traveling"],
            ...     "#add-address": [
            ...         {"#street": "123 Main St", "#city": "Anytown"},
            ...         {"#street": "456 Oak Ave", "#city": "Othertown"}
            ...     ],
            ...     "select2-choices": ["option1", "option2"],
            ... })
        """
        for selector, value in data.items():
            field = await self.resolver.resolve_field(selector)
            strategy = self.get_strategy(field)

            # -----------------------------
            # Formset handling: button + list of dicts
            # -----------------------------
            if isinstance(value, list) and field.tag == "button":
                for item in value:
                    if not isinstance(item, dict):
                        raise FormFillingError(f"Expected dict for formset item, got {type(item)}", field_selector=selector)
                    
                    # Click the add button to create a new row
                    await strategy.fill(field, None)
                    logger.debug(f"New formset row added for button '{selector}'")
                    # Fill the row recursively
                    await self.fill_data(item)

            # -----------------------------
            # List of values (multi-selects, multi-files)
            # -----------------------------
            elif isinstance(value, list):
                for item in value:
                    logger.debug(f"Filling field '{selector}' with value: {item}")
                    await strategy.fill(field, item)

            # -----------------------------
            # Single value
            # -----------------------------
            else:
                logger.debug(f"Filling field '{selector}' with value: {value}")
                await strategy.fill(field, value)
