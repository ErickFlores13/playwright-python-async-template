import logging
from playwright.async_api import Page, Locator

logger = logging.getLogger(__name__)


class ModalComponent:
    """Generic modal/dialog component."""

    def __init__(self, page: Page, root_selector: str):
        self.page = page
        self.root_selector = root_selector
        self.root: Locator = page.locator(root_selector)

    @property
    def title(self) -> Locator:
        return self.root.locator(".modal-title")

    @property
    def body(self) -> Locator:
        return self.root.locator(".modal-body")

    @property
    def close_btn(self) -> Locator:
        return self.root.locator(".modal-footer button, button[data-dismiss='modal'], .close")

    async def is_visible(self) -> bool:
        """Return whether the modal is visible."""
        logger.debug(f"[Modal] Checking visibility of {self.root_selector}")
        return await self.root.is_visible()

    async def wait_for_visible(self, timeout: int = 3000) -> None:
        """Wait for the modal to be visible."""
        logger.debug(f"[Modal] Waiting for visibility of {self.root_selector} with timeout {timeout}ms")
        await self.root.wait_for(state="visible", timeout=timeout)

    async def close(self) -> None:
        """Close the modal by clicking the close button."""
        if await self.close_btn.count() > 0:
            logger.debug(f"[Modal] Closing modal {self.root_selector}")
            await self.close_btn.first.click()

    async def get_title(self) -> str:
        """Return the modal title text."""
        await self.wait_for_visible()
        logger.debug(f"[Modal] Getting title of {self.root_selector}")
        modal_title = (await self.title.text_content()).strip()
        logger.debug(f"[Modal] Title of {self.root_selector} is '{modal_title}'")
        return modal_title

    async def get_body_text(self) -> str:
        """Return the modal body text."""
        await self.wait_for_visible()
        logger.debug(f"[Modal] Getting body text of {self.root_selector}")
        modal_body = (await self.body.text_content()).strip()
        logger.debug(f"[Modal] Body text of {self.root_selector} is '{modal_body}'")
        return modal_body

    async def confirm(self) -> None:
        """Click the confirm/primary button in the modal footer."""
        btn = self.root.locator(".modal-footer button.btn-primary, .modal-footer button:has-text('Confirm'), .modal-footer button:has-text('OK')")
        logger.debug(f"[Modal] Confirming modal {self.root_selector}")
        if await btn.count() > 0:
            await btn.first.click()

    async def cancel(self) -> None:
        """Click the cancel/close button in the modal footer. """
        btn = self.root.locator(".modal-footer button:has-text('Cancel'), .modal-footer button:has-text('Close')")
        logger.debug(f"[Modal] Cancelling modal {self.root_selector}")
        if await btn.count() > 0:
            await btn.first.click()
