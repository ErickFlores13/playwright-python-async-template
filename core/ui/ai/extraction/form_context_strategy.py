"""
Form-context extraction strategy - extracts all fields within the same form.
"""

import logging

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Page

from .base_strategy import ExtractionStrategy

logger = logging.getLogger(__name__)


class FormContextStrategy(ExtractionStrategy):
    """
    Extracts all form fields within the same form as the failed selector.

    Provides semantic context - AI understands the field's purpose within the form.
    Works well for form restructuring or when field relationships matter.
    """

    async def extract(self, page: Page, failed_selector: str) -> str:
        """
        Extract all form fields, grouped by form.

        Args:
            page: Playwright Page instance
            failed_selector: The selector that failed

        Returns:
            Formatted string with form and field information
        """
        try:
            # Extract all forms with their fields
            forms_data = await page.evaluate(
                """() => {
                const forms = Array.from(document.querySelectorAll('form'));

                return forms.map((form, formIndex) => {
                    const formAttrs = {};
                    for (const attr of form.attributes) {
                        if (['id', 'name', 'class', 'action', 'method'].includes(attr.name)) {
                            formAttrs[attr.name] = attr.value;
                        }
                    }

                    const fields = Array.from(form.querySelectorAll('input, select, textarea, button')).map(field => {
                        const fieldAttrs = {};
                        for (const attr of field.attributes) {
                            if (['name', 'id', 'class', 'type', 'data-testid', 'placeholder', 'value'].includes(attr.name)) {
                                fieldAttrs[attr.name] = attr.value;
                            }
                        }
                        return {
                            tag: field.tagName.toLowerCase(),
                            attributes: fieldAttrs,
                            text: field.textContent?.trim().substring(0, 30) || '',
                            label: (() => {
                                // Try to find associated label
                                const id = field.id;
                                if (id) {
                                    const label = document.querySelector(`label[for="${id}"]`);
                                    if (label) return label.textContent?.trim();
                                }
                                // Check for wrapping label
                                const parentLabel = field.closest('label');
                                if (parentLabel) return parentLabel.textContent?.trim();
                                return null;
                            })()
                        };
                    });

                    return {
                        formIndex,
                        attributes: formAttrs,
                        fieldsCount: fields.length,
                        fields: fields.slice(0, 20)  // Limit to 20 fields per form
                    };
                });
            }"""
            )

            logger.debug(f"📦 [{self.get_name()}] Extracted {len(forms_data)} forms from page")

            # Format as readable text for AI
            if not forms_data:
                # No forms found - fallback to all input fields
                return await self._extract_all_fields(page)

            formatted = f"Found {len(forms_data)} forms on page:\n\n"

            # Parse each form and its fields
            for form in forms_data:
                # Format form attributes
                attrs = form.get("attributes", {})
                attr_str = (
                    " ".join([f'{k}="{v}"' for k, v in attrs.items()]) if attrs else "no attributes"
                )
                formatted += f"FORM {form['formIndex'] + 1} ({form['fieldsCount']} fields): <form {attr_str}>\n"

                # List fields within the form
                for i, field in enumerate(form["fields"]):
                    field_attrs = field.get("attributes", {})  # Get field attributes
                    field_attr_str = " ".join(
                        [f'{k}="{v}"' for k, v in field_attrs.items()]
                    )  # Format attributes
                    formatted += f"  {i+1}. <{field['tag']} {field_attr_str}>\n"  # Basic field info

                    # Include label or text if available
                    if field.get("label"):
                        formatted += f"     Label: {field['label']}\n"
                    if field.get("text") and field["tag"] == "button":
                        formatted += f"     Text: {field['text']}\n"

                formatted += "\n"  # Separate forms

            return formatted

        except PlaywrightError as e:
            logger.warning(
                f"[WARN] [{self.get_name()}] Playwright error, falling back to all fields"
            )
            return await self._extract_all_fields(page)
        except Exception as e:
            raise RuntimeError(
                f"Unexpected error in form context extraction: {type(e).__name__}: {e}"
            ) from e

    async def _extract_all_fields(self, page: Page) -> str:
        """
        Fallback: Extract all input fields when no forms found.

        Args:
            page: Playwright Page instance

        Returns:
            Formatted string with all field information
        """
        try:
            fields_data = await page.evaluate(
                """() => {
                return Array.from(document.querySelectorAll('input, select, textarea, button'))
                    .slice(0, 50)
                    .map(field => {
                        const attrs = {};
                        for (const attr of field.attributes) {
                            if (['name', 'id', 'class', 'type', 'data-testid', 'placeholder'].includes(attr.name)) {
                                attrs[attr.name] = attr.value;
                            }
                        }
                        return {
                            tag: field.tagName.toLowerCase(),
                            attributes: attrs
                        };
                    });
            }"""
            )

            formatted = f"No forms found. Available fields ({len(fields_data)}):\n\n"
            for i, field in enumerate(fields_data):
                attrs = field.get("attributes", {})  # Get field attributes
                attr_str = " ".join([f'{k}="{v}"' for k, v in attrs.items()])  # Format attributes
                formatted += f"{i+1}. <{field['tag']} {attr_str}>\n"  # Basic field info

            return formatted

        except PlaywrightError as e:
            raise PlaywrightError(f"Fallback field extraction failed: {e}") from e

    def get_name(self) -> str:
        """Get strategy name."""
        return "form_context"
