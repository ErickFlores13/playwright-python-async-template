import asyncio
import logging

from playwright.async_api import Page

from core.ui.services.wait import Wait
from core.utils.exceptions import ConfigurationError, ElementNotFoundError, ValidationError

logger = logging.getLogger(__name__)


class TabWindow:
    """
    Generic base page with overridable playwright methods that allow a custom-made test automation.
    """

    def __init__(self, page: Page) -> None:
        if not page:
            raise ConfigurationError(
                config_key="page", message="Page instance cannot be None or empty"
            )

        self.page = page
        self.wait = Wait(page)

    async def switch_to_new_tab(self) -> None:
        """
        Switches to the newest opened tab.

        Raises:
            ValidationError: If tab switch operation fails.

        Note:
            Updates self.page to reference the new tab.
        """
        try:
            # Wait for new page to open
            async with self.page.context.expect_page() as new_page_info:
                pass
            new_page = await new_page_info.value
            await new_page.wait_for_load_state()
            self.page = new_page
        except Exception as e:
            raise ValidationError("tab_switch", f"Tab switch failed: {str(e)}") from e

    async def close_current_tab(self) -> None:
        """
        Closes current tab and switches to previous one.

        Raises:
            ValidationError: If tab close operation fails.

        Note:
            Will not close the last remaining tab - logs a warning instead.
        """
        try:
            context = self.page.context
            pages = context.pages
            if len(pages) > 1:
                await self.page.close()
                self.page = pages[-2]  # Switch to previous tab
            else:
                logger.warning("Cannot close last remaining tab")
        except Exception as e:
            raise ValidationError("tab_close", f"Failed to close tab: {str(e)}") from e

    async def refresh_page(self) -> None:
        """
        Refreshes the current page.

        Raises:
            ValidationError: If page refresh operation fails.

        Note:
            Waits for page to fully load after refresh.
        """
        try:
            await self.page.reload()
            await self.wait.wait_for_page_load()
        except Exception as e:
            raise ValidationError("page_refresh", f"Page refresh failed: {str(e)}") from e

    async def go_back(self) -> None:
        """
        Navigates back in browser history.

        Raises:
            ValidationError: If back navigation fails.

        Note:
            Waits for page to fully load after navigation.
        """
        try:
            await self.page.go_back()
            await self.wait.wait_for_page_load()
        except Exception as e:
            raise ValidationError("navigation_back", f"Back navigation failed: {str(e)}") from e

    async def go_forward(self) -> None:
        """
        Navigates forward in browser history.

        Raises:
            ValidationError: If forward navigation fails.

        Note:
            Waits for page to fully load after navigation.
        """
        try:
            await self.page.go_forward()
            await self.wait.wait_for_page_load()
        except Exception as e:
            raise ValidationError(
                "navigation_forward", f"Forward navigation failed: {str(e)}"
            ) from e

    async def handle_confirmation_dialog(
        self, trigger_action, accept: bool = True, dialog_text: str = None
    ) -> str:
        """
        Handles JavaScript confirmation dialogs (alert, confirm, prompt).

        Args:
            trigger_action: Function/coroutine that triggers the dialog
            accept (bool): Whether to accept (OK) or dismiss (Cancel) the dialog
            dialog_text (str, optional): Expected dialog text for validation

        Returns:
            str: The actual dialog message text

        Example:
            message = await page.handle_confirmation_dialog(
                lambda: page.click('#delete-button'),
                accept=True,
                dialog_text="Are you sure you want to delete?"
            )
        """
        dialog_message = None

        async def dialog_handler(dialog):
            nonlocal dialog_message
            dialog_message = dialog.message

            if dialog_text and dialog_text not in dialog_message:
                raise ValidationError(
                    "dialog_validation",
                    f"Expected dialog text '{dialog_text}' but got '{dialog_message}'",
                )

            if accept:
                await dialog.accept()
            else:
                await dialog.dismiss()

        self.page.on("dialog", dialog_handler)

        try:
            if asyncio.iscoroutinefunction(trigger_action):
                await trigger_action()
            else:
                await trigger_action()
        finally:
            self.page.remove_listener("dialog", dialog_handler)

        return dialog_message or ""

    async def close_modal_by_escape(self, modal_selector: str) -> None:
        """
        Closes a modal by pressing the Escape key.

        Args:
            modal_selector (str): Selector for the modal element to verify closure.

        Raises:
            PlaywrightTimeoutError: If modal doesn't close within 5 seconds.

        Example:
            await self.close_modal_by_escape('.modal-dialog')
        """
        await self.page.keyboard.press("Escape")
        await self.page.wait_for_selector(modal_selector, state="hidden", timeout=5000)

    async def open_link_in_new_tab(self, link_selector: str) -> Page:
        """
        Opens a link in a new tab and returns the new page object.

        Args:
            link_selector (str): selector for the link

        Returns:
            Page: New page object for the opened tab

        Example:
            new_page = await page.open_link_in_new_tab('a[href="/reports"]')
        """
        # Listen for new page
        async with self.page.context.expect_page() as new_page_info:
            # Right-click and open in new tab, or use Ctrl+Click
            await self.page.click(link_selector, modifiers=["Meta"])

        new_page = await new_page_info.value
        await new_page.wait_for_load_state("networkidle")
        return new_page

    async def switch_to_tab_by_title(self, title_pattern: str) -> Page:
        """
        Switches to a tab based on its title pattern.

        Args:
            title_pattern (str): Pattern to match in the tab title

        Returns:
            Page: The page object of the matching tab

        Example:
            target_page = await page.switch_to_tab_by_title('Dashboard')
        """
        pages = self.page.context.pages

        for page in pages:
            page_title = await page.title()
            if title_pattern.lower() in page_title.lower():
                await page.bring_to_front()
                return page

        raise ElementNotFoundError(f"Tab with title containing '{title_pattern}'", timeout=5000)

    async def close_other_tabs_except_current(self) -> None:
        """
        Closes all tabs except the current one.

        Example:
            await page.close_other_tabs_except_current()
        """
        current_page = self.page
        pages = self.page.context.pages

        for page in pages:
            if page != current_page:
                await page.close()

    async def wait_for_new_tab_and_switch(self, trigger_action, timeout: int = 10000) -> Page:
        """
        Waits for a new tab to open after performing an action and switches to it.

        Args:
            trigger_action: Function/coroutine that triggers the new tab
            timeout (int): Timeout in milliseconds

        Returns:
            Page: New page object

        Example:
            new_page = await page.wait_for_new_tab_and_switch(
                lambda: page.click('#open-report-button')
            )
        """
        async with self.page.context.expect_page(timeout=timeout) as new_page_info:
            if asyncio.iscoroutinefunction(trigger_action):
                await trigger_action()
            else:
                await trigger_action()

        new_page = await new_page_info.value
        await new_page.wait_for_load_state("networkidle")
        await new_page.bring_to_front()
        return new_page
