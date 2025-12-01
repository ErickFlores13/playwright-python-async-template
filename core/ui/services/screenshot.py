import logging
from playwright.async_api import Page
from core.utils.exceptions import ConfigurationError

logger = logging.getLogger(__name__)

class Screenshot:
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
    
    async def take_screenshot(self, name: str = None) -> str:
        """
        Takes a screenshot of the current page.

        Args:
            name (str, optional): Custom name for the screenshot file.

        Returns:
            str: Path to the saved screenshot file.
        """
        from datetime import datetime
        import os
        
        if not name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"screenshot_{timestamp}"
        
        screenshots_dir = "screenshots"
        os.makedirs(screenshots_dir, exist_ok=True)
        
        screenshot_path = os.path.join(screenshots_dir, f"{name}.png")
        await self.page.screenshot(path=screenshot_path, full_page=True)
        
        logger.debug(f"Screenshot saved: {screenshot_path}")
        return screenshot_path

    async def highlight_element(self, selector: str, duration: int = 2000) -> None:
        """
        Highlights an element by adding a colored border (useful for debugging).

        Args:
            selector (str): Selector of the element to highlight.
            duration (int): Duration to keep the highlight in milliseconds.
        """
        await self.page.locator(selector).evaluate(
            """(element, duration) => {
                element.style.border = '3px solid red';
                element.style.backgroundColor = 'yellow';
                setTimeout(() => {
                    element.style.border = '';
                    element.style.backgroundColor = '';
                }, duration);
            }""",
            duration
        )