"""
AI-powered selector healing service.

Automatically suggests and applies alternative selectors when original ones fail,
reducing maintenance burden and improving test stability.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from utils.config import Config

from .cache_manager import CacheManager
from .extraction import StrategySelector
from .metrics_tracker import MetricsTracker

logger = logging.getLogger(__name__)

# Singleton instance
_healer_instance: Optional["AILocatorHealer"] = None


def get_healer() -> "AILocatorHealer":
    """
    Get or create the singleton AILocatorHealer instance.

    This ensures all code shares the same healer instance and cache,
    preventing cache fragmentation across multiple instances.

    Returns:
        Singleton AILocatorHealer instance
    """
    global _healer_instance
    if _healer_instance is None:
        _healer_instance = AILocatorHealer()
    return _healer_instance


class AILocatorHealer:
    """
    Intelligent selector healing using AI.

    Orchestrates the healing process by:
    1. Checking cache for previous healings
    2. Extracting relevant page elements (via StrategySelector)
    3. Getting AI suggestions for alternative selectors
    4. Validating suggestions against the page
    5. Caching successful healings
    6. Tracking metrics and generating reports
    """

    def __init__(self):
        # Initialize modular components
        self.cache_manager = CacheManager(".selector_cache.json")
        self.metrics_tracker = MetricsTracker()
        self.strategy_selector = StrategySelector()

        # AI configuration
        self.enabled = Config.get_ai_healing_enabled()
        self.confidence_threshold = Config.get_ai_confidence_threshold()

        if self.enabled:
            self._init_ai_client()

    def _init_ai_client(self):
        """Initialize AI client (OpenAI, Claude, etc.)."""
        try:
            from openai import AsyncOpenAI

            api_key = Config.get_openai_api_key()

            if not api_key:
                logger.warning("⚠️ OpenAI API key not configured. AI healing disabled.")
                self.enabled = False
                return

            self.ai_client = AsyncOpenAI(api_key=api_key)
            logger.info("✅ AI Locator Healer initialized")

        except ImportError as e:
            logger.warning(
                f"[WARN] OpenAI package not installed. AI healing disabled. Install with: pip install openai"
            )
            self.enabled = False
        except ValueError as e:
            raise ValueError(f"Invalid OpenAI API key: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to initialize AI client: {type(e).__name__}: {e}") from e

    async def heal_selector(
        self, page: Page, failed_selector: str, context: str = "", error: str = ""
    ) -> Optional[str]:
        """
        Attempt to heal a failed selector using AI.

        Args:
            page: Playwright Page instance
            failed_selector: The selector that failed
            context: Optional context about what element we're looking for
            error: The error message that occurred

        Returns:
            Healed selector string or None if healing failed
        """
        if not self.enabled:
            return None

        # Track attempt
        self.metrics_tracker.record_attempt()

        # Check cache first
        if self.cache_manager.has(failed_selector):
            cached = self.cache_manager.get(failed_selector)
            self.metrics_tracker.record_cache_hit()
            logger.info(f"[CACHE HIT] Using cached healed selector: {failed_selector} -> {cached}")
            return cached

        try:
            # Get page context
            page_url = page.url

            # Extract relevant elements using strategy selector
            relevant_elements, strategy_used = await self.strategy_selector.extract(
                page, failed_selector
            )
            self.metrics_tracker.record_strategy_usage(strategy_used)

            # AI suggestion
            suggestions = await self._get_ai_suggestions(
                failed_selector=failed_selector,
                relevant_elements=relevant_elements,
                page_url=page_url,
                context=context,
                error=error,
            )

            # Validate suggestions against actual page
            for suggestion in suggestions:
                selector = suggestion["selector"]
                confidence = suggestion.get("confidence", 0)

                logger.debug(f"🔍 Testing suggestion: {selector} (confidence: {confidence:.0%})")

                # Try the suggested selector
                locator = page.locator(selector)
                count = await locator.count()

                logger.debug(f"   Found {count} elements")

                if count > 0:
                    # Found working selector
                    self.metrics_tracker.record_success()
                    logger.info(
                        f"✅ Healed selector (confidence: {confidence:.0%}): "
                        f"{failed_selector} → {selector}"
                    )

                    # Cache it
                    self.cache_manager.set(failed_selector, selector)

                    # Log for review
                    self.metrics_tracker.log_healing(
                        original=failed_selector,
                        healed=selector,
                        confidence=confidence,
                        page_url=page_url,
                        auto_applied=confidence >= self.confidence_threshold,
                        strategy_used=strategy_used,
                    )

                    return selector

            # No working selector found
            self.metrics_tracker.record_failure()
            logger.warning(f"[FAIL] Could not heal selector: {failed_selector}")
            logger.warning(
                f"   Tried {len(suggestions)} AI suggestions, none matched elements on page"
            )
            return None

        except PlaywrightTimeoutError as e:
            self.metrics_tracker.record_failure()
            raise PlaywrightTimeoutError(f"Timeout while testing healed selectors: {e}") from e
        except PlaywrightError as e:
            self.metrics_tracker.record_failure()
            raise PlaywrightError(f"Playwright error during healing: {e}") from e
        except json.JSONDecodeError as e:
            self.metrics_tracker.record_failure()
            raise json.JSONDecodeError(
                f"Failed to parse AI response as JSON: {e.msg}", e.doc, e.pos
            ) from e
        except Exception as e:
            self.metrics_tracker.record_failure()
            logger.error(f"Unexpected error during healing: {type(e).__name__}: {e}", exc_info=True)
            raise RuntimeError(f"Unexpected error during healing: {type(e).__name__}: {e}") from e

    async def _get_ai_suggestions(
        self,
        failed_selector: str,
        relevant_elements,  # Can be str (text extraction) or dict (visual extraction)
        page_url: str,
        context: str,
        error: str,
    ) -> List[Dict[str, Any]]:
        """
        Get AI-powered selector suggestions.

        Handles both text-based extraction (str) and visual extraction (dict with screenshot).

        Returns list of suggestions sorted by confidence.
        """
        # Check if visual extraction was used (returns dict instead of str)
        is_visual = isinstance(relevant_elements, dict) and "screenshot_b64" in relevant_elements

        if is_visual:
            # Visual strategy - use vision model
            from core.ui.ai.extraction.visual_strategy import VisualStrategy

            visual_strategy = VisualStrategy()

            prompt_text = visual_strategy.format_for_ai(relevant_elements)

            # Build messages with image for vision model
            messages = [
                {
                    "role": "system",
                    "content": "You are a Playwright test automation expert with vision capabilities.",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{relevant_elements['screenshot_b64']}"
                            },
                        },
                    ],
                },
            ]

            logger.info(
                f"📸 Using vision model for screenshot analysis ({relevant_elements['size_kb']}KB)"
            )
            cost = 0.01  # Visual models cost more

        else:
            # Text-based extraction - standard prompt
            prompt = f"""You are a Playwright selector expert. A test selector has failed.

FAILED SELECTOR: {failed_selector}
ERROR: {error}
CONTEXT: {context if context else "Not provided"}
PAGE URL: {page_url}

AVAILABLE ELEMENTS ON PAGE:
{relevant_elements}

TASK: Analyze the available elements and suggest 3 alternative selectors that might work.

Consider:
1. **Name/ID similarity**: Look for elements with similar names (e.g., if looking for 'porc_rasasdaojo', suggest 'porc_rojo')
2. **Pattern matching**: Match partial names, similar attributes, or semantic meaning
3. **Stable attributes**: Prefer data-testid, name, id over classes
4. **Position/context**: Consider form context, nearby elements

Return ONLY valid JSON (no markdown):
[
  {{
    "selector": "input[name='porc_rojo']",
    "confidence": 0.95,
    "reason": "Name attribute 'porc_rojo' is very similar to 'porc_rasasdaojo' - likely a typo"
  }},
  {{
    "selector": "input[data-testid='percentage-input']",
    "confidence": 0.85,
    "reason": "Data attribute found with semantic meaning matching the field"
  }},
  {{
    "selector": "form input[type='text']:nth-child(3)",
    "confidence": 0.60,
    "reason": "Positional fallback based on form structure"
  }}
]"""

            messages = [
                {"role": "system", "content": "You are a Playwright test automation expert."},
                {"role": "user", "content": prompt},
            ]
            cost = 0.0003  # Text-based models are cheap

        try:
            self.metrics_tracker.record_ai_call(cost=cost)

            response = await self.ai_client.chat.completions.create(
                model="gpt-4o-mini",  # Fast and cheap model (supports vision too)
                messages=messages,
                temperature=0.3,  # Low temperature for consistent results
                max_tokens=500,
            )

            content = response.choices[0].message.content.strip()

            # Log the raw AI response for debugging
            logger.debug(f"[AI] AI Response for '{failed_selector}':\n{content}")

            # Parse JSON response
            # Handle markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            suggestions = json.loads(content)

            # Validate suggestions structure
            if not isinstance(suggestions, list):
                logger.error(
                    f"[ERROR] AI returned invalid format (expected list, got {type(suggestions).__name__})"
                )
                return []

            # Log parsed suggestions
            logger.debug(f"📋 Parsed {len(suggestions)} suggestions: {suggestions}")

            # Sort by confidence
            suggestions.sort(key=lambda x: x.get("confidence", 0), reverse=True)

            return suggestions

        except ImportError as e:
            raise ImportError(
                "OpenAI package not available. Install with: pip install openai"
            ) from e
        except AttributeError as e:
            raise AttributeError(f"AI client not properly initialized: {e}") from e
        except json.JSONDecodeError as e:
            logger.debug(f"Raw AI response: {content if 'content' in locals() else 'N/A'}")
            raise json.JSONDecodeError(
                f"AI response was not valid JSON: {e.msg}", e.doc, e.pos
            ) from e
        except KeyError as e:
            raise KeyError(f"Unexpected AI response structure (missing key: {e})") from e
        except Exception as e:
            # Catch OpenAI-specific errors (RateLimitError, APIError, etc.)
            error_type = type(e).__name__
            if "RateLimitError" in error_type:
                raise RuntimeError(
                    "OpenAI rate limit exceeded. Consider implementing retry logic or upgrading API plan."
                ) from e
            elif "APIError" in error_type or "APIConnectionError" in error_type:
                raise RuntimeError(f"OpenAI API error: {e}") from e
            elif "AuthenticationError" in error_type:
                raise RuntimeError("OpenAI authentication failed. Check API key.") from e
            else:
                raise RuntimeError(f"AI suggestion failed: {error_type}: {e}") from e

    def print_summary(self):
        """Delegate to metrics tracker."""
        self.metrics_tracker.print_summary()

    def generate_report(self, output_path: str = "ai_healing_report.json"):
        """Delegate to metrics tracker."""
        self.metrics_tracker.generate_report(output_path)
