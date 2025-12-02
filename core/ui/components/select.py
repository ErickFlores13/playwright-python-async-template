import logging
from playwright.async_api import Page, Locator, expect

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

    async def select_by_partial_text(self, partial_text: str) -> None:
        """Select option containing the given text (partial match)."""
        await self.wait_for_visible()
        logger.debug(f"[Select] Selecting option containing '{partial_text}' in {self.selector}")
        
        # Get all options
        options = await self.locator.locator('option').all()
        
        # Find option containing the text
        for option in options:
            text = await option.text_content()
            if partial_text in text:
                value = await option.get_attribute('value')
                await self.locator.select_option(value=value)
                logger.debug(f"[Select] Selected option with value '{value}' (text: '{text}')")
                return
        
        raise ValueError(f"No option containing '{partial_text}' found in {self.selector}")

    async def get_value(self) -> str:
        """Get the currently selected value."""
        await self.wait_for_visible()
        select_value = (await self.locator.input_value()).strip()
        logger.debug(f"[Select] Selected value in {self.selector} is '{select_value}'")
        return select_value
    
    async def clear_selection(self) -> None:
        """Clear the selection (reset to empty)."""
        await self.wait_for_visible()
        logger.debug(f"[Select] Clearing selection in {self.selector}")
        await self.locator.select_option("")

    async def validate_cleared(self) -> None:
        """Validate if selection is cleared."""
        await expect(self.locator).to_have_value("")

    async def validate(self, expected_text: str) -> None:
        """Validate that the selected option contains the expected text.
        
        Args:
            expected_text: The expected text (partial match) in the selected option
        """
        await self.wait_for_visible()
        logger.debug(f"[Select] Validating {self.selector} has option containing '{expected_text}' selected")
        await expect(self.locator).to_contain_text(expected_text)

    async def clear_and_validate(self) -> None:
        """Clear selection and validate."""
        await self.clear_selection()
        await self.validate_cleared()