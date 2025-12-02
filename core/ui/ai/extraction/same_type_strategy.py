"""
Same-type extraction strategy - extracts elements of the same type as failed selector.
"""

import logging

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Page

from .base_strategy import ExtractionStrategy

logger = logging.getLogger(__name__)


class SameTypeStrategy(ExtractionStrategy):
    """
    Extracts elements of the same type as the failed selector.

    Fast and efficient - only sends relevant elements to AI.
    Works well for simple attribute typos (e.g., name="porc_rasasdaojo" -> "porc_rojo")
    """

    async def extract(self, page: Page, failed_selector: str) -> str:
        """
        Extract elements of the same type as the failed selector.

        Args:
            page: Playwright Page instance
            failed_selector: The selector that failed

        Returns:
            Formatted string with element information
        """
        try:
            # Determine element type from failed selector
            element_type = self._guess_element_type(failed_selector)

            # Build selector for that element type
            selector_map = {
                "input": "input",
                "button": 'button, input[type="button"], input[type="submit"]',
                "select": "select",
                "textarea": "textarea",
                "a": "a",
                "unknown": "input, button, select, textarea, a",
            }
            selector = selector_map.get(element_type, selector_map["unknown"])

            # Get elements in one batch operation (much faster!)
            # Use evaluate with argument passing to avoid injection issues
            elements_data = await page.evaluate(
                """(selector) => {
                const elements = document.querySelectorAll(selector);
                const relevantAttrs = ['name', 'id', 'class', 'type', 'data-testid',
                                       'placeholder', 'value', 'aria-label', 'role'];

                return Array.from(elements).slice(0, 50).map((el) => {
                    const attrs = {};
                    for (const attr of el.attributes) {
                        // Only get relevant attributes (reduces payload size)
                        if (relevantAttrs.includes(attr.name)) {
                            attrs[attr.name] = attr.value;
                        }
                    }
                    return {
                        tag: el.tagName.toLowerCase(),
                        attributes: attrs,
                        text: el.textContent?.trim().substring(0, 50) || ''
                    };
                });
            }""",
                selector,
            )

            logger.debug(
                f"📦 [{self.get_name()}] Extracted {len(elements_data)} {element_type} elements"
            )

            if not elements_data:
                logger.warning(f"[WARN] [{self.get_name()}] No {element_type} elements found")
                return f"No {element_type} elements found on page"

            # Format as readable text for AI
            formatted = f"Found {len(elements_data)} {element_type} elements on page:\n\n"
            for i, elem in enumerate(elements_data, start=1):
                attrs = elem.get("attributes", {})  # Get element attributes
                attr_str = " ".join(
                    [f'{k}="{v}"' for k, v in attrs.items() if v]
                )  # Format attributes
                formatted += f"{i}. <{elem['tag']} {attr_str}>\n"  # Basic element info
                if elem.get("text"):
                    formatted += f"   Text: {elem['text']}\n"  # Include text content if available

            return formatted

        except PlaywrightError as e:
            logger.warning(f"[WARN] [{self.get_name()}] Playwright error, trying fallback")
            # Ultra-fast fallback - just get input names
            try:
                input_names = await page.evaluate(
                    """() => {
                    return Array.from(document.querySelectorAll('input')).map(el => ({
                        name: el.name,
                        id: el.id,
                        type: el.type
                    }));
                }"""
                )
                return f"Available inputs: {input_names}"
            except PlaywrightError as e:
                raise PlaywrightError(f"Fallback element extraction also failed: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"Unexpected error extracting elements: {type(e).__name__}: {e}"
            ) from e

    def get_name(self) -> str:
        """Get strategy name."""
        return "same_type"
