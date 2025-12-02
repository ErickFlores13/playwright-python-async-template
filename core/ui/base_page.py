from functools import cached_property

from playwright.async_api import Page

from core.ui.services.file import FileHandler
from core.ui.services.form.element_resolver import ElementResolver
from core.ui.services.form.strategy_factory import StrategyFactory
from core.ui.services.mouse import Mouse
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
    - element_resolver: Service for resolving and interacting with web elements.
    - strategy_factory: Factory for form field interaction strategies.
    - file: Service for handling file upload and download operations.
    - mouse: Service for mouse interactions.
    - screenshot: Service for taking screenshots.
    - storage: Service for managing local and session storage.
    - tab_window: Service for managing browser tabs.
    - validation: Service for validating page states and elements.
    - wait: Service for waiting and synchronization.
    """

    def __init__(self, page: Page):
        self.page = page
        self.timeout = Config.get_timeout()

    @cached_property
    def element_resolver(self) -> ElementResolver:
        return ElementResolver(self.page)

    @cached_property
    def strategy_factory(self) -> StrategyFactory:
        return StrategyFactory(self.element_resolver)

    @cached_property
    def file(self) -> FileHandler:
        return FileHandler(self.page)

    @cached_property
    def mouse(self) -> Mouse:
        return Mouse(self.page)

    @cached_property
    def screenshot(self) -> Screenshot:
        return Screenshot(self.page)

    @cached_property
    def storage(self) -> Storage:
        return Storage(self.page)

    @cached_property
    def tab_window(self) -> TabWindow:
        return TabWindow(self.page)

    @cached_property
    def validation(self) -> Validation:
        return Validation(self.page)

    @cached_property
    def wait(self) -> Wait:
        return Wait(self.page)
