"""
Configuration management module for the Playwright Python Async Template.

This module provides a centralized configuration class that loads settings
from environment variables and provides sensible defaults for test execution.

Author: Erick Guadalupe Félix Flores
License: MIT
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)


class Config:
    """
    Centralized configuration management for the test framework.
    
    This class provides a single source of truth for all configuration values,
    with sensible defaults and easy customization via environment variables.
    """
    
    # ========== Application Settings ==========
    @staticmethod
    def get_base_url() -> str:
        """Get the base URL for the application under test."""
        return os.getenv('BASE_URL', 'http://localhost:8000')
    
    @staticmethod
    def get_test_username() -> str:
        """Get the test username."""
        return os.getenv('TEST_USERNAME', 'test_user')
    
    @staticmethod
    def get_test_password() -> str:
        """Get the test password."""
        return os.getenv('TEST_PASSWORD', 'test_password')
    
    # ========== Database Settings ==========
    @staticmethod
    def is_db_testing_enabled() -> bool:
        """Check if database testing is enabled."""
        return os.getenv('DB_TEST', 'false').lower() == 'true'
    
    @staticmethod
    def get_db_type() -> str:
        """Get database type (postgresql, mysql, mssql, oracle)."""
        return os.getenv('DB_TYPE', 'postgresql')
    
    @staticmethod
    def get_db_host() -> str:
        """Get database host."""
        return os.getenv('DB_HOST', 'localhost')
    
    @staticmethod
    def get_db_port() -> str:
        """Get database port."""
        return os.getenv('DB_PORT', '5432')
    
    @staticmethod
    def get_db_name() -> str:
        """Get database name."""
        return os.getenv('DB_NAME', 'testdb')
    
    @staticmethod
    def get_db_user() -> str:
        """Get database username."""
        return os.getenv('DB_USER', 'postgres')
    
    @staticmethod
    def get_db_password() -> str:
        """Get database password."""
        return os.getenv('DB_PASSWORD', 'password')
    
    # ========== Redis Settings ==========
    @staticmethod
    def get_redis_config() -> Dict[str, Any]:
        """
        Get Redis configuration.
        
        Returns:
            Dictionary with Redis connection parameters
        """
        try:
            redis_db = int(os.getenv('REDIS_DB', '0'))
        except ValueError:
            redis_db = 0  # Default to 0 if invalid value
            
        return {
            'host': os.getenv('REDIS_HOST', 'localhost'),
            'port': os.getenv('REDIS_PORT', '6379'),
            'db': redis_db
        }
    
    # ========== Browser Settings ==========
    @staticmethod
    def get_browser_type() -> str:
        """Get the browser type (chromium, firefox, webkit)."""
        return os.getenv('BROWSER', 'chromium')
    
    @staticmethod
    def is_headless() -> bool:
        """Check if browser should run in headless mode."""
        return os.getenv('HEADLESS', 'true').lower() == 'true'
    
    @staticmethod
    def get_viewport_size() -> Dict[str, int]:
        """
        Get browser viewport size.
        
        Returns:
            Dictionary with width and height
        """
        return {
            'width': int(os.getenv('VIEWPORT_WIDTH', '1920')),
            'height': int(os.getenv('VIEWPORT_HEIGHT', '1080'))
        }
    
    @staticmethod
    def get_browser_locale() -> str:
        """Get browser locale."""
        return os.getenv('BROWSER_LOCALE', 'en-US')
    
    @staticmethod
    def get_user_agent() -> str:
        """Get custom user agent string."""
        default_ua = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
        return os.getenv('USER_AGENT', default_ua)
    
    # ========== Test Execution Settings ==========
    @staticmethod
    def get_test_timeout() -> int:
        """Get test timeout in milliseconds."""
        return int(os.getenv('TIMEOUT', '30000'))
    
    @staticmethod
    def get_pytest_workers() -> str:
        """Get number of pytest workers for parallel execution."""
        return os.getenv('PYTEST_WORKERS', 'auto')
    
    @staticmethod
    def should_screenshot_on_failure() -> bool:
        """Check if screenshots should be taken on test failure."""
        return os.getenv('SCREENSHOT_ON_FAILURE', 'true').lower() == 'true'
    
    # ========== Reporting Settings ==========
    @staticmethod
    def get_screenshots_dir() -> str:
        """Get screenshots directory path."""
        return os.getenv('SCREENSHOTS_DIR', 'screenshots')
    
    @staticmethod
    def get_discord_webhook_url() -> Optional[str]:
        """Get Discord webhook URL for notifications."""
        return os.getenv('DISCORD_WEBHOOK_URL')
    
    # ========== Helper Methods ==========
    @staticmethod
    def get_all_config() -> Dict[str, Any]:
        """
        Get all configuration as a dictionary.
        
        Useful for debugging and logging configuration state.
        
        Returns:
            Dictionary with all configuration values
        """
        return {
            'base_url': Config.get_base_url(),
            'test_username': Config.get_test_username(),
            'db_testing_enabled': Config.is_db_testing_enabled(),
            'db_type': Config.get_db_type(),
            'db_host': Config.get_db_host(),
            'browser_type': Config.get_browser_type(),
            'headless': Config.is_headless(),
            'viewport': Config.get_viewport_size(),
            'locale': Config.get_browser_locale(),
            'test_timeout': Config.get_test_timeout(),
            'pytest_workers': Config.get_pytest_workers(),
            'screenshots_dir': Config.get_screenshots_dir(),
        }
    
    @staticmethod
    def validate_required_config() -> bool:
        """
        Validate that required configuration is present.
        
        Returns:
            True if all required config is present, raises ValueError otherwise
            
        Raises:
            ValueError: If required configuration is missing
        """
        required = {
            'BASE_URL': Config.get_base_url(),
        }
        
        missing = [key for key, value in required.items() if not value]
        
        if missing:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing)}. "
                f"Please check your .env file or environment variables."
            )
        
        return True


# Singleton instance for easy access
config = Config()