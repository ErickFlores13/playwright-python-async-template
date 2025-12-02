"""
CI/CD pipeline browser strategy.

Optimized for continuous integration environments.

Author: Erick Guadalupe Félix Flores
License: MIT
"""
from typing import Dict, Any
from core.ui.browser.strategies.browser_strategy import BrowserStrategy
from utils.config import Config


class CIStrategy(BrowserStrategy):
    """
    Browser configuration strategy for CI/CD pipelines.
    
    Features:
    - Always uses chromium (most stable for CI)
    - Always headless (no display in CI)
    - Video recording enabled for debugging failures
    - Optimized args for containerized environments
    - Fixed viewport for consistency
    """
    
    def get_browser_type(self) -> str:
        """Always use chromium in CI for stability."""
        return "chromium"
    
    def get_launch_options(self) -> Dict[str, Any]:
        """
        Get launch options optimized for CI/CD.
        
        Returns:
            dict: Browser launch options with:
                - headless: Always true
                - args: Optimized for Docker/containerized environments
                    --no-sandbox: Required in most CI containers
                    --disable-dev-shm-usage: Prevents shared memory issues
                    --disable-gpu: Not needed in headless
                    --disable-software-rasterizer: Performance optimization
        """
        return {
            "headless": True,
            "args": [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-software-rasterizer",
                "--disable-blink-features=AutomationControlled"
            ]
        }
    
    def get_context_options(self) -> Dict[str, Any]:
        """
        Get context options for CI environment.
        
        Returns:
            dict: Browser context options with:
                - viewport: Fixed 1920x1080 for consistency
                - locale: From config
                - record_video_dir: Enable video recording for failure debugging
                - record_video_size: Match viewport for clarity
        """
        options = {
            "viewport": {"width": 1920, "height": 1080},
            "locale": Config.get_browser_locale(),
        }
        
        # Enable video recording in CI
        screenshots_dir = Config.get_screenshots_dir()
        options["record_video_dir"] = f"{screenshots_dir}/videos"
        options["record_video_size"] = {"width": 1920, "height": 1080}
        
        return options
