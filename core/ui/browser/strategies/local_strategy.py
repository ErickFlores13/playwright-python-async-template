"""
Local development browser strategy.

Optimized for local development with visual debugging.

Author: Erick Guadalupe Félix Flores
License: MIT
"""
from typing import Dict, Any
from core.ui.browser.strategies.browser_strategy import BrowserStrategy
from utils.config import Config


class LocalStrategy(BrowserStrategy):
    """
    Browser configuration strategy for local development.
    
    Features:
    - Uses browser type from config (chromium/firefox/webkit)
    - Headless mode from config (default: false for visual debugging)
    - Window maximized for better visibility
    - Slight slow motion if DEBUG mode enabled
    - Browser locale from config
    """
    
    def get_browser_type(self) -> str:
        """Get browser type from configuration."""
        return Config.get_browser_type()
    
    def get_launch_options(self) -> Dict[str, Any]:
        """
        Get launch options for local development.
        
        Returns:
            dict: Browser launch options with:
                - headless: From config (default: false)
                - slow_mo: 50ms if DEBUG=true, else 0
                - args: Start maximized for better visibility
        """
        options = {
            "headless": Config.is_headless(),
            "slow_mo": 50 if Config.is_debug() else 0,
        }
        
        # Chromium-specific: start maximized
        if self.get_browser_type() == "chromium":
            options["args"] = ["--start-maximized"]
        
        return options
    
    def get_context_options(self) -> Dict[str, Any]:
        """
        Get context options for local development.
        
        Returns:
            dict: Browser context options with:
                - viewport: From config (default: 1920x1080)
                - locale: From config (default: en-US)
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
