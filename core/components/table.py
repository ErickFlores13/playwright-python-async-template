import logging
from typing import List
from playwright.async_api import Page, Locator

logger = logging.getLogger(__name__)

class TableComponent:
    """Utility class to interact with HTML tables."""

    def __init__(self, page: Page, selector: str, timeout: int = 3000):
        self.page = page
        self.selector = selector
        self.timeout = timeout
        self.locator: Locator = page.locator(selector)

    async def wait_for_visible(self) -> None:
        """Wait for the table to be visible."""
        logger.debug(f"[Table] Waiting for visibility of {self.selector}")
        await self.locator.wait_for(state="visible", timeout=self.timeout)

    async def get_rows(self) -> List[Locator]:
        """Return list of row locators."""
        await self.wait_for_visible()
        logger.debug(f"[Table] Getting rows for {self.selector}")
        return self.locator.locator("tr")

    async def get_row_texts(self) -> List[List[str]]:
        """Return table data as list of rows with cell texts."""
        rows = await self.get_rows()
        data = []
        for i in range(await rows.count()):
            row = rows.nth(i)
            cells = row.locator("th, td")
            row_texts = [await cells.nth(j).inner_text() for j in range(await cells.count())]
            logger.debug(f"[Table] Row {i} texts: {row_texts}")
            data.append([text.strip() for text in row_texts])
        logger.debug(f"[Table] Full table data for {self.selector}: {data}")
        return data

    async def click_row(self, index: int) -> None:
        """Click a row by index (0-based)."""
        rows = await self.get_rows()
        if index >= await rows.count():
            raise IndexError(f"Row index {index} out of range for table {self.selector}")
        logger.debug(f"[Table] Clicking row {index} for {self.selector}")
        await rows.nth(index).click()
