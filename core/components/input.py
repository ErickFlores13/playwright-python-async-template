import logging
from playwright.async_api import Page, Locator, expect

logger = logging.getLogger(__name__)

class InputComponent:
    """Wrapper for standard text-like inputs and textareas."""

    def __init__(self, page: Page, selector: str, timeout: int = 3000):
        self.page = page
        self.selector = selector
        self.timeout = timeout
        self.locator: Locator = page.locator(selector)

    async def wait_for_visible(self) -> None:
        """Wait for input to be visible."""
        logger.debug(f"[InputComponent] Waiting for visibility of {self.selector}")
        await self.locator.wait_for(state="visible", timeout=self.timeout)
            
    async def fill(self, value: str) -> None:
        """Fill input with given value."""
        await self.wait_for_visible()
        logger.debug(f"[InputComponent] Filling {self.selector} with '{value}'")
        await self.locator.fill(str(value))

    async def clear(self) -> None:
        """Clear input value."""
        await self.wait_for_visible()
        logger.debug(f"[InputComponent] Clearing {self.selector}")
        await self.locator.fill("")

    async def validate_cleared(self) -> bool:
        """Validate if input is cleared."""
        await expect(self.locator).to_have_value("")
    
    async def clear_and_validate(self) -> bool:
        """Clear input and validate."""
        await self.clear()
        await self.validate_cleared()

    async def validate(self, expected_value: str) -> bool:
        """
        Validate input has the expected value.
        
        For numeric inputs, compares numeric values to handle formatting differences (e.g., 19 vs 19.00).
        For text inputs, uses Playwright's to_have_value for exact string comparison.
        """
        await self.wait_for_visible()
        
        input_type = await self.locator.get_attribute("type")
        
        # For number inputs, compare as floats to handle formatting differences
        if input_type == "number":
            actual_value = await self.locator.input_value()
            logger.debug(f"[InputComponent] Validating {self.selector} has numeric value '{expected_value}' (actual: '{actual_value}')")
            assert float(actual_value) == float(expected_value), f"Expected '{expected_value}', but got '{actual_value}'"
        else:
            # For text/other inputs, use Playwright's to_have_value
            logger.debug(f"[InputComponent] Validating {self.selector} has value '{expected_value}'")
            await expect(self.locator).to_have_value(str(expected_value))