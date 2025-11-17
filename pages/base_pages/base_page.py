from mixins.attribute import AttributeMixin
from mixins.content import ContentMixin
from mixins.element_state import ElementStateMixin
from mixins.file import FileMixin
from mixins.form_filling import FormFillingMixin
from mixins.mouse import MouseMixin
from mixins.screenshot import ScreenshotMixin
from mixins.storage import StorageMixin
from mixins.tab_window import TabWindowMixin
from mixins.validation import ValidationMixin
from mixins.wait import WaitMixin


class BasePage(AttributeMixin, 
               ContentMixin, 
               ElementStateMixin, 
               FileMixin, 
               FormFillingMixin, 
               MouseMixin, 
               ScreenshotMixin, 
               StorageMixin, 
               TabWindowMixin, 
               ValidationMixin, 
               WaitMixin):
    
    """BasePage class that combines all mixins for comprehensive page interactions."""
    def __init__(self, page):
        self.page = page