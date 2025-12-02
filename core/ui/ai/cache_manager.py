"""
Cache manager for storing and retrieving healed selectors.
"""

import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manages persistent cache of healed selectors.

    Stores successful healings to disk to avoid repeated AI calls
    for the same failed selectors.
    """

    def __init__(self, cache_file: str = ".selector_cache.json"):
        """
        Initialize cache manager.

        Args:
            cache_file: Path to cache file
        """
        self.cache_file = cache_file
        self.cache: Dict[str, str] = self._load_cache()

    def _load_cache(self) -> Dict[str, str]:
        """
        Load selector cache from file if it exists.

        Returns:
            Dictionary of failed_selector -> healed_selector mappings
        """
        try:
            with open(self.cache_file, "r") as f:
                cache = json.load(f)
                logger.info(f"[CACHE] Loaded {len(cache)} cached healings from {self.cache_file}")
                return cache
        except FileNotFoundError:
            logger.debug(f"[CACHE] No cache file found at {self.cache_file}, starting fresh")
            return {}
        except json.JSONDecodeError as e:
            logger.warning(f"[WARN] Cache file corrupted, starting fresh: {e}")
            return {}
        except Exception as e:
            logger.warning(f"[WARN] Failed to load cache: {e}")
            return {}

    def _save_cache(self):
        """
        Save selector cache to file.

        Raises:
            PermissionError: If cannot write to cache file
            OSError: If file system error occurs
            TypeError: If cache data is not JSON serializable
        """
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f, indent=2)
                logger.debug(f"[CACHE] Saved {len(self.cache)} healings to {self.cache_file}")
        except PermissionError as e:
            raise PermissionError(f"Permission denied writing cache file: {self.cache_file}") from e
        except OSError as e:
            raise OSError(f"OS error saving cache: {e}") from e
        except TypeError as e:
            raise TypeError(f"Invalid cache data (not JSON serializable): {e}") from e

    def get(self, failed_selector: str) -> Optional[str]:
        """
        Get healed selector from cache.

        Args:
            failed_selector: The selector that failed

        Returns:
            Healed selector if found in cache, None otherwise
        """
        return self.cache.get(failed_selector)

    def set(self, failed_selector: str, healed_selector: str):
        """
        Store healed selector in cache and persist to disk.

        Args:
            failed_selector: The selector that failed
            healed_selector: The working selector that replaced it
        """
        self.cache[failed_selector] = healed_selector
        self._save_cache()
        logger.debug(f"[CACHE] Cached healing: {failed_selector} -> {healed_selector}")

    def has(self, failed_selector: str) -> bool:
        """
        Check if selector exists in cache.

        Args:
            failed_selector: The selector to check

        Returns:
            True if selector is cached, False otherwise
        """
        return failed_selector in self.cache

    def size(self) -> int:
        """
        Get number of cached healings.

        Returns:
            Number of cached selector mappings
        """
        return len(self.cache)

    def clear(self):
        """Clear all cached healings and save empty cache to disk."""
        self.cache.clear()
        self._save_cache()
        logger.info("🗑️ Cache cleared")
