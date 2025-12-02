import logging
import os
from typing import Union

from playwright.async_api import Locator, Page, expect

from core.ui.services.wait import Wait
from core.utils.exceptions import ValidationError
from core.utils.playwright_utils import resolve_locator

logger = logging.getLogger(__name__)


class FileComponent:
    """
    Component for file input interactions and file download operations.

    Handles file uploads, preview validation, downloads, and verification.
    Bound to a specific file input selector for simple operations.
    """

    def __init__(self, page: Page, selector: str, timeout: int = 30000):
        self.page = page
        self.selector = selector
        self.timeout = timeout
        self.locator: Locator = self.page.locator(selector)
        self.wait = Wait(page)

    async def wait_for_visible(self) -> None:
        """Wait for file input to be visible."""
        logger.debug(f"[FileComponent] Waiting for visibility of {self.selector}")
        await self.locator.wait_for(state="visible", timeout=self.timeout)

    async def upload(self, file_path: str) -> None:
        """Upload a file."""
        await self.wait_for_visible()
        logger.debug(f"[FileComponent] Uploading file {file_path} to {self.selector}")
        await self.locator.set_input_files(file_path)

    async def clear(self) -> None:
        """Clear the selected file(s)."""
        await self.wait_for_visible()
        logger.debug(f"[FileComponent] Clearing files from {self.selector}")
        await self.locator.evaluate("el => el.value = ''")

    async def validate_cleared(self) -> None:
        """Validate if file input is cleared."""
        await expect(self.locator).to_have_value("")

    async def validate_has_file(self) -> None:
        """Validate that a file has been uploaded (input is not empty).

        Note: Due to browser security restrictions, we can only verify that
        a file exists, but cannot validate the specific filename.
        """
        await self.wait_for_visible()
        logger.debug(f"[FileComponent] Validating {self.selector} has a file")
        await expect(self.locator).not_to_have_value("")

    async def clear_and_validate(self) -> None:
        """Clear file input and validate."""
        await self.clear()
        await self.validate_cleared()

    # ========== Advanced File Operations (from FileHandler) ==========

    async def upload_files_with_preview_validation(
        self, file_paths: list[str], preview_element: Union[str, Locator], timeout: float = None
    ) -> None:
        """
        Uploads files to the bound file input and validates preview elements.

        Args:
            file_paths (list): List of absolute file paths to upload
            preview_element (Union[str, Locator]): Selector or Locator for file preview elements
            timeout (float, optional): Maximum wait time (ms). Defaults to instance timeout.

        Raises:
            ValidationError: if any file does not exist or preview count mismatches.

        Example:
            file_comp = FileComponent(page, 'input[type="file"]')
            await file_comp.upload_files_with_preview_validation(
                ['/path/to/image1.jpg', '/path/to/document.pdf'],
                '.file-preview'
            )
        """
        timeout = timeout or self.timeout

        logger.debug(f"[FileComponent] Uploading files: {file_paths}")
        for file_path in file_paths:
            if not os.path.exists(file_path):
                raise ValidationError("file_upload", f"File not found: {file_path}")

        await self.wait_for_visible()
        logger.debug(f"[FileComponent] Setting files on {self.selector}")
        await self.locator.set_input_files(file_paths, timeout=timeout)

        logger.debug("[FileComponent] Waiting for page to process uploads and display previews")
        await self.wait.wait_for_page_load(timeout=timeout)

        logger.debug(
            f"[FileComponent] Validating {len(file_paths)} file previews: {preview_element}"
        )
        preview_locator = resolve_locator(self.page, preview_element)
        await preview_locator.first.wait_for(state="visible", timeout=timeout)
        preview_count = await preview_locator.count()

        logger.debug(f"[FileComponent] Found {preview_count} file previews")
        if preview_count != len(file_paths):
            raise ValidationError(
                "file_preview", f"Expected {len(file_paths)} previews, found {preview_count}"
            )

    async def download_file(
        self, download_trigger: Union[str, Locator], expected_filename: str = None
    ) -> str:
        """
        Triggers a file download and waits for it to complete.

        Args:
            download_trigger (Union[str, Locator]): Selector or Locator for the download trigger element
            expected_filename (str, optional): Expected filename pattern to validate.

        Returns:
            str: Path to the downloaded file.

        Raises:
            ValidationError: if download fails or filename doesn't match.

        Example:
            file_comp = FileComponent(page, 'input[type="file"]')
            file_path = await file_comp.download_file('button#download', 'report.pdf')
        """
        download_trigger_locator = resolve_locator(self.page, download_trigger)
        logger.debug(f"[FileComponent] Initiating file download: {download_trigger}")
        async with self.page.expect_download() as download_info:
            await download_trigger_locator.click()

        logger.debug("[FileComponent] Waiting for download to complete")
        download = await download_info.value

        if expected_filename and expected_filename not in download.suggested_filename:
            raise ValidationError(
                field=str(download_trigger),
                message=f"Downloaded file '{download.suggested_filename}' does not match expected '{expected_filename}'",
            )

        logger.debug(f"[FileComponent] Saving downloaded file: {download.suggested_filename}")
        file_path = os.path.join(os.getcwd(), "downloads", download.suggested_filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        await download.save_as(file_path)

        logger.debug(f"[FileComponent] File downloaded successfully: {file_path}")
        return file_path

    async def verify_file_downloaded(self, file_path: str, min_size_bytes: int = 0) -> bool:
        """
        Verifies that a file exists and optionally checks its size.

        Args:
            file_path (str): Path to the downloaded file.
            min_size_bytes (int): Minimum expected file size in bytes.

        Returns:
            bool: True if file exists and meets size requirement.

        Raises:
            ValidationError: if file doesn't exist or is too small.
        """
        logger.debug(
            f"[FileComponent] Verifying file at: {file_path} (min size: {min_size_bytes} bytes)"
        )

        if not os.path.exists(file_path):
            raise ValidationError(
                field=file_path, message=f"Downloaded file does not exist: {file_path}"
            )

        file_size = os.path.getsize(file_path)
        logger.debug(f"[FileComponent] Downloaded file size: {file_size} bytes")

        if file_size < min_size_bytes:
            raise ValidationError(
                field=file_path,
                message=f"File size {file_size} bytes is less than minimum {min_size_bytes} bytes",
            )

        logger.debug(f"[FileComponent] File verified: {file_path} ({file_size} bytes)")
        return True

    async def download_and_verify_file(
        self,
        download_trigger: Union[str, Locator],
        expected_filename: str = None,
        min_size_bytes: int = 0,
        cleanup: bool = True,
    ) -> str:
        """
        Complete workflow: download file, verify it, and optionally clean up.

        Args:
            download_trigger (Union[str, Locator]): Selector or locator for download trigger.
            expected_filename (str, optional): Expected filename pattern.
            min_size_bytes (int): Minimum file size in bytes.
            cleanup (bool): Whether to delete file after verification.

        Returns:
            str: Path to downloaded file (if cleanup=False), None otherwise.

        Example:
            file_comp = FileComponent(page, 'input[type="file"]')
            await file_comp.download_and_verify_file(
                'a#export-csv',
                expected_filename='data.csv',
                min_size_bytes=100
            )
        """
        logger.debug(f"[FileComponent] Starting download and verification: {download_trigger}")
        file_path = await self.download_file(download_trigger, expected_filename)

        logger.debug(f"[FileComponent] Verifying downloaded file at: {file_path}")
        await self.verify_file_downloaded(file_path, min_size_bytes)

        if cleanup:
            os.remove(file_path)
            logger.debug(f"[FileComponent] Cleaned up downloaded file: {file_path}")
            return None

        logger.debug(f"[FileComponent] Download and verification complete: {file_path}")
        return file_path
