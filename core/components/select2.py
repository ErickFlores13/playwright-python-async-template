import logging
import re
from playwright.async_api import Page, Locator, TimeoutError
from typing import List, Optional, Union
from core.utils.exceptions import Select2Error, ConfigurationError

logger = logging.getLogger(__name__)

class Select2Component:
    """
    Robust Select2 component handler.
    Works with default Select2 4.x structure.
    """

    def __init__(self, page: Page, selector: str, timeout: int = 5000):
        self.page = page
        self.selector = selector
        self.timeout = timeout
        self.root: Optional[Locator] = None

    # -----------------------------
    # Core Select2 locators
    # -----------------------------
    @property
    def dropdown(self) -> Locator:
        return self.page.locator(".select2-dropdown")

    @property
    def results(self) -> Locator:
        return self.page.locator(".select2-results__option")
    
    @property
    def multi_field_textarea(self) -> Locator:
        return self.root.locator("textarea.select2-search__field")
    
    @property
    def single_field_input(self) -> Locator:
        return self.page.locator("input.select2-search__field") # note: outside root
    
    @property
    def single_value_display(self) -> Locator:
        return self.root.locator(".select2-selection__rendered")
    
    @property
    def multi_value_display(self) -> Locator:
        return self.root.locator(".select2-selection__choice__display")
    
    @property
    def clear_all(self) -> Locator:
        return self.root.locator(".select2-selection__clear")

    @property
    def single_clear(self) -> Locator:
        return self.root.locator(".select2-selection__choice__remove")
    
    @classmethod
    async def create(cls, page: Page, selector: str, timeout: int = 5000) -> "Select2Component":
        """
        Factory method to create and initialize a Select2Component instance.
        Args:
            page (Page): Playwright Page instance.
            selector (str): Selector for the Select2 root container.
            timeout (int): Timeout for operations in milliseconds.
        Returns:
            Select2Component: Initialized Select2Component instance.
        """
        inst = cls(page, selector, timeout=timeout)
        root_locator = inst.page.locator(inst.selector)
        inst.root = await inst._resolve_select2_root(root_locator)
        return inst

    async def search_field(self) -> Locator:
        """
        Returns the search field for this Select2 component.

        Handles:
        - Multi-select: <textarea.select2-search__field> inside root
        - Single-select: <input.select2-search__field> generated dynamically after opening dropdown
        """
        # 1. Check for multi-select textarea inside root
        if await self.multi_field_textarea.is_visible():
            return self.multi_field_textarea

        # 2. Otherwise, single-select: open the dropdown and look for input
        await self.root.click()

        await self.single_field_input.wait_for(state="attached", timeout=self.timeout)

        if await self.single_field_input.is_visible():
            return self.single_field_input

        raise Select2Error(
            selector=self.selector,
            message="No visible Select2 search field found (multi or single select)."
        )

    # -----------------------------
    # Public API
    # -----------------------------

    async def open(self) -> None:
        """Opens the Select2 dropdown."""
        logger.debug(f"[Select2] Opening Select2 ({self.selector})")

        await self.root.click()

        try:
            await self.dropdown.wait_for(state="visible", timeout=self.timeout)
        except TimeoutError as e:
            raise Select2Error(
                selector=self.root,
                message="Search field did not become visible after opening Select2.",
                cause=e
            )

    async def close(self) -> None:
        """
        Closes the Select2 dropdown if open.
        """
        if await self.dropdown.is_visible():
            logger.debug(f"[Select2] Dropdown visible, closing: ({self.dropdown})")
            await self.page.keyboard.press("Escape") # try to close with Escape
            if await self.dropdown.is_visible(): 
                await self.root.click() # try to close by clicking outside if escape didn't work

        try:
            await self.dropdown.wait_for(state="hidden", timeout=self.timeout)
        except TimeoutError as e:
            raise Select2Error(
                selector=self.dropdown,
                message="Dropdown did not close after attempting to close Select2.",
                cause=e
            )

    async def search(self, query: str) -> None:
        """Performs a search in the Select2 dropdown."""
        logger.debug(f"[Select2] Searching for '{query}'")

        search_field = await self.search_field()

        await search_field.fill(query)

        # Wait for results to load or update
        try:
            await self.dropdown.wait_for(state="visible", timeout=self.timeout)
        except TimeoutError as e:
            raise Select2Error(
                selector=self.dropdown,
                message=f"Dropdown did not show results after searching for '{query}'.",
                cause=e
            )

    async def select(self, value: str) -> None:
        """
        Selects an exisiting option by visible text or creates it if allowed.
        Get or create select2 supported.
        - If the value exists, it will be selected.
        - If it does not exist, and Select2 is configured to allow new options, it will be created.
        - If it does not exist and cannot be created, do nothing.
        """

        await self.search(value)

        option_locator = self.results.filter(has_text=re.escape(value), exact=True)

        if await option_locator.count() > 0:
            logger.debug(f"[Select2] Selecting existing option '{value}'")
            await option_locator.first.click() # select existing option
        else:
            logger.debug(f"[Select2] Option '{value}' not found, attempting to create it.")
            await self.page.keyboard.press("Enter") # try to create new option or do nothing

        if await self.get_value():
            logger.debug(f"[Select2] Successfully selected or created option '{value}'")
            await self.close()
        else:
            raise Select2Error(
                selector=self.selector,
                message=f"Failed to select or create option '{value}'."
            )        

    async def clear(self) -> None:
        """Clears the current selection(s)."""

        # Close dropdown if open
        if await self.dropdown.is_visible():
            logger.debug(f"[Select2] Dropdown: {self.dropdown} is open, closing before clearing selections.")
            await self.close()

        # Try clear all
        if await self.clear_all.is_visible():
            logger.debug(f"[Select2] Using clear-all button: {self.clear_all} to clear selections.")
            await self.clear_all.click()
            return

        # Try per-item clear (for multi-select without clear-all button)
        if await self.single_clear.is_visible():
            logger.debug(f"[Select2] Using per-item clear buttons: {self.single_clear} to clear selections.")
            while await self.single_clear.count() > 0: # loop to remove all
                await self.single_clear.nth(0).click()

        # Nothing to clear
        logger.debug(f"[Select2] No clear button in {self.selector} available to clear selections, nothing to clear.")
        return

    async def get_value(self) -> Optional[Union[str, List[str]]]:
        """Return the currently selected value(s) as visible text."""
        # Check multi-select first
        if await self.multi_value_display.count() > 0:
            logger.debug(f"[Select2] Found multiple selected values: {self.multi_value_display}")
            multi_count = await self.multi_value_display.count()
            texts = [await self.multi_value_display.nth(i).inner_text() for i in range(multi_count)]
            return texts

        # Fallback to single-select
        if await self.single_value_display.is_visible():
            logger.debug(f"[Select2] Found single selected value: {self.single_value_display}")
            text = await self.single_value_display.inner_text()
            return text

        return None
    
    async def get_options(self) -> List[str]:
        """Return a list of all options currently visible."""

        await self.open()

        count = await self.results.count()
        options = [await self.results.nth(i).inner_text() for i in range(count)]
        logger.debug(f"[Select2] Found options: {options}")

        return [opt.strip() for opt in options]
    
    async def _resolve_select2_root(self, locator: Locator) -> Locator:
        """Given a Locator, identify and return the Select2 root container Locator."""
        # --- CASE 1: element is inside static container ---
        closest_container = locator.locator("closest=.select2-container")
        if await closest_container.count() > 0:
            logger.debug(f"[Select2] Found Select2 container via closest(): {closest_container.first}")
            return closest_container.first

        # --- CASE 2: original <select> passed ---
        is_select = await locator.evaluate("el => el.tagName.toLowerCase() === 'select'")
        if is_select:
            sibling = locator.locator("xpath=following-sibling::*[contains(@class, 'select2-container')]")
            if await sibling.count() > 0:
                logger.debug(f"[Select2] Found Select2 container via sibling of <select>: {sibling.first}")
                return sibling.first

        # --- CASE 3: wrapper div passed ---
        descendant = locator.locator(".select2-container")
        if await descendant.count() > 0:
            logger.debug(f"[Select2] Found Select2 container via descendant: {descendant.first}")
            return descendant.first

        # --- INVALID CASE: inside dropdown popup ---
        in_popup = await locator.evaluate("el => el.closest('.select2-container--open') !== null")
        if in_popup:
            raise ConfigurationError(
                config_key="select2",
                message="Invalid locator: do not pass dynamic dropdown inputs."
            )

        raise ConfigurationError(
            config_key="select2",
            message="Cannot identify Select2 root. Pass parent div, original <select>, or static child."
        )