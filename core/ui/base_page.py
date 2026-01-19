from functools import cached_property

from playwright.async_api import Page

from core.ui.services.attribute import Attribute
from core.ui.services.form.element_resolver import ElementResolver
from core.ui.services.form.strategy_factory import StrategyFactory
from core.ui.services.screenshot import Screenshot
from core.ui.services.storage import Storage
from core.ui.services.tab_window import TabWindow
from core.ui.services.validation import Validation
from core.ui.services.wait import Wait
from utils.config import Config


class BasePage:
    """
    BasePage class that provides lazy-loaded services for page interactions.

    Designed to be used as part of a modular Page Object Model for test automation.
    Uses cached properties to initialize services only when accessed.

    Convenience Methods (Recommended - Simplified API):
    - fill_data(): Fill form fields automatically
    - edit_item(): Clear and refill form fields
    - validate_edit_view(): Validate form field values
    - validate_details_view(): Validate read-only detail view

    Services (Advanced - Direct access when needed):
    - attribute: DOM attribute manipulation for security/validation testing
    - element_resolver: Service for resolving and interacting with web elements
    - strategy_factory: Factory for form field interaction strategies
    - screenshot: Service for taking screenshots
    - storage: Service for managing local and session storage
    - tab_window: Service for managing browser tabs
    - validation: Service for validating page states and elements
    - wait: Service for managing page load and element wait strategies

    Components (for file operations):
    - Use FileComponent directly: FileComponent(page, selector)

    Note: For simple operations, use Playwright's API directly:
    - Mouse: page.locator(selector).hover(), .dblclick(), .click(button='right'), .drag_to()
    - Text: page.locator(selector).inner_text(), .text_content()
    - Click: page.locator(selector).click()
    """

    def __init__(self, page: Page):
        self.page = page
        self.timeout = Config.get_timeout()

    # ==================== Lazy-Loaded Services ====================

    @cached_property
    def attribute(self) -> Attribute:
        """Service for manipulating DOM attributes (for security/validation testing)."""
        return Attribute(self.page)

    @cached_property
    def element_resolver(self) -> ElementResolver:
        """Service for resolving and interacting with web elements."""
        return ElementResolver(self.page)

    @cached_property
    def strategy_factory(self) -> StrategyFactory:
        """Factory for form field interaction strategies."""
        return StrategyFactory(self.element_resolver)

    @cached_property
    def screenshot(self) -> Screenshot:
        """Service for taking screenshots."""
        return Screenshot(self.page)

    @cached_property
    def storage(self) -> Storage:
        """Service for managing local and session storage."""
        return Storage(self.page)

    @cached_property
    def tab_window(self) -> TabWindow:
        """Service for managing browser tabs and windows."""
        return TabWindow(self.page)

    @cached_property
    def validation(self) -> Validation:
        """Service for validating page states and elements."""
        return Validation(self.page)

    @cached_property
    def wait(self) -> Wait:
        """Service for managing page load and element wait strategies."""
        return Wait(self.page)

    # ==================== Convenience Shortcuts (Facade Pattern) ====================

    async def fill_data(self, data: dict) -> None:
        """
        Fill form fields automatically with type detection.

        This is a convenience shortcut to self.strategy_factory.fill_data().
        Automatically detects field types and uses appropriate interaction strategy.

        Args:
            data: Dict mapping selectors to values

        Example:
            await self.fill_data({
                '#name': 'John Doe',
                '#email': 'john@example.com',
                '#department': 'Engineering',
                '#active': True,
                '#resume': 'C:/resume.pdf',
            })
        """
        await self.strategy_factory.fill_data(data)

    async def edit_item(self, data: dict) -> None:
        """
        Clear existing values and refill form fields.

        This is a convenience shortcut to self.strategy_factory.edit_item().
        Clears fields before filling with new values.

        Args:
            data: Dict mapping selectors to new values

        Example:
            await self.edit_item({
                '#name': 'Jane Smith',
                '#department': 'Sales',
            })
        """
        await self.strategy_factory.edit_item(data)

    async def validate_edit_view(self, data: dict) -> None:
        """
        Validate form field values in edit view.

        This is a convenience shortcut to self.strategy_factory.validate_edit_view().
        Validates that form fields contain expected values.

        Args:
            data: Dict mapping selectors to expected values

        Example:
            await self.validate_edit_view({
                '#name': 'John Doe',
                '#department': 'Engineering',
                '#active': True,
            })
        """
        await self.strategy_factory.validate_edit_view(data)

    async def validate_details_view(self, data: dict) -> None:
        """
        Validate values in read-only details view.

        This is a convenience shortcut to:
        self.validation.validate_record_information_in_details_view()

        Validates that container elements display expected values.

        Args:
            data: Dict mapping container selectors to expected values

        Example:
            await self.validate_details_view({
                '#div_id_name': 'John Doe',
                '#div_id_email': 'john@example.com',
                '#div_id_active': True,
            })
        """
        await self.validation.validate_record_information_in_details_view(data)
