import logging
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from utils.exceptions import (
    ElementNotFoundError, 
    ConfigurationError,
)

logger = logging.getLogger(__name__)

class WaitMixin:
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
        """
        Waits for the page to fully load including network requests.

        Args:
            timeout (int): Timeout in milliseconds (default: 30000).
            
        Raises:
            ElementNotFoundError: if page doesn't load within timeout.
        """
        try:
            await self.page.wait_for_load_state("networkidle", timeout=timeout)
            await self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
            logger.info("Page loaded successfully")
        except PlaywrightTimeoutError as e:
            await self.take_screenshot("page_load_timeout")
            raise ElementNotFoundError("page", timeout=timeout) from e
        except Exception as e:
            await self.take_screenshot("page_load_error")
            raise ElementNotFoundError("page", timeout=timeout) from e