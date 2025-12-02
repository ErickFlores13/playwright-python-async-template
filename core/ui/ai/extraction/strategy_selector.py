"""
Strategy selector - intelligently chooses and executes extraction strategies.
"""

import logging
import os
from typing import Optional

from playwright.async_api import Page

from .base_strategy import ExtractionStrategy
from .form_context_strategy import FormContextStrategy
from .same_type_strategy import SameTypeStrategy
from .visual_strategy import VisualStrategy, supports_vision_model

logger = logging.getLogger(__name__)


class StrategySelector:
    """
    Selects and executes the best extraction strategy using cascading fallback.

    Strategy order:
    1. SameTypeStrategy (fast, cheap, works for simple typos)
    2. FormContextStrategy (more context, better for form changes)
    3. VisualStrategy (last resort, expensive, requires vision model)

    Visual strategy only enabled if:
        - VISUAL_EXTRACTION_ENABLED=true
        - AI model supports vision (gpt-4o, claude-3, etc.)
    """

    def __init__(self):
        self.strategies = [SameTypeStrategy(), FormContextStrategy()]

        # Add visual strategy if enabled and model supports it
        visual_enabled = os.getenv("VISUAL_EXTRACTION_ENABLED", "false").lower() == "true"
        ai_model = os.getenv("AI_MODEL", "gpt-4o")

        if visual_enabled:
            if supports_vision_model(ai_model):
                full_page = os.getenv("VISUAL_SCREENSHOT_FULL_PAGE", "false").lower() == "true"
                max_width = int(os.getenv("VISUAL_MAX_WIDTH", "1920"))
                max_height = int(os.getenv("VISUAL_MAX_HEIGHT", "1080"))

                self.strategies.append(
                    VisualStrategy(full_page=full_page, max_width=max_width, max_height=max_height)
                )
                logger.info(f"📸 Visual extraction enabled with {ai_model} (full_page={full_page})")
            else:
                logger.warning(
                    f"⚠️ VISUAL_EXTRACTION_ENABLED=true but model '{ai_model}' doesn't support vision. "
                    f"Use gpt-4o, claude-3-*, or gemini-1.5-pro for visual extraction."
                )

        self.current_strategy_name = None

    async def extract(self, page: Page, failed_selector: str) -> tuple[str, str]:
        """
        Extract elements using the best available strategy.

        Tries strategies in order until one succeeds:
        1. SameTypeStrategy - Fast extraction of same element type
        2. FormContextStrategy - Contextual form-based extraction
        3. VisualStrategy - Screenshot-based visual analysis (if enabled)

        Args:
            page: Playwright Page instance
            failed_selector: The selector that failed

        Returns:
            Tuple of (extracted_elements_str, strategy_name_used)
        """
        last_error = None

        for strategy in self.strategies:
            try:
                logger.debug(f"🔍 Trying extraction strategy: {strategy.get_name()}")
                elements = await strategy.extract(page, failed_selector)

                # Check if we got useful data
                if elements and len(elements) > 50:  # Meaningful content threshold
                    self.current_strategy_name = strategy.get_name()
                    logger.debug(f"[SUCCESS] Successfully extracted using: {strategy.get_name()}")
                    return elements, strategy.get_name()
                else:
                    logger.debug(
                        f"[WARN] {strategy.get_name()} returned insufficient data, trying next strategy"
                    )

            except Exception as e:
                logger.warning(f"[WARN] Strategy {strategy.get_name()} failed: {e}")
                last_error = e
                continue

        # All strategies failed
        error_msg = f"All extraction strategies failed. Last error: {last_error}"
        logger.error(f"[ERROR] {error_msg}")

        # Return minimal fallback
        return "Could not extract meaningful elements from page", "none"

    def get_current_strategy_name(self) -> Optional[str]:
        """
        Get the name of the last successful strategy.

        Returns:
            Strategy name or None if no strategy has been used yet
        """
        return self.current_strategy_name
