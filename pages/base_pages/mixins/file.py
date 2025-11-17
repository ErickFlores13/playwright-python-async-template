import logging
import os
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from utils.exceptions import (
    ValidationError,
    ConfigurationError,
)

logger = logging.getLogger(__name__)

class FileMixin:
    """
    Generic base page with overridable playwright methods that allow a custom-made test automation.
    """

    def __init__(self, page: Page) -> None:
        if not page:
            raise ConfigurationError(
                config_key="page",
                message="Page instance cannot be None or empty"
            )
            
        self.page = page

    async def upload_files_with_preview_validation(self, file_input_selector: str, file_paths: list, 
                                                 preview_selector: str) -> None:
        """
        Uploads files and optionally validates preview elements.
        
        Args:
            file_input_selector (str): CSS selector for the file input
            file_paths (list): List of absolute file paths to upload
            preview_selector (str, optional): Selector for file preview elements
            
        Example:
            await page.upload_files_with_preview_validation(
                'input[type="file"]',
                ['/path/to/image1.jpg', '/path/to/document.pdf'],
                '.file-preview'
            )
        """
        # Ensure all files exist
        import os
        for file_path in file_paths:
            if not os.path.exists(file_path):
                raise ValidationError("file_upload", f"File not found: {file_path}")
        
        await self.page.wait_for_selector(file_input_selector)
        await self.page.set_input_files(file_input_selector, file_paths)
        
        # Wait for upload processing
        await self.page.wait_for_timeout(1000)
        
        # Validate previews if selector provided
        await self.page.wait_for_selector(preview_selector, timeout=10000)
        preview_count = await self.page.locator(preview_selector).count()
        
        if preview_count != len(file_paths):
            raise ValidationError("file_preview", 
                                f"Expected {len(file_paths)} previews, found {preview_count}")

    async def handle_drag_and_drop_upload(self, drop_zone_selector: str, file_paths: list) -> None:
        """
        Handles drag-and-drop file uploads.
        
        Args:
            drop_zone_selector (str): CSS selector for the drop zone
            file_paths (list): List of file paths to upload
            
        Example:
            await page.handle_drag_and_drop_upload('#dropzone', ['/path/to/file.pdf'])
        """
        await self.page.wait_for_selector(drop_zone_selector)
        
        # Validate all files exist first
        for file_path in file_paths:
            if not os.path.exists(file_path):
                raise ValidationError("file_upload", f"File not found: {file_path}")
        
        # Look for a hidden file input within the drop zone (more direct approach)
        hidden_input_selector = f'{drop_zone_selector} input[type="file"]'
        hidden_input = self.page.locator(hidden_input_selector).first
        
        if await hidden_input.count() > 0:
            await hidden_input.set_input_files(file_paths)
        else:
            # If no hidden input, simulate drag-drop on the drop zone directly
            drop_zone_element = self.page.locator(drop_zone_selector)
            await drop_zone_element.evaluate("""
                (element, files) => {
                    const dt = new DataTransfer();
                    files.forEach(file => {
                        const fileObj = new File([''], file.split('/').pop(), {type: 'application/octet-stream'});
                        dt.items.add(fileObj);
                    });
                    
                    const event = new DragEvent('drop', {
                        bubbles: true,
                        cancelable: true,
                        dataTransfer: dt
                    });
                    
                    element.dispatchEvent(event);
                }
            """, file_paths)

    async def download_file(self, download_trigger_selector: str, expected_filename: str = None) -> str:
        """
        Triggers a file download and waits for it to complete.
        
        Args:
            download_trigger_selector (str): Selector for the download button/link.
            expected_filename (str, optional): Expected filename pattern to validate.
            
        Returns:
            str: Path to the downloaded file.
            
        Raises:
            ValidationError: if download fails or filename doesn't match.
            
        Example:
            file_path = await self.download_file('button#download', 'report.pdf')
            # File is saved and path is returned
        """
        try:
            async with self.page.expect_download() as download_info:
                await self.page.click(download_trigger_selector)
            
            download = await download_info.value
            
            # Validate filename if provided
            if expected_filename and expected_filename not in download.suggested_filename:
                raise ValidationError(
                    field=download_trigger_selector,
                    message=f"Downloaded file '{download.suggested_filename}' does not match expected '{expected_filename}'"
                )
            
            # Save to temp location
            file_path = os.path.join(os.getcwd(), 'downloads', download.suggested_filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            await download.save_as(file_path)
            
            logger.info(f"File downloaded successfully: {file_path}")
            return file_path
            
        except PlaywrightTimeoutError as e:
            raise ValidationError(
                field=download_trigger_selector,
                message="Download did not start within timeout"
            ) from e

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
        if not os.path.exists(file_path):
            raise ValidationError(
                field=file_path,
                message=f"Downloaded file does not exist: {file_path}"
            )
        
        file_size = os.path.getsize(file_path)
        
        if file_size < min_size_bytes:
            raise ValidationError(
                field=file_path,
                message=f"File size {file_size} bytes is less than minimum {min_size_bytes} bytes"
            )
        
        logger.info(f"File verified: {file_path} ({file_size} bytes)")
        return True

    async def download_and_verify_file(
        self, 
        download_trigger_selector: str, 
        expected_filename: str = None,
        min_size_bytes: int = 0,
        cleanup: bool = True
    ) -> str:
        """
        Complete workflow: download file, verify it, and optionally clean up.
        
        Args:
            download_trigger_selector (str): Selector for download trigger.
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
        file_path = await self.download_file(download_trigger_selector, expected_filename)
        await self.verify_file_downloaded(file_path, min_size_bytes)
        
        if cleanup:
            os.remove(file_path)
            logger.info(f"Cleaned up downloaded file: {file_path}")
            return None
        
        return file_path