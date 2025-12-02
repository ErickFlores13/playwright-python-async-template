from playwright.async_api import Locator


class Field:
    """
    Represents a fully-resolved form field, including its locator and metadata.
    """

    def __init__(
        self,
        selector: str,
        locator: Locator,
        tag: str,
        input_type: str,
        is_select2: bool,
    ):
        self.selector = selector
        self.locator = locator
        self.tag = tag
        self.input_type = input_type
        self.is_select2 = is_select2