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
from core.utils.exceptions import FormFillingError

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

    async def get_strategy(self, field: Field) -> BaseFieldStrategy:
        """Return the appropriate strategy for a Field."""
        for strategy in self.strategies:
            if await strategy.can_handle(field):
                return strategy
        raise FormFillingError(f"No strategy found for field with selector: {field.selector}", field_selector=field.selector)

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
            strategy = await self.get_strategy(field)

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


    async def edit_item(self, new_data: dict) -> None:
        """
        Edit fields based on the provided new_data dictionary.
        Args:
            new_data (Dict[str, Any]): A dictionary mapping field selectors to new values.
        Examples:
            >>> await strategy_factory.edit_item({
            ...     "#username": "newuser",
            ...     "#password": "newpass",
            ...     "#remember-me": False,
            ...     "#profile-picture": "/path/to/newpic.jpg",
            ...     "#birthdate": "1992-02-02",
            ...     "#country": "CA",
            ...     "#hobbies": ["gaming", "cooking"],
            ... })
        """
        await self.clear_fields(new_data)
        await self.fill_data(new_data)


    async def clear_fields(self, data: dict) -> None:
        """
        Clear multiple fields based on the provided data dictionary.
        Args:
            data (Dict[str, Any]): A dictionary mapping field selectors to values.
        Examples:
            >>> await strategy_factory.clear_fields({
            ...     "#username": None,
            ...     "#password": None,
            ...     "#remember-me": None,
            ...     "#profile-picture": None,
            ...     "#birthdate": None,
            ...     "#country": None,
            ...     "#hobbies": None,
            ... })
        """
        for selector in data.keys():
            field = await self.resolver.resolve_field(selector)
            strategy = await self.get_strategy(field)

            logger.debug(f"Clearing field '{selector}'")
            await strategy.clear_and_validate(field)


    async def validate_edit_view(self, expected_data: dict) -> None:
        """
        Validate multiple fields in edit view based on the provided expected_data dictionary.
        Args:
            expected_data (Dict[str, Any]): A dictionary mapping field selectors to expected values.
        Examples:
            >>> await strategy_factory.validate_edit_view({
            ...     "#username": "newuser",
            ...     "#password": "newpass",
            ...     "#remember-me": False,
            ...     "#profile-picture": "/path/to/newpic.jpg",
            ...     "#birthdate": "1992-02-02",
            ...     "#country": "CA",
            ...     "#hobbies": ["gaming", "cooking"],
            ... })
        """
        for selector, expected_value in expected_data.items():
            field = await self.resolver.resolve_field(selector)
            strategy = await self.get_strategy(field)

            logger.debug(f"Validating field '{selector}' has expected value: {expected_value}")
            await strategy.validate_in_edit_view(field, expected_value)
