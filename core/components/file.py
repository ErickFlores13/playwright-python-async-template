import logging
from playwright.async_api import Page, Locator, expect

logger = logging.getLogger(__name__)

class FileComponent:
    """Wrapper for <input type='file'> elements."""

    def __init__(self, page: Page, selector: str, timeout: int = 3000):
        self.page = page
        self.selector = selector
        self.timeout = timeout
        self.locator: Locator = self.page.locator(selector)

    async def wait_for_visible(self) -> None:
        """Wait for file input to be visible."""
        logger.debug(f"[FileComponent] Waiting for visibility of {self.selector}")
        await self.locator.wait_for(state="visible", timeout=self.timeout)

    async def upload(self, file_path: str) -> None:
        """Upload a file."""
        await self.wait_for_visible()
        logger.debug(f"[FileComponent] Uploading file {file_path} to {self.selector}")
        await self.locator.set_input_files(file_path)

    async def clear(self) -> None:
        """Clear the selected file(s)."""
        await self.wait_for_visible()
        logger.debug(f"[FileComponent] Clearing files from {self.selector}")
        await self.locator.evaluate("el => el.value = ''")

    async def validate_cleared(self) -> None:
        """Validate if file input is cleared."""
        await expect(self.locator).to_have_value("")

    async def clear_and_validate(self) -> None:
        """Clear file input and validate."""
        await self.clear()
        await self.validate_cleared()
