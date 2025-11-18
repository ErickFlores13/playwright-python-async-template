from playwright.async_api import Page, Locator
from typing import Union

def resolve_locator(page: Page, selector: Union[str, Locator]) -> Locator:
    """
    Resolves a string selector or a Locator to a Locator instance.

    Args:
        page (Page): Playwright Page instance.
        selector (Union[str, Locator]): Selector string or Locator.

    Returns:
        Locator: Playwright Locator instance.
    """
    if selector is None:
        raise ValueError("Selector cannot be None")
    return selector if isinstance(selector, Locator) else page.locator(selector)
