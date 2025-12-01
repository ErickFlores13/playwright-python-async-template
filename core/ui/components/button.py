import logging
from playwright.async_api import Page, Locator

logger = logging.getLogger(__name__)

class ButtonComponent:
    """Simple Button wrapper for a single clickable element."""

    def __init__(self, page: Page, selector: str, timeout: int = 3000):
        self.page = page
        self.selector = selector
        self.timeout = timeout
        self.locator: Locator = self.page.locator(selector)

    async def wait_for_visible(self) -> None:
        """Wait for the button to be visible."""
        logger.debug(f"[Button] Waiting for visibility of {self.selector}")
        await self.locator.wait_for(state="visible", timeout=self.timeout)

    async def click(self) -> None:
        """Click the button."""
        await self.wait_for_visible()
        logger.debug(f"[Button] Clicking {self.selector}")
        await self.locator.click()
        
    async def get_text(self) -> str:
        """Return the button text."""
        await self.wait_for_visible()
        button_text = (await self.locator.text_content()).strip()
        logger.debug(f"[Button] Text of {self.selector} is '{button_text}'")
        return button_text

    async def is_enabled(self) -> bool:
        """Check if button is enabled."""
        logger.debug(f"[Button] Checking if {self.selector} is enabled")
        return not await self.locator.is_disabled()
