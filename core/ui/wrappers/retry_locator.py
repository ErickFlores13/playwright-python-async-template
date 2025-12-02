"""
Retry wrapper for Playwright Locator.

Automatically retries failed operations to handle transient failures
before escalating to expensive AI healing.
"""

import asyncio
import logging
from typing import Any

from playwright.async_api import Locator
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)


class RetryLocator:
    """
    Wrapper that retries failed locator operations.

    Handles transient failures (network glitches, timing issues, loading delays)
    by retrying operations before escalating to AI healing.

    Benefits:
    - Reduces AI healing costs (retry is free, AI is expensive)
    - Handles flaky tests gracefully
    - Configurable retry count and delay

    Usage:
        locator = page.locator("input")
        locator = RetryLocator(locator, max_retries=3, delay=1.0)
        await locator.click()  # Will retry up to 3 times if fails
    """

    def __init__(
        self, locator: Locator, max_retries: int = 3, delay: float = 1.0, selector: str = "unknown"
    ):
        """
        Initialize retry wrapper.

        Args:
            locator: Playwright Locator to wrap
            max_retries: Maximum retry attempts (default: 3)
            delay: Delay between retries in seconds (default: 1.0)
            selector: Selector string for logging (default: "unknown")
        """
        self._locator = locator
        self.max_retries = max_retries
        self.delay = delay
        self.selector = selector

    async def _retry_operation(self, operation_name: str, operation_func, *args, **kwargs) -> Any:
        """
        Execute operation with retry logic.

        Args:
            operation_name: Name of the operation (for logging)
            operation_func: Async function to execute
            *args: Positional arguments for operation
            **kwargs: Keyword arguments for operation

        Returns:
            Result of the operation

        Raises:
            Exception from last retry attempt if all retries fail
        """
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(
                    f"[RETRY] [{operation_name}] Attempt {attempt}/{self.max_retries} for {self.selector}"
                )
                result = await operation_func(*args, **kwargs)

                if attempt > 1:
                    logger.info(
                        f"[RETRY SUCCESS] [{operation_name}] Succeeded on attempt {attempt} for {self.selector}"
                    )

                return result

            except PlaywrightTimeoutError as e:
                last_error = e
                if attempt < self.max_retries:
                    logger.warning(
                        f"⚠️ [{operation_name}] Timeout on attempt {attempt}/{self.max_retries} "
                        f"for {self.selector}, retrying in {self.delay}s..."
                    )
                    await asyncio.sleep(self.delay)
                else:
                    logger.warning(
                        f"❌ [{operation_name}] All {self.max_retries} retries exhausted for {self.selector}, "
                        f"escalating to next layer (AI healing if enabled)"
                    )

            except Exception as e:
                # Non-timeout errors - don't retry
                logger.debug(
                    f"[WARN] [{operation_name}] Non-timeout error, not retrying: {type(e).__name__}"
                )
                raise

        # All retries exhausted, raise last error
        raise last_error

    # ============================================================================
    # LOCATOR METHODS - Wrap with retry logic
    # ============================================================================

    async def click(self, **kwargs) -> None:
        """Click element with retry."""
        return await self._retry_operation("click", self._locator.click, **kwargs)

    async def fill(self, value: str, **kwargs) -> None:
        """Fill element with retry."""
        return await self._retry_operation("fill", self._locator.fill, value, **kwargs)

    async def press(self, key: str, **kwargs) -> None:
        """Press key with retry."""
        return await self._retry_operation("press", self._locator.press, key, **kwargs)

    async def select_option(self, value=None, **kwargs) -> list[str]:
        """Select option with retry."""
        return await self._retry_operation(
            "select_option", self._locator.select_option, value, **kwargs
        )

    async def check(self, **kwargs) -> None:
        """Check checkbox with retry."""
        return await self._retry_operation("check", self._locator.check, **kwargs)

    async def uncheck(self, **kwargs) -> None:
        """Uncheck checkbox with retry."""
        return await self._retry_operation("uncheck", self._locator.uncheck, **kwargs)

    async def set_checked(self, checked: bool, **kwargs) -> None:
        """Set checked state with retry."""
        return await self._retry_operation(
            "set_checked", self._locator.set_checked, checked, **kwargs
        )

    async def hover(self, **kwargs) -> None:
        """Hover over element with retry."""
        return await self._retry_operation("hover", self._locator.hover, **kwargs)

    async def focus(self, **kwargs) -> None:
        """Focus element with retry."""
        return await self._retry_operation("focus", self._locator.focus, **kwargs)

    async def blur(self, **kwargs) -> None:
        """Blur element with retry."""
        return await self._retry_operation("blur", self._locator.blur, **kwargs)

    async def clear(self, **kwargs) -> None:
        """Clear element with retry."""
        return await self._retry_operation("clear", self._locator.clear, **kwargs)

    async def dblclick(self, **kwargs) -> None:
        """Double-click element with retry."""
        return await self._retry_operation("dblclick", self._locator.dblclick, **kwargs)

    async def dispatch_event(self, event_type: str, event_init=None, **kwargs) -> None:
        """Dispatch event with retry."""
        return await self._retry_operation(
            "dispatch_event", self._locator.dispatch_event, event_type, event_init, **kwargs
        )

    async def drag_to(self, target, **kwargs) -> None:
        """Drag to target with retry."""
        return await self._retry_operation("drag_to", self._locator.drag_to, target, **kwargs)

    async def screenshot(self, **kwargs) -> bytes:
        """Take screenshot with retry."""
        return await self._retry_operation("screenshot", self._locator.screenshot, **kwargs)

    async def scroll_into_view_if_needed(self, **kwargs) -> None:
        """Scroll into view with retry."""
        return await self._retry_operation(
            "scroll_into_view_if_needed", self._locator.scroll_into_view_if_needed, **kwargs
        )

    async def set_input_files(self, files, **kwargs) -> None:
        """Set input files with retry."""
        return await self._retry_operation(
            "set_input_files", self._locator.set_input_files, files, **kwargs
        )

    async def tap(self, **kwargs) -> None:
        """Tap element with retry."""
        return await self._retry_operation("tap", self._locator.tap, **kwargs)

    async def type(self, text: str, **kwargs) -> None:
        """Type text with retry."""
        return await self._retry_operation("type", self._locator.type, text, **kwargs)

    # ============================================================================
    # READ-ONLY METHODS - Delegate directly (no retry needed)
    # ============================================================================

    async def bounding_box(self, **kwargs):
        """Get bounding box (no retry)."""
        return await self._locator.bounding_box(**kwargs)

    async def count(self) -> int:
        """Get element count (no retry)."""
        return await self._locator.count()

    async def get_attribute(self, name: str, **kwargs) -> str | None:
        """Get attribute (no retry)."""
        return await self._locator.get_attribute(name, **kwargs)

    async def inner_html(self, **kwargs) -> str:
        """Get inner HTML (no retry)."""
        return await self._locator.inner_html(**kwargs)

    async def inner_text(self, **kwargs) -> str:
        """Get inner text (no retry)."""
        return await self._locator.inner_text(**kwargs)

    async def input_value(self, **kwargs) -> str:
        """Get input value (no retry)."""
        return await self._locator.input_value(**kwargs)

    async def is_checked(self, **kwargs) -> bool:
        """Check if checked (no retry)."""
        return await self._locator.is_checked(**kwargs)

    async def is_disabled(self, **kwargs) -> bool:
        """Check if disabled (no retry)."""
        return await self._locator.is_disabled(**kwargs)

    async def is_editable(self, **kwargs) -> bool:
        """Check if editable (no retry)."""
        return await self._locator.is_editable(**kwargs)

    async def is_enabled(self, **kwargs) -> bool:
        """Check if enabled (no retry)."""
        return await self._locator.is_enabled(**kwargs)

    async def is_hidden(self, **kwargs) -> bool:
        """Check if hidden (no retry)."""
        return await self._locator.is_hidden(**kwargs)

    async def is_visible(self, **kwargs) -> bool:
        """Check if visible (no retry)."""
        return await self._locator.is_visible(**kwargs)

    async def text_content(self, **kwargs) -> str | None:
        """Get text content (no retry)."""
        return await self._locator.text_content(**kwargs)

    # ============================================================================
    # CHAINING METHODS - Return wrapped locators
    # ============================================================================

    def locator(self, selector: str, **kwargs):
        """Create child locator (wrapped)."""
        child = self._locator.locator(selector, **kwargs)
        return RetryLocator(child, self.max_retries, self.delay, selector)

    def filter(self, **kwargs):
        """Filter locator (wrapped)."""
        filtered = self._locator.filter(**kwargs)
        return RetryLocator(filtered, self.max_retries, self.delay, self.selector)

    def first(self):
        """Get first element (wrapped)."""
        first = self._locator.first
        return RetryLocator(first, self.max_retries, self.delay, f"{self.selector}:first")

    def last(self):
        """Get last element (wrapped)."""
        last = self._locator.last
        return RetryLocator(last, self.max_retries, self.delay, f"{self.selector}:last")

    def nth(self, index: int):
        """Get nth element (wrapped)."""
        nth = self._locator.nth(index)
        return RetryLocator(nth, self.max_retries, self.delay, f"{self.selector}:nth({index})")

    # ============================================================================
    # WAIT METHODS - Delegate with retry
    # ============================================================================

    async def wait_for(self, **kwargs) -> None:
        """Wait for element with retry."""
        return await self._retry_operation("wait_for", self._locator.wait_for, **kwargs)

    # ============================================================================
    # PASSTHROUGH - Delegate to underlying locator
    # ============================================================================

    def __getattr__(self, name: str):
        """Delegate unknown methods to underlying locator."""
        return getattr(self._locator, name)
