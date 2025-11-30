import logging
from playwright.async_api import Page, Locator, expect

logger = logging.getLogger(__name__)

class DatePickerComponent:
    """Wrapper for native HTML date inputs."""

    def __init__(self, page: Page, selector: str, timeout: int = 3000):
        self.page = page
        self.selector = selector
        self.timeout = timeout
        self.locator: Locator = page.locator(selector)

    async def wait_for_visible(self) -> None:
        """Wait for the date picker to be visible."""
        logger.debug(f"[DatePicker] Waiting for visibility of {self.selector}")
        await self.locator.wait_for(state="visible", timeout=self.timeout)

    async def set_date(self, date_value: str) -> None:
        """Sets a specific date value."""
        await self.wait_for_visible()
        logger.debug(f"[DatePicker] Setting value of {self.selector} to {date_value}")
        await self.locator.fill(date_value)

    async def get_value(self) -> str:
        """Returns the current date value."""
        await self.wait_for_visible()
        logger.debug(f"[DatePicker] Getting value of {self.selector}")
        date_value = (await self.locator.input_value()).strip()
        logger.debug(f"[DatePicker] Value of {self.selector} is '{date_value}'")
        return date_value

    async def clear(self) -> None:
        """Clears the date value."""
        await self.wait_for_visible()
        logger.debug(f"[DatePicker] Clearing value of {self.selector}")
        await self.locator.fill("")

    async def validate_cleared(self) -> None:
        """Validate if date picker is cleared."""
        await expect(self.locator).to_have_value("")
    
    async def clear_and_validate(self) -> None:
        """Clear date picker and validate."""
        await self.clear()
        await self.validate_cleared()