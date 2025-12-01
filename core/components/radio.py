import logging
from playwright.async_api import Page, Locator, TimeoutError, expect

logger = logging.getLogger(__name__)

class RadioComponent:
    """Wrapper for a radio input group."""

    def __init__(self, page: Page, selector: str, timeout: int = 3000):
        self.page = page
        self.selector = selector
        self.timeout = timeout
        self.locator: Locator = page.locator(selector)

    async def wait_for_visible(self) -> None:
        """Wait for the radio inputs to be visible."""
        logger.debug(f"[Radio] Waiting for visibility of {self.selector}")
        await self.locator.wait_for(state="visible", timeout=self.timeout)

    async def select(self, value: str) -> None:
        """Select a radio input by value."""
        await self.wait_for_visible()
        option_locator = self.locator.locator(f"input[type='radio'][value='{value}']")
        await option_locator.wait_for(state="attached", timeout=self.timeout)
        logger.debug(f"[Radio] Selecting radio {value} in {self.selector}")
        await option_locator.check()

    async def get_value(self) -> str:
        """Return currently selected value."""
        await self.wait_for_visible()
        logger.debug(f"[Radio] Getting selected value from {self.selector}")
        count = await self.locator.locator("input[type='radio']:checked").count()
        if count == 0:
            return ""
        radio_value = await self.locator.locator("input[type='radio']:checked").first.get_attribute("value")
        logger.debug(f"[Radio] Selected value in {self.selector} is '{radio_value}'")
        return radio_value

    async def validate(self, expected_value: str) -> None:
        """Validate that the radio button with the expected value is selected.
        
        Args:
            expected_value: The expected value of the selected radio button
        """
        await self.wait_for_visible()
        logger.debug(f"[Radio] Validating {self.selector} has value '{expected_value}' selected")
        
        # Validate that the radio button with the expected value is checked
        radio_with_value = self.locator.locator(f"input[type='radio'][value='{expected_value}']")
        await expect(radio_with_value).to_be_checked()