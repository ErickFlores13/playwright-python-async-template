"""
Visual extraction strategy using screenshots and visual context.

This strategy captures a screenshot of the page and provides it to the AI
for visual analysis. This is a LAST RESORT option as it:
- Costs more (vision models are expensive)
- Takes longer (screenshot + upload + analysis)
- May have privacy concerns (sends full page screenshot)

Only enable via VISUAL_EXTRACTION_ENABLED=true when other strategies fail.
"""

import base64
import logging
from typing import Any, Dict

from playwright.async_api import Page

from core.ui.ai.extraction.base_strategy import ExtractionStrategy

logger = logging.getLogger(__name__)


class VisualStrategy(ExtractionStrategy):
    """
    Extracts visual context via screenshot for AI vision models.

    Use this as a last resort when:
    - HTML structure is too complex/obfuscated
    - Element identification requires visual context
    - Other strategies consistently fail

    Costs:
    - Screenshot capture: ~100-500ms
    - Image upload: ~500ms-2s (depends on size)
    - Vision model: ~$0.01-0.05 per request (much higher than text-only)

    Configuration:
        VISUAL_EXTRACTION_ENABLED=true  # Must explicitly enable
        VISUAL_SCREENSHOT_FULL_PAGE=false  # Full page vs viewport only
        VISUAL_MAX_WIDTH=1920  # Max screenshot width (for cost control)
        VISUAL_MAX_HEIGHT=1080  # Max screenshot height
    """

    def __init__(self, full_page: bool = False, max_width: int = 1920, max_height: int = 1080):
        """
        Initialize visual extraction strategy.

        Args:
            full_page: Capture full scrollable page vs viewport only
            max_width: Maximum screenshot width (larger = more expensive)
            max_height: Maximum screenshot height
        """
        self.full_page = full_page
        self.max_width = max_width
        self.max_height = max_height

    async def extract(self, page: Page, failed_selector: str) -> Dict[str, Any]:
        """
        Capture screenshot and return visual context with base64 image.

        Args:
            page: Playwright Page instance
            failed_selector: The selector that failed

        Returns:
            Dictionary containing:
                - screenshot_b64: Base64 encoded PNG screenshot
                - viewport_size: Current viewport dimensions
                - failed_selector: The selector that failed
                - page_url: Current page URL
                - page_title: Current page title
        """
        logger.info(f"📸 Capturing screenshot for visual analysis (full_page={self.full_page})")

        try:
            # Get page metadata
            page_url = page.url
            page_title = await page.title()

            # Get viewport size
            viewport = page.viewport_size
            if viewport:
                viewport_info = f"{viewport['width']}x{viewport['height']}"
            else:
                viewport_info = "unknown"

            # Capture screenshot
            screenshot_bytes = await page.screenshot(full_page=self.full_page, type="png")

            # Convert to base64 for API transmission
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")

            # Calculate approximate size
            size_kb = len(screenshot_bytes) / 1024
            logger.info(f"📸 Screenshot captured: {size_kb:.1f}KB, viewport={viewport_info}")

            # Warn if large (expensive)
            if size_kb > 500:
                logger.warning(
                    f"⚠️ Large screenshot ({size_kb:.1f}KB) may increase costs significantly. "
                    f"Consider using viewport-only or reducing max dimensions."
                )

            return {
                "screenshot_b64": screenshot_b64,
                "viewport_size": viewport_info,
                "failed_selector": failed_selector,
                "page_url": page_url,
                "page_title": page_title,
                "full_page": self.full_page,
                "size_kb": round(size_kb, 1),
            }

        except Exception as e:
            logger.error(f"[ERROR] Failed to capture screenshot: {e}")
            raise RuntimeError(f"Visual extraction failed: {e}") from e

    def get_name(self) -> str:
        """Get strategy name for logging/metrics."""
        return "visual"

    def format_for_ai(self, visual_data: Dict[str, Any]) -> str:
        """
        Format visual data for AI prompt (metadata only, image sent separately).

        Args:
            visual_data: Dictionary from extract() method

        Returns:
            Formatted text description for AI prompt
        """
        return f"""
VISUAL CONTEXT (Screenshot Analysis):
=====================================
Page URL: {visual_data['page_url']}
Page Title: {visual_data['page_title']}
Viewport Size: {visual_data['viewport_size']}
Screenshot Type: {'Full Page' if visual_data['full_page'] else 'Viewport Only'}
Screenshot Size: {visual_data['size_kb']}KB

Failed Selector: {visual_data['failed_selector']}

Please analyze the provided screenshot to:
1. Locate the element that the failed selector was trying to target
2. Identify visual characteristics (color, size, position, text content)
3. Suggest a reliable selector based on visual context
4. Consider accessibility attributes (aria-label, role, etc.)

The screenshot is attached as a base64-encoded PNG image.
"""


def supports_vision_model(model_name: str) -> bool:
    """
    Check if the configured AI model supports vision/image inputs.

    Args:
        model_name: Name of the AI model

    Returns:
        True if model supports vision, False otherwise
    """
    # Common vision-capable models
    vision_models = [
        "gpt-4-vision",
        "gpt-4o",
        "gpt-4-turbo",
        "claude-3-opus",
        "claude-3-sonnet",
        "claude-3-haiku",
        "gemini-pro-vision",
        "gemini-1.5-pro",
    ]

    model_lower = model_name.lower()
    return any(vision_model in model_lower for vision_model in vision_models)
