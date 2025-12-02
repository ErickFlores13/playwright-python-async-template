"""
Base class for element extraction strategies.
"""

from abc import ABC, abstractmethod

from playwright.async_api import Page


class ExtractionStrategy(ABC):
    """
    Abstract base class for element extraction strategies.

    Strategies determine how to extract relevant HTML elements
    from a page when a selector fails, providing context for AI healing.
    """

    @abstractmethod
    async def extract(self, page: Page, failed_selector: str) -> str:
        """
        Extract relevant elements from the page.

        Args:
            page: Playwright Page instance
            failed_selector: The selector that failed

        Returns:
            String containing formatted HTML/element information for AI analysis
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        Get the strategy name for logging/metrics.

        Returns:
            Strategy name (e.g., "same_type", "form_context")
        """
        pass

    def _guess_element_type(self, selector: str) -> str:
        """
        Guess the element type from the selector using robust parsing.

        Handles complex selectors like:
            input[name="test"] -> input
            button.submit -> button
            #my-select -> select (if contains 'select')
            .btn-primary -> button
            div > input.form-control -> input
            form button[type="submit"] -> button

        Args:
            selector: CSS selector string

        Returns:
            Element type string (input, button, select, textarea, a, or unknown)
        """
        import re

        selector_lower = selector.lower().strip()

        # Priority 1: Direct tag name at start
        # Matches: input[...], button.class, select#id, etc.
        tag_match = re.match(r"^(input|button|select|textarea|a)\b", selector_lower)
        if tag_match:
            return tag_match.group(1)

        # Priority 2: Tag name after combinators (>, +, ~, space)
        # Matches: div > input, form button, etc.
        combinator_match = re.search(r"[>\+~\s](input|button|select|textarea|a)\b", selector_lower)
        if combinator_match:
            return combinator_match.group(1)

        # Priority 3: Input type attributes
        # Matches: [type="button"], [type="submit"], etc.
        if re.search(r'\[type\s*=\s*["\']?(button|submit)', selector_lower):
            return "button"
        if re.search(r'\[type\s*=\s*["\']?(text|email|password|number|date)', selector_lower):
            return "input"

        # Priority 4: Common naming patterns in classes/IDs
        # Matches: .btn-primary, #submit-button, [name="user-input"], etc.
        if re.search(r"btn|button", selector_lower):
            return "button"
        if re.search(r"input|field", selector_lower):
            return "input"
        if re.search(r"select|dropdown", selector_lower):
            return "select"
        if re.search(r"textarea|comment|description", selector_lower):
            return "textarea"
        if re.search(r"link|anchor", selector_lower):
            return "a"

        # Priority 5: Semantic HTML5 elements (treat as buttons)
        if re.search(r"\b(nav|header|footer)\b", selector_lower):
            return "button"

        return "unknown"
