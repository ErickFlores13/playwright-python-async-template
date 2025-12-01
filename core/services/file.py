import logging
import os
from playwright.async_api import Page, Locator
from core.utils.exceptions import ValidationError, ConfigurationError
from typing import Union
from core.utils.playwright_utils import resolve_locator
from core.services.wait import Wait

logger = logging.getLogger(__name__)

class FileHandler:
    """
    Service for handling file upload and download operations in Playwright tests.
    Provides methods for uploading files with preview validation, handling drag-and-drop uploads,
    Designed to be used as part of a modular Page Object Model for test automation.
    """

    def __init__(self, page: Page):
        if not page:
            raise ConfigurationError(
                config_key="page",
                message="Page instance cannot be None or empty"
            )
        self.page = page
        self.wait = Wait(page)

    async def upload_files_with_preview_validation(
            self, 
            file_input: Union[str, Locator], 
            file_paths: list[str], 
            preview_element: Union[str, Locator],
            timeout: float = 30000) -> None:
        """
        Uploads files and validates preview elements.
        
        Args:
            file_input (Union[str, Locator]): selector or Locator for the file input element
            file_paths (list): List of absolute file paths to upload
            preview_element (Union[str, Locator]): Selector or Locator for file preview elements
            timeout (float, optional): Maximum wait time (ms) for elements
                to become visible. Defaults to Playwright's timeout.
            
        Raises:
            ValidationError: if any file does not exist or preview count mismatches.
            playwright.async_api.TimeoutError: if elements do not become visible in time.    
            
        Example:
            await page.upload_files_with_preview_validation(
                'input[type="file"]',
                ['/path/to/image1.jpg', '/path/to/document.pdf'],
                '.file-preview'
            )
        """
        logger.debug(f"Uploading files: {file_paths} using input: {file_input}")
        for file_path in file_paths:
            if not os.path.exists(file_path):
                raise ValidationError("file_upload", f"File not found: {file_path}")
        
        file_input_locator = resolve_locator(self.page, file_input)
        await file_input_locator.wait_for(state="visible", timeout=timeout)

        logger.debug(f"Setting files on input: {file_input}")
        await file_input_locator.set_input_files(file_paths, timeout=timeout)
        
        logger.debug("Waiting for page to process uploads and display previews")
        await self.wait.wait_for_page_load(timeout=timeout)
        
        logger.debug(f"Validating {len(file_paths)} file previews using selector: {preview_element}")
        preview_locator = resolve_locator(self.page, preview_element)
        await preview_locator.wait_for(state="visible", timeout=timeout)
        preview_count = await preview_locator.count()
        
        logger.debug(f"Found {preview_count} file previews")
        if preview_count != len(file_paths):
            raise ValidationError("file_preview", f"Expected {len(file_paths)} previews, found {preview_count}")

    async def download_file(
            self, 
            download_trigger: Union[str, Locator], 
            expected_filename: str = None) -> str:
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
            file_path = await self.download_file('button#download', 'report.pdf')
            # File is saved and path is returned
        """
        download_trigger_locator = resolve_locator(self.page, download_trigger)
        logger.debug(f"Initiating file download using trigger: {download_trigger}")
        async with self.page.expect_download() as download_info:
            await download_trigger_locator.click()
        
        logger.debug("Waiting for download to complete")
        download = await download_info.value
        
        if expected_filename and expected_filename not in download.suggested_filename:
            raise ValidationError(
                field=download_trigger,
                message=f"Downloaded file '{download.suggested_filename}' does not match expected '{expected_filename}'"
            )
        
        logger.debug(f"Saving downloaded file: {download.suggested_filename}")
        file_path = os.path.join(os.getcwd(), 'downloads', download.suggested_filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        await download.save_as(file_path)
        
        logger.debug(f"File downloaded successfully: {file_path}")
        return file_path

    async def verify_file_downloaded(
            self, 
            file_path: str, 
            min_size_bytes: int = 0) -> bool:
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
        logger.debug(f"Verifying downloaded file at: {file_path} with minimum size: {min_size_bytes} bytes")

        if not os.path.exists(file_path):
            raise ValidationError(
                field=file_path,
                message=f"Downloaded file does not exist: {file_path}"
            )
        
        file_size = os.path.getsize(file_path)
        logger.debug(f"Downloaded file size: {file_size} bytes")

        if file_size < min_size_bytes:
            raise ValidationError(
                field=file_path,
                message=f"File size {file_size} bytes is less than minimum {min_size_bytes} bytes"
            )
        
        logger.debug(f"File verified: {file_path} ({file_size} bytes)")
        return True

    async def download_and_verify_file(
        self, 
        download_trigger: Union[str, Locator], 
        expected_filename: str = None,
        min_size_bytes: int = 0,
        cleanup: bool = True
    ) -> str:
        """
        Complete workflow: download file, verify it, and optionally clean up.
        
        Args:
            download_trigger (Union[str, Locator]): Selector or locator for download trigger.
            expected_filename (str, optional): Expected filename pattern.
            min_size_bytes (int): Minimum file size in bytes.
            cleanup (bool): Whether to delete file after verification.
            
        Returns:
            str: Path to downloaded file (if cleanup=False).
            
        Example:
            await self.download_and_verify_file(
                'a#export-csv',
                expected_filename='data.csv',
                min_size_bytes=100
            )
        """
        logger.debug(f"Starting download and verification for trigger: {download_trigger}")
        file_path = await self.download_file(download_trigger, expected_filename)
    
        logger.debug(f"Verifying downloaded file at: {file_path}")
        await self.verify_file_downloaded(file_path, min_size_bytes)
        
        if cleanup:
            os.remove(file_path)
            logger.debug(f"Cleaned up downloaded file: {file_path}")
            return None
        
        logger.debug(f"Download and verification complete for file: {file_path}")
        return file_path