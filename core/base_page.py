from playwright.async_api import Page
from functools import cached_property

from core.services.attribute import Attribute
from core.services.content import Content
from core.services.element_state import ElementState
from core.services.file import FileHandler
from core.services.form_filling.element_resolver import ElementResolver
from core.services.form_filling.strategy_factory import StrategyFactory
from core.services.mouse import Mouse
from core.services. screenshot import Screenshot
from core.services.storage import Storage
from core. services.tab_window import TabWindow
from core.services.validation import Validation
from core.services. wait import Wait
from utils.config import Config


class BasePage:
    """BasePage class that provides lazy-loaded services for page interactions."""

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
    def attribute(self) -> Attribute:
        return Attribute(self.page)

    @cached_property
    def content(self) -> Content:
        return Content(self.page)

    @cached_property
    def element_state(self) -> ElementState:
        return ElementState(self.page)

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
        return Wait(self. page)