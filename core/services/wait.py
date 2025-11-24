import logging
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from core.utils.exceptions import (
    ElementNotFoundError, 
    ConfigurationError,
)

logger = logging.getLogger(__name__)

class Wait:
    """
    Generic base page with overridable playwright methods that allow a custom-made test automation.
    """

    def __init__(self, page: Page) -> None:
        if not page:
            raise ConfigurationError(
                config_key="page",
                message="Page instance cannot be None or empty"
            )
            
        self.page = page
        

    async def wait_for_page_load(self, timeout: int = 30000) -> None:
        logger.debug("Waiting for page full load (networkidle preferred)")

        try:
            await self.page.wait_for_load_state("networkidle", timeout=timeout)
            logger.debug("Page reached networkidle state")
        except PlaywrightTimeoutError:
            logger.warning("Networkidle not reached, falling back to domcontentloaded")
            await self.page.wait_for_load_state("domcontentloaded", timeout=timeout)

        logger.debug("Page loaded successfully")