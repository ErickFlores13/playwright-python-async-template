"""
Smart Locator wrapper with AI-powered healing capabilities.

Transparently wraps Playwright Locator objects to provide automatic
selector healing when elements cannot be found.
"""

import asyncio
import logging
from typing import Any, Optional

from playwright.async_api import Locator, Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from core.ui.ai.locator_healer import AILocatorHealer, get_healer
from utils.config import Config

from .retry_locator import RetryLocator

logger = logging.getLogger(__name__)


class SmartLocator:
    """
    Intelligent wrapper around Playwright Locator with AI healing.

    This class spoofs being a Playwright Locator to avoid JSON serialization issues
    when Playwright's internal code tries to serialize locator objects.

    When a locator operation times out (element not found), this class:
    1. Catches the TimeoutError
    2. Asks AILocatorHealer to suggest alternative selectors
    3. Retries the operation with the healed selector
    4. Falls back to original error if healing fails
    """

    def __init__(self, locator: Locator, selector: str, healer: AILocatorHealer, page: Page):
        """
        Initialize SmartLocator.

        Args:
            locator: Original Playwright Locator or SmartLocator (will be unwrapped)
            selector: Selector string used to create the locator
            healer: AILocatorHealer instance for healing attempts
            page: Playwright Page instance
        """
        # Unwrap if locator is already a SmartLocator (prevents nested wrapping)
        if isinstance(locator, SmartLocator):
            locator = locator._locator

        # Store our custom attributes
        object.__setattr__(self, "_locator", locator)
        object.__setattr__(self, "_selector_str", selector)  # Different name to avoid conflict
        object.__setattr__(self, "_healer", healer)
        object.__setattr__(self, "_healing_page", page)  # Different name to avoid conflict
        object.__setattr__(self, "_healed_selector", None)  # Track if this selector has been healed

    # ========== Class Spoofing (Make Playwright think we're a real Locator) ==========

    @property
    def __class__(self):
        """Spoof class identity to fool isinstance() and type() checks."""
        return Locator

    def __reduce_ex__(self, protocol):
        """When pickled/serialized, return the underlying Playwright Locator."""
        return (lambda x: x, (object.__getattribute__(self, "_locator"),))

    def __getstate__(self):
        """For pickle: return the underlying Locator's state."""
        locator = object.__getattribute__(self, "_locator")
        if hasattr(locator, "__getstate__"):
            return locator.__getstate__()
        return locator

    def __setstate__(self, state):
        """For pickle: restore from underlying Locator state."""
        locator = object.__getattribute__(self, "_locator")
        if hasattr(locator, "__setstate__"):
            locator.__setstate__(state)
        else:
            object.__setattr__(self, "_locator", state)

    def __getattribute__(self, name: str):
        """
        Intercept attribute access to delegate Playwright internals to wrapped locator.

        This ensures Playwright's internal code gets the real Locator's attributes,
        while our healing logic uses our custom attributes.
        """
        # Our custom attributes - return from SmartLocator
        if name in (
            "_locator",
            "_selector_str",
            "_healer",
            "_healing_page",
            "_healed_selector",
            "_heal_and_retry",
            "__class__",
            "__reduce_ex__",
            "__getstate__",
            "__setstate__",
            "__getattribute__",
            "__setattr__",
        ):
            return object.__getattribute__(self, name)

        # For Playwright's internal attributes (start with _), delegate to wrapped locator
        if name.startswith("_"):
            locator = object.__getattribute__(self, "_locator")
            return getattr(locator, name)

        # For public methods/properties, return from SmartLocator (these have healing)
        return object.__getattribute__(self, name)

    def __setattr__(self, name: str, value: Any):
        """Delegate attribute setting to wrapped locator for Playwright internals."""
        if name in ("_locator", "_selector_str", "_healer", "_healing_page", "_healed_selector"):
            object.__setattr__(self, name, value)
        else:
            # Delegate to wrapped locator
            locator = object.__getattribute__(self, "_locator")
            setattr(locator, name, value)

    # ========== Healing Logic ==========

    async def _heal_and_retry(self, operation_name: str, operation_func, *args, **kwargs) -> Any:
        """
        Core healing logic - try operation, heal if it fails, retry.

        Args:
            operation_name: Name of the operation (for logging)
            operation_func: The async function to call
            *args: Positional arguments for the operation
            **kwargs: Keyword arguments for the operation

        Returns:
            Result of the operation

        Raises:
            Original TimeoutError if healing fails
        """
        # Check if we already have a healed selector from a previous operation
        healed_selector = object.__getattribute__(self, "_healed_selector")

        if healed_selector:
            # Use the healed selector directly (skip the try-fail-heal cycle)
            logger.debug(
                f"[CACHED] Using previously healed selector: {healed_selector} for {operation_name}"
            )
            page = object.__getattribute__(self, "_healing_page")
            if hasattr(page, "_original_locator"):
                healed_locator = page._original_locator(healed_selector)
            else:
                from playwright.async_api import Page as PlaywrightPage

                healed_locator = PlaywrightPage.locator.__get__(page, type(page))(healed_selector)

            healed_operation = getattr(healed_locator, operation_name)
            return await healed_operation(*args, **kwargs)

        try:
            # Try original operation
            return await operation_func(*args, **kwargs)

        except PlaywrightTimeoutError as e:
            logger.warning(
                f"[WARN] Selector failed: {self._selector_str} (operation: {operation_name})"
            )

            # Attempt healing
            healed_selector = await self._healer.heal_selector(
                page=self._healing_page,
                failed_selector=self._selector_str,
                context=f"Operation: {operation_name}",
                error=str(e),
            )

            if healed_selector:
                # Healing successful - SAVE the healed selector for future operations
                object.__setattr__(self, "_healed_selector", healed_selector)
                logger.info(
                    f"[HEALING] Retrying {operation_name} with healed selector: {healed_selector}"
                )

                # IMPORTANT: Get the ORIGINAL page.locator (before monkey-patching)
                # to avoid creating another SmartLocator wrapper
                page = object.__getattribute__(self, "_healing_page")
                if hasattr(page, "_original_locator"):
                    # Use the stored original method
                    new_locator = page._original_locator(healed_selector)
                else:
                    # Fallback: import Playwright's Page and create locator directly
                    # This bypasses our monkey-patched version
                    from playwright.async_api import Page as PlaywrightPage

                    new_locator = PlaywrightPage.locator.__get__(page, type(page))(healed_selector)

                # Get the same operation from new locator
                new_operation = getattr(new_locator, operation_name)

                # Retry the operation
                result = await new_operation(*args, **kwargs)
                logger.info(
                    f"[SUCCESS] Successfully completed {operation_name} with healed selector: {healed_selector}"
                )
                return result
            else:
                # Healing failed - re-raise original error
                selector_str = object.__getattribute__(self, "_selector_str")
                logger.error(f"[FAIL] Healing failed for selector: {selector_str}")
                raise

    # ========== Interaction Methods ==========

    async def click(self, **kwargs):
        """Click the element."""
        return await self._heal_and_retry("click", self._locator.click, **kwargs)

    async def dblclick(self, **kwargs):
        """Double-click the element."""
        return await self._heal_and_retry("dblclick", self._locator.dblclick, **kwargs)

    async def fill(self, value: str, **kwargs):
        """Fill input with value."""
        return await self._heal_and_retry("fill", self._locator.fill, value, **kwargs)

    async def type(self, text: str, **kwargs):
        """Type text into element."""
        return await self._heal_and_retry("type", self._locator.type, text, **kwargs)

    async def press(self, key: str, **kwargs):
        """Press a key."""
        return await self._heal_and_retry("press", self._locator.press, key, **kwargs)

    async def hover(self, **kwargs):
        """Hover over the element."""
        return await self._heal_and_retry("hover", self._locator.hover, **kwargs)

    async def check(self, **kwargs):
        """Check a checkbox."""
        return await self._heal_and_retry("check", self._locator.check, **kwargs)

    async def uncheck(self, **kwargs):
        """Uncheck a checkbox."""
        return await self._heal_and_retry("uncheck", self._locator.uncheck, **kwargs)

    async def select_option(self, value=None, **kwargs):
        """Select option from dropdown."""
        return await self._heal_and_retry(
            "select_option", self._locator.select_option, value, **kwargs
        )

    async def focus(self, **kwargs):
        """Focus the element."""
        return await self._heal_and_retry("focus", self._locator.focus, **kwargs)

    async def blur(self, **kwargs):
        """Remove focus from element."""
        return await self._heal_and_retry("blur", self._locator.blur, **kwargs)

    # ========== State Checking Methods ==========

    async def is_visible(self, **kwargs) -> bool:
        """Check if element is visible."""
        return await self._heal_and_retry("is_visible", self._locator.is_visible, **kwargs)

    async def is_hidden(self, **kwargs) -> bool:
        """Check if element is hidden."""
        return await self._heal_and_retry("is_hidden", self._locator.is_hidden, **kwargs)

    async def is_enabled(self, **kwargs) -> bool:
        """Check if element is enabled."""
        return await self._heal_and_retry("is_enabled", self._locator.is_enabled, **kwargs)

    async def is_disabled(self, **kwargs) -> bool:
        """Check if element is disabled."""
        return await self._heal_and_retry("is_disabled", self._locator.is_disabled, **kwargs)

    async def is_checked(self, **kwargs) -> bool:
        """Check if checkbox is checked."""
        return await self._heal_and_retry("is_checked", self._locator.is_checked, **kwargs)

    # ========== Content Retrieval Methods ==========

    async def inner_text(self, **kwargs) -> str:
        """Get inner text of element."""
        return await self._heal_and_retry("inner_text", self._locator.inner_text, **kwargs)

    async def text_content(self, **kwargs) -> Optional[str]:
        """Get text content of element."""
        return await self._heal_and_retry("text_content", self._locator.text_content, **kwargs)

    async def get_attribute(self, name: str, **kwargs) -> Optional[str]:
        """Get attribute value."""
        return await self._heal_and_retry(
            "get_attribute", self._locator.get_attribute, name, **kwargs
        )

    async def input_value(self, **kwargs) -> str:
        """Get input value."""
        return await self._heal_and_retry("input_value", self._locator.input_value, **kwargs)

    async def evaluate(self, expression: str, arg=None, **kwargs):
        """
        Evaluate JavaScript expression on the element.

        Note: If arg is a SmartLocator, it will be automatically unwrapped.
        """
        # Unwrap SmartLocator if passed as argument
        if isinstance(arg, SmartLocator):
            arg = arg._locator

        return await self._heal_and_retry(
            "evaluate", self._locator.evaluate, expression, arg, **kwargs
        )

    async def evaluate_all(self, expression: str, arg=None):
        """
        Evaluate JavaScript expression on all matching elements.

        Note: If arg is a SmartLocator, it will be automatically unwrapped.
        """
        # Unwrap SmartLocator if passed as argument
        if isinstance(arg, SmartLocator):
            arg = arg._locator

        return await self._locator.evaluate_all(expression, arg)

    # ========== Advanced Methods ==========

    async def count(self) -> int:
        """Get count of matching elements."""
        return await self._locator.count()

    async def all(self):
        """
        Get all matching elements (returns list of SmartLocators).

        Note: This wraps each element in SmartLocator for consistency.
        """
        raw_locators = await self._locator.all()
        selector_str = object.__getattribute__(self, "_selector_str")
        healer = object.__getattribute__(self, "_healer")
        healing_page = object.__getattribute__(self, "_healing_page")
        return [
            SmartLocator(loc, f"{selector_str}[{i}]", healer, healing_page)
            for i, loc in enumerate(raw_locators)
        ]

    def first(self):
        """Get first matching element (returns new SmartLocator)."""
        first_locator = self._locator.first()
        selector_str = object.__getattribute__(self, "_selector_str")
        healer = object.__getattribute__(self, "_healer")
        healing_page = object.__getattribute__(self, "_healing_page")
        return SmartLocator(first_locator, f"{selector_str}.first()", healer, healing_page)

    def last(self):
        """Get last matching element (returns new SmartLocator)."""
        last_locator = self._locator.last()
        selector_str = object.__getattribute__(self, "_selector_str")
        healer = object.__getattribute__(self, "_healer")
        healing_page = object.__getattribute__(self, "_healing_page")
        return SmartLocator(last_locator, f"{selector_str}.last()", healer, healing_page)

    def nth(self, index: int):
        """Get nth matching element (returns new SmartLocator)."""
        nth_locator = self._locator.nth(index)
        selector_str = object.__getattribute__(self, "_selector_str")
        healer = object.__getattribute__(self, "_healer")
        healing_page = object.__getattribute__(self, "_healing_page")
        return SmartLocator(nth_locator, f"{selector_str}.nth({index})", healer, healing_page)

    # ========== Internal/Advanced - Access raw locator if needed ==========

    @property
    def unwrap(self):
        """
        Get the underlying Playwright Locator (for advanced use cases).

        Use this when you need to pass the locator to Playwright methods
        that don't accept SmartLocator (e.g., as arguments to other methods).

        Example:
            await element.evaluate("el => el.value", locator.unwrap)
        """
        return self._locator

    async def wait_for(self, **kwargs):
        """Wait for element to be present."""
        return await self._heal_and_retry("wait_for", self._locator.wait_for, **kwargs)

    async def screenshot(self, **kwargs):
        """Take screenshot of element."""
        return await self._heal_and_retry("screenshot", self._locator.screenshot, **kwargs)

    # ========== Filtering Methods (return new SmartLocator) ==========

    def filter(self, **kwargs):
        """Filter locator (returns new SmartLocator)."""
        filtered_locator = self._locator.filter(**kwargs)
        selector_str = object.__getattribute__(self, "_selector_str")
        healer = object.__getattribute__(self, "_healer")
        healing_page = object.__getattribute__(self, "_healing_page")
        return SmartLocator(
            filtered_locator, f"{selector_str}.filter({kwargs})", healer, healing_page
        )

    def locator(self, selector: str):
        """Create sub-locator (returns new SmartLocator)."""
        sub_locator = self._locator.locator(selector)
        selector_str = object.__getattribute__(self, "_selector_str")
        healer = object.__getattribute__(self, "_healer")
        healing_page = object.__getattribute__(self, "_healing_page")
        return SmartLocator(sub_locator, f"{selector_str} >> {selector}", healer, healing_page)

    # ========== Pass-through properties (for user convenience) ==========

    @property
    def page(self) -> Page:
        """Get the page object."""
        return object.__getattribute__(self, "_healing_page")

    @property
    def unwrap(self) -> Locator:
        """Get the underlying Playwright Locator (for direct access if needed)."""
        return object.__getattribute__(self, "_locator")

    # NOTE: _impl_obj, _frame, and other internal Playwright attributes
    # are automatically delegated via __getattribute__

    # ========== Dynamic method wrapping (fallback for any missing methods) ==========

    def __getattr__(self, name: str):
        """
        Dynamically wrap any Playwright Locator method not explicitly defined.

        This fallback ensures SmartLocator works with ALL Locator methods,
        even ones not manually wrapped above. When you call a method that
        doesn't exist on SmartLocator, Python calls this __getattr__.

        Args:
            name: Name of the attribute/method being accessed

        Returns:
            The wrapped method with AI healing, or the original attribute

        Example:
            # evaluate() is now defined, but if it wasn't:
            locator.evaluate("el => el.value")  # Calls __getattr__("evaluate")
            # → Returns wrapped version with healing
        """
        # Get the attribute from the wrapped locator
        original_attr = getattr(self._locator, name)

        # If it's not callable (property/value), return as-is
        if not callable(original_attr):
            return original_attr

        # If it's an async method, wrap it with healing
        if asyncio.iscoroutinefunction(original_attr):

            async def wrapped(*args, **kwargs):
                return await self._heal_and_retry(name, original_attr, *args, **kwargs)

            return wrapped

        # If it's a sync method (like filter, locator), return as-is
        # These are already manually wrapped above
        return original_attr

    # ========== Static method for page injection ==========

    @staticmethod
    def inject_into_page(page: Page) -> None:
        """
        Inject enhanced locator wrappers into a Playwright Page.

        This method monkey-patches page.locator() and all get_by_* methods
        to return wrapped Locator instances with the following layers:

        1. RetryLocator (if enabled) - Retries failed operations (cheap)
        2. SmartLocator (if enabled) - AI-powered healing (expensive)

        The retry layer prevents unnecessary AI calls for transient failures.

        Configuration (via .env):
            RETRY_ENABLED=true          # Enable retry wrapper
            RETRY_MAX_ATTEMPTS=3        # Max retries before AI healing
            RETRY_DELAY=1.0             # Delay between retries (seconds)
            AI_HEALING_ENABLED=true     # Enable AI healing wrapper

        Args:
            page: Playwright Page to enhance
        """
        # Get configuration
        retry_enabled = Config.get_retry_enabled()
        ai_enabled = Config.get_ai_healing_enabled()

        if not retry_enabled and not ai_enabled:
            logger.debug("No wrappers enabled, using plain Playwright locators")
            return

        # Get healer if AI is enabled
        healer = None
        if ai_enabled:
            healer = get_healer()
            if not healer.enabled:
                logger.warning("⚠️ AI healing is enabled in config but healer failed to initialize")
                ai_enabled = False

        # Log enabled wrappers
        enabled_wrappers = []
        if retry_enabled:
            enabled_wrappers.append(f"Retry({Config.get_retry_max_attempts()} attempts)")
        if ai_enabled:
            enabled_wrappers.append("AI Healing")

        logger.info(f"[WRAPPERS] Enhanced locators enabled: {' -> '.join(enabled_wrappers)}")

        # Store original methods
        original_locator = page.locator
        original_get_by_text = page.get_by_text
        original_get_by_label = page.get_by_label
        original_get_by_role = page.get_by_role
        original_get_by_test_id = page.get_by_test_id
        original_get_by_placeholder = page.get_by_placeholder
        original_get_by_alt_text = page.get_by_alt_text
        original_get_by_title = page.get_by_title

        # Store original locator method on page for healing to use
        page._original_locator = original_locator

        # Helper function to apply wrappers in correct order
        def apply_wrappers(base_locator, selector_str):
            """
            Apply wrappers in order: Retry (inner) → SmartLocator (outer)

            This ensures retries happen first (cheap), AI healing second (expensive).
            """
            wrapped = base_locator

            # Layer 1: Retry wrapper (inner layer - tries first)
            if retry_enabled:
                wrapped = RetryLocator(
                    wrapped,
                    max_retries=Config.get_retry_max_attempts(),
                    delay=Config.get_retry_delay(),
                    selector=selector_str,
                )

            # Layer 2: SmartLocator wrapper (outer layer - last resort)
            if ai_enabled:
                wrapped = SmartLocator(wrapped, selector_str, healer, page)

            return wrapped

        # Create enhanced versions that return wrapped locators
        def enhanced_locator(selector: str, **kwargs):
            base_locator = original_locator(selector, **kwargs)
            return apply_wrappers(base_locator, selector)

        def enhanced_get_by_text(text, **kwargs):
            base_locator = original_get_by_text(text, **kwargs)
            selector_str = f"get_by_text('{text}')"
            return apply_wrappers(base_locator, selector_str)

        def enhanced_get_by_label(text, **kwargs):
            base_locator = original_get_by_label(text, **kwargs)
            selector_str = f"get_by_label('{text}')"
            return apply_wrappers(base_locator, selector_str)

        def enhanced_get_by_role(role, **kwargs):
            base_locator = original_get_by_role(role, **kwargs)
            selector_str = f"get_by_role('{role}')"
            return apply_wrappers(base_locator, selector_str)

        def enhanced_get_by_test_id(test_id):
            base_locator = original_get_by_test_id(test_id)
            selector_str = f"get_by_test_id('{test_id}')"
            return apply_wrappers(base_locator, selector_str)

        def enhanced_get_by_placeholder(text, **kwargs):
            base_locator = original_get_by_placeholder(text, **kwargs)
            selector_str = f"get_by_placeholder('{text}')"
            return apply_wrappers(base_locator, selector_str)

        def enhanced_get_by_alt_text(text, **kwargs):
            base_locator = original_get_by_alt_text(text, **kwargs)
            selector_str = f"get_by_alt_text('{text}')"
            return apply_wrappers(base_locator, selector_str)

        def enhanced_get_by_title(text, **kwargs):
            base_locator = original_get_by_title(text, **kwargs)
            selector_str = f"get_by_title('{text}')"
            return apply_wrappers(base_locator, selector_str)

        # Monkey-patch the page object
        page.locator = enhanced_locator
        page.get_by_text = enhanced_get_by_text
        page.get_by_label = enhanced_get_by_label
        page.get_by_role = enhanced_get_by_role
        page.get_by_test_id = enhanced_get_by_test_id
        page.get_by_placeholder = enhanced_get_by_placeholder
        page.get_by_alt_text = enhanced_get_by_alt_text
        page.get_by_title = enhanced_get_by_title
