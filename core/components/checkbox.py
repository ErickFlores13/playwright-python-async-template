import logging
from playwright.async_api import Page, Locator

logger = logging.getLogger(__name__)

class CheckboxComponent:
    """Wrapper for a single checkbox input."""

    def __init__(self, page: Page, selector: str, timeout: int = 3000):
        self.page = page
        self.selector = selector
        self.timeout = timeout
        self.locator: Locator = page.locator(selector)

    async def wait_for_visible(self) -> None:
        """Wait for the checkbox to be visible."""
        logger.debug(f"[Checkbox] Waiting for visibility of {self.selector}")
        await self.locator.wait_for(state="visible", timeout=self.timeout)

    async def is_checked(self) -> bool:
        """Return whether the checkbox is checked."""
        await self.wait_for_visible()
        logger.debug(f"[Checkbox] Checking if {self.selector} is checked")
        return await self.locator.is_checked()

    async def check(self) -> None:
        """Check the checkbox."""
        await self.wait_for_visible()
        if not await self.locator.is_checked():
            logger.debug(f"[Checkbox] Checking {self.selector}")
            await self.locator.check()

    async def uncheck(self) -> None:
        """Uncheck the checkbox."""
        await self.wait_for_visible()
        if await self.locator.is_checked():
            logger.debug(f"[Checkbox] Unchecking {self.selector}")
            await self.locator.uncheck()

    async def toggle(self) -> None:
        """Toggle the checkbox state."""
        await self.wait_for_visible()
        logger.debug(f"[Checkbox] Toggling {self.selector}")
        await self.locator.click()
