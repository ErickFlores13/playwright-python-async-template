import logging
from playwright.async_api import Page, Locator

logger = logging.getLogger(__name__)

class SelectComponent:
    """Wrapper for a native <select> element."""

    def __init__(self, page: Page, selector: str, timeout: int = 3000):
        self.page = page
        self.selector = selector
        self.timeout = timeout
        self.locator: Locator = page.locator(selector)

    async def wait_for_visible(self) -> None:
        """Wait for the select element to be visible."""
        logger.debug(f"[Select] Waiting for visibility of {self.selector}")
        await self.locator.wait_for(state="visible", timeout=self.timeout)

    async def select_by_value(self, value: str) -> None:
        """Select an option by its value attribute."""
        await self.wait_for_visible()
        logger.debug(f"[Select] Selecting value '{value}' in {self.selector}")
        await self.locator.select_option(value=value)

    async def select_by_text(self, text: str) -> None:
        """Select an option by its visible text."""
        await self.wait_for_visible()
        logger.debug(f"[Select] Selecting text '{text}' in {self.selector}")
        await self.locator.select_option(label=text)

    async def get_value(self) -> str:
        """Get the currently selected value."""
        await self.wait_for_visible()
        select_value = (await self.locator.input_value()).strip()
        logger.debug(f"[Select] Selected value in {self.selector} is '{select_value}'")
        return select_value