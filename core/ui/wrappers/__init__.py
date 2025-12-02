"""
Locator wrappers for enhanced functionality.

Wrappers add behaviors to Playwright Locator objects:
- RetryLocator: Simple retry for transient failures
- SmartLocator: AI-powered selector healing
"""

from .retry_locator import RetryLocator
from .smart_locator import SmartLocator

__all__ = ["RetryLocator", "SmartLocator"]
