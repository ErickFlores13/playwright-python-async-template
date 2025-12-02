"""
Browser Manager for Playwright browser lifecycle management.

Manages browser instances using strategy pattern for configuration.

Author: Erick Guadalupe Félix Flores
License: MIT
"""
import logging
from typing import Optional, List
from playwright.async_api import Playwright, Browser, BrowserContext, async_playwright
from core.ui.browser.strategies.browser_strategy import BrowserStrategy

logger = logging.getLogger(__name__)


class BrowserManager:
    """
    Manages Playwright browser lifecycle with strategy-based configuration.
    
    This class handles:
    - Browser launch with strategy-specific options
    - Context creation with strategy-specific options
    - Resource cleanup (contexts, browser, playwright)
    
    Usage:
        strategy = get_browser_strategy()
        manager = BrowserManager(strategy)
        await manager.start()
        context = await manager.new_context()
        # ... use context ...
        await manager.stop()
    """
    
    def __init__(self, strategy: BrowserStrategy):
        """
        Initialize BrowserManager with a strategy.
        
        Args:
            strategy: Browser configuration strategy to use
        """
        self.strategy = strategy
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self._contexts: List[BrowserContext] = []
    
    async def start(self) -> None:
        """
        Initialize Playwright and launch browser.
        
        Uses the strategy to determine:
        - Which browser type to launch (chromium/firefox/webkit)
        - Launch options (headless, args, slow_mo, etc.)
        
        Raises:
            RuntimeError: If already started
        """
        if self.playwright is not None:
            raise RuntimeError("BrowserManager already started")
        
        # Start Playwright
        self.playwright = await async_playwright().start()
        logger.debug("Playwright started")
        
        # Get configuration from strategy
        browser_type = self.strategy.get_browser_type()
        launch_options = self.strategy.get_launch_options()
        
        # Launch appropriate browser
        if browser_type == "chromium":
            self.browser = await self.playwright.chromium.launch(**launch_options)
        elif browser_type == "firefox":
            self.browser = await self.playwright.firefox.launch(**launch_options)
        elif browser_type == "webkit":
            self.browser = await self.playwright.webkit.launch(**launch_options)
        else:
            raise ValueError(f"Unknown browser type: {browser_type}")
        
        logger.info(
            f"Browser launched: {browser_type}, "
            f"headless={launch_options.get('headless', False)}"
        )
    
    async def new_context(self, **override_options) -> BrowserContext:
        """
        Create a new browser context with strategy options.
        
        Args:
            **override_options: Optional overrides for context options
                              (merged with strategy options)
        
        Returns:
            BrowserContext: New browser context
        
        Raises:
            RuntimeError: If browser not started
        
        Example:
            # Use strategy defaults
            context = await manager.new_context()
            
            # Override specific options
            context = await manager.new_context(
                locale="es-ES",
                viewport={"width": 1280, "height": 720}
            )
        """
        if self.browser is None:
            raise RuntimeError("Browser not started. Call start() first.")
        
        # Get base options from strategy
        options = self.strategy.get_context_options()
        
        # Merge with overrides
        options.update(override_options)
        
        # Create context
        context = await self.browser.new_context(**options)
        self._contexts.append(context)
        
        logger.debug(f"Created browser context (total: {len(self._contexts)})")
        return context
    
    async def stop(self) -> None:
        """
        Cleanup all resources.
        
        Closes:
        1. All browser contexts
        2. Browser instance
        3. Playwright instance
        """
        # Close all contexts
        for context in self._contexts:
            try:
                await context.close()
            except Exception as e:
                logger.warning(f"Error closing context: {e}")
        
        self._contexts.clear()
        logger.debug("All contexts closed")
        
        # Close browser
        if self.browser:
            try:
                await self.browser.close()
                logger.info("Browser closed")
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
            finally:
                self.browser = None
        
        # Stop Playwright
        if self.playwright:
            try:
                await self.playwright.stop()
                logger.debug("Playwright stopped")
            except Exception as e:
                logger.warning(f"Error stopping Playwright: {e}")
            finally:
                self.playwright = None
    
    @property
    def is_started(self) -> bool:
        """Check if browser is started."""
        return self.browser is not None
    
    @property
    def active_contexts(self) -> int:
        """Get number of active contexts."""
        return len(self._contexts)
