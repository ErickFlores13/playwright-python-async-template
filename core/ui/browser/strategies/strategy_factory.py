"""
Factory for selecting browser configuration strategy.

Selects the appropriate strategy based on environment variables.

Author: Erick Guadalupe Félix Flores
License: MIT
"""
import os
import logging
from core.ui.browser.strategies.browser_strategy import BrowserStrategy
from core.ui.browser.strategies.local_strategy import LocalStrategy
from core.ui.browser.strategies.ci_strategy import CIStrategy
from core.ui.browser.strategies.debug_strategy import DebugStrategy
from utils.config import Config

logger = logging.getLogger(__name__)


def get_browser_strategy() -> BrowserStrategy:
    """
    Factory function to select browser strategy based on environment.
    
    Selection logic:
    1. If CI=true → CIStrategy (optimized for CI/CD)
    2. If TEST_MODE=debug → DebugStrategy (slow motion, devtools)
    3. Otherwise → LocalStrategy (default for local development)
    
    Returns:
        BrowserStrategy: Selected strategy instance
    
    Environment Variables:
        CI: Set to 'true' to use CI strategy
        TEST_MODE: Set to 'debug' for debug strategy
    
    Examples:
        >>> # Local development (default)
        >>> pytest
        
        >>> # CI environment
        >>> CI=true pytest
        
        >>> # Debug mode
        >>> TEST_MODE=debug pytest
    """
    # Check if running in CI
    if Config.is_ci_environment():
        logger.info("Using CIStrategy (CI environment detected)")
        return CIStrategy()
    
    # Check test mode
    test_mode = os.getenv('TEST_MODE', 'local').lower()
    
    if test_mode == 'debug':
        logger.info("Using DebugStrategy (TEST_MODE=debug)")
        return DebugStrategy()
    
    # Default to local strategy
    logger.info("Using LocalStrategy (default)")
    return LocalStrategy()
