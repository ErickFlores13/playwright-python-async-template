"""
Debug mode browser strategy.

Optimized for debugging test failures with slow motion and devtools.

Author: Erick Guadalupe Félix Flores
License: MIT
"""
from typing import Dict, Any
from core.ui.browser.strategies.browser_strategy import BrowserStrategy
from utils.config import Config


class DebugStrategy(BrowserStrategy):
    """
    Browser configuration strategy for debugging.
    
    Features:
    - Uses browser type from config
    - Always visible (headless=false)
    - Slow motion enabled (500ms) for observing actions
    - DevTools automatically opened
    - Window maximized for better visibility
    """
    
    def get_browser_type(self) -> str:
        """Get browser type from configuration."""
        return Config.get_browser_type()
    
    def get_launch_options(self) -> Dict[str, Any]:
        """
        Get launch options for debug mode.
        
        Returns:
            dict: Browser launch options with:
                - headless: Always false
                - slow_mo: 500ms for observing each action
                - devtools: Auto-open DevTools
                - args: Start maximized
        """
        options = {
            "headless": False,
            "slow_mo": 500,  # 500ms delay between actions
            "devtools": True,  # Auto-open DevTools
        }
        
        # Chromium-specific: start maximized
        if self.get_browser_type() == "chromium":
            options["args"] = ["--start-maximized", "--auto-open-devtools-for-tabs"]
        
        return options
    
    def get_context_options(self) -> Dict[str, Any]:
        """
        Get context options for debug mode.
        
        Returns:
            dict: Browser context options with:
                - viewport: From config for realistic debugging
                - locale: From config
                - user_agent: From config if set
        """
        viewport = Config.get_viewport_size()
        options = {
            "viewport": viewport,
            "locale": Config.get_browser_locale(),
        }
        
        # Add user agent if configured
        user_agent = Config.get_user_agent()
        if user_agent:
            options["user_agent"] = user_agent
        
        return options
