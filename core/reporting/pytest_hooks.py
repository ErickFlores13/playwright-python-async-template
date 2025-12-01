"""
Pytest hooks for test reporting and evidence collection.

Handles automatic capture of test failure evidence:
- Screenshots
- Videos (CI mode)
- HTML snapshots
- Browser console logs

Author: Erick Guadalupe Félix Flores
License: MIT
"""
import logging
import os
import re
from datetime import datetime

import allure
import pytest
from allure_commons.types import AttachmentType

from utils.config import Config

logger = logging.getLogger(__name__)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture screenshots and attach evidence when a test fails.
    
    Captures:
    - Screenshot (if page fixture is available)
    - Full HTML snapshot (for debugging)
    - Video recording (CI mode only)
    - Browser console logs (if collected)
    
    Evidence is only captured if SCREENSHOT_ON_FAILURE=true in .env
    """
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        # Check if screenshots should be captured
        if not Config.should_screenshot_on_failure():
            logger.debug("Screenshot on failure disabled by config")
            return
        
        # Get page fixture (modern approach - single page per test)
        page = item.funcargs.get("page")
        
        if not page:
            logger.debug("No page fixture found, skipping screenshot capture")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        match = re.search(r"\[([^\s\]]+)", item.nodeid)
        base_name = (match.group(1) if match else item.nodeid.split("[")[0])[:50]
        
        try:
            # Capture screenshot
            screenshot_filename = f"screenshots/{base_name}_{timestamp}.png"
            screenshot_bytes = item.funcargs["event_loop"].run_until_complete(
                page.screenshot(path=screenshot_filename, full_page=True)
            )
            allure.attach(
                screenshot_bytes,
                name="failure_screenshot",
                attachment_type=AttachmentType.PNG
            )
            logger.info(f"📸 Screenshot captured: {screenshot_filename}")
            
            # Capture HTML snapshot for debugging
            html_content = item.funcargs["event_loop"].run_until_complete(page.content())
            allure.attach(
                html_content,
                name="page_html",
                attachment_type=AttachmentType.HTML
            )
            
            # Capture video in CI mode (if enabled via CIStrategy)
            if Config.is_ci_environment() and page.video:
                try:
                    # Close page to finalize video
                    video_path = page.video.path()
                    item.funcargs["event_loop"].run_until_complete(page.close())
                    
                    # Attach video to Allure
                    with open(video_path, "rb") as video_file:
                        allure.attach(
                            video_file.read(),
                            name="failure_video",
                            attachment_type=allure.attachment_type.WEBM
                        )
                    logger.info(f"🎥 Video captured: {video_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not attach video: {e}")
            
            # Capture browser console logs if available
            try:
                console_logs = []
                # Note: Console messages need to be collected during test execution
                # This is just a placeholder - implement console listener in page fixture if needed
                if console_logs:
                    allure.attach(
                        "\n".join(console_logs),
                        name="console_logs",
                        attachment_type=AttachmentType.TEXT
                    )
            except Exception:
                pass  # Console logs not critical
                
        except Exception as e:
            logger.error(f"❌ Error capturing failure evidence: {e}")
