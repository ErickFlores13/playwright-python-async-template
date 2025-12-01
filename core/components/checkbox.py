import logging
from playwright.async_api import Page, Locator, expect

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

    async def validate_unchecked(self) -> None:
        """Validate that the checkbox is unchecked."""
        await expect(self.locator).not_to_be_checked()

    async def validate(self, expected_checked: bool) -> None:
        """Validate that the checkbox matches the expected state.
        
        Args:
            expected_checked: True if checkbox should be checked, False if unchecked
        """
        await self.wait_for_visible()
        logger.debug(f"[Checkbox] Validating {self.selector} is {'checked' if expected_checked else 'unchecked'}")
        if expected_checked:
            await expect(self.locator).to_be_checked()
        else:
            await expect(self.locator).not_to_be_checked()

    async def uncheck_and_validate(self) -> None:
        """Uncheck the checkbox and validate it is unchecked."""
        await self.uncheck()
        await self.validate_unchecked()

    async def toggle(self) -> None:
        """Toggle the checkbox state."""
        await self.wait_for_visible()
        logger.debug(f"[Checkbox] Toggling {self.selector}")
        await self.locator.click()
