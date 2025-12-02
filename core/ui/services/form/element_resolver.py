import logging
from typing import Optional, Tuple, Union

from playwright.async_api import Locator, Page

from core.ui.services.form.field import Field
from core.utils.exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class ElementResolver:
    """
    Service for resolving and interacting with web elements.
    Provides helper methods to identify element types and interact with complex widgets like Select2.
    Designed to be used as part of a modular Page Object Model for test automation.
    """

    def __init__(self, page: Page, default_timeout: int = 5000) -> None:
        if not page:
            raise ConfigurationError(config_key="page", message="Page instance required")
        self.page = page
        self.timeout = default_timeout

    # -----------------------
    # Basic helpers
    # -----------------------
    async def get_locator(self, selector_or_locator: Union[str, Locator]) -> Locator:
        """
        Resolve and return a Locator from a selector string or return the Locator as-is.

        Args:
            selector_or_locator (Union[str, Locator]): Selector string or Locator instance.

        Returns:
            Locator: The resolved Locator instance.
        """
        if isinstance(selector_or_locator, Locator):
            return selector_or_locator
        return self.page.locator(selector_or_locator)

    async def get_field_props(
        self, selector_or_locator: Union[str, Locator]
    ) -> Tuple[str, Optional[str], bool]:
        """
        Given a selector or Locator, return a tuple of (tag, type, is_select2).

        Args:
            selector_or_locator (Union[str, Locator]): Selector string or Locator instance.

        Returns:
            Tuple[str, Optional[str], bool]: A tuple containing:

        Examples:
            >>> tag, input_type, is_select2 = await resolver.get_field_props("#my-input")
        """
        locator = await self.get_locator(selector_or_locator)
        props = await locator.evaluate(
            """el => ({
                tag: el.tagName ? el.tagName.toLowerCase() : null,
                type: el.type || null,
                select2: !!(el.classList && el.classList.contains && el.classList.contains('select2-container'))
            })"""
        )
        tag = props.get("tag") or ""
        input_type = props.get("type")
        is_select2 = bool(props.get("select2"))
        logger.debug(
            f"get_field_props: selector={selector_or_locator} -> tag={tag} type={input_type} select2={is_select2}"
        )
        return tag, input_type, is_select2

    async def resolve_field(self, selector: str) -> Field:
        """
        Given a selector or Locator, return a fully-resolved Field object.

        Args:
            selector (str): Selector string.

        Returns:
            Field: A Field object containing metadata about the element.
        """
        locator = await self.get_locator(selector)
        await locator.wait_for(state="visible", timeout=self.timeout)

        tag, input_type, is_select2 = await self.get_field_props(locator)
        logger.debug(
            f"resolve_field: selector={selector} -> Field(tag={tag}, type={input_type}, select2={is_select2})"
        )

        return Field(
            selector=selector,
            locator=locator,
            tag=tag,
            input_type=input_type or "",
            is_select2=is_select2,
        )
