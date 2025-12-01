"""
Abstract base class for browser configuration strategies.

Author: Erick Guadalupe Félix Flores
License: MIT
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BrowserStrategy(ABC):
    """
    Abstract base class for browser configuration strategies.
    
    Each strategy defines how the browser should be launched and configured
    based on the testing environment (local development, CI, debug, etc.).
    """
    
    @abstractmethod
    def get_browser_type(self) -> str:
        """
        Get the browser type to use.
        
        Returns:
            str: Browser type ('chromium', 'firefox', or 'webkit')
        """
        pass
    
    @abstractmethod
    def get_launch_options(self) -> Dict[str, Any]:
        """
        Get browser launch options.
        
        Returns:
            dict: Options to pass to browser.launch()
                  (e.g., headless, args, slow_mo, devtools)
        """
        pass
    
    @abstractmethod
    def get_context_options(self) -> Dict[str, Any]:
        """
        Get browser context options.
        
        Returns:
            dict: Options to pass to browser.new_context()
                  (e.g., viewport, locale, record_video_dir, user_agent)
        """
        pass
