from core.services.attribute import Attribute
from core.services.content import Content
from core.services.element_state import ElementState
from core.services.file import FileHandler
from core.services.mouse import Mouse
from core.services.screenshot import Screenshot
from core.services.storage import Storage
from core.services.tab_window import TabWindow
from core.services.validation import Validation
from core.services.wait import Wait
from core.services.form_filling.strategy_factory import StrategyFactory
from core.services.form_filling.element_resolver import ElementResolver
from utils.config import Config

class BasePage():
    
    """BasePage class that combines all services for comprehensive page interactions."""
    def __init__(self, page):
        self.page = page
        self.element_resolver = ElementResolver(page)
        self.strategy_factory = StrategyFactory(self.element_resolver)
        self.timeout = Config.get_timeout()
        self.attribute = Attribute(page)
        self.content = Content(page)
        self.element_state = ElementState(page)
        self.file = FileHandler(page)
        self.mouse = Mouse(page)
        self.screenshot = Screenshot(page)
        self.storage = Storage(page)
        self.tab_window = TabWindow(page)
        self.validation = Validation(page)
        self.wait = Wait(page)