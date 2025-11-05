"""
conftest.py — Core pytest configuration for async Playwright tests.

Includes:
- Multi-context browser management.
- Automatic screenshot capture on failure (Allure integrated).
- Database (Postgres) and Redis connections.
- 502 error handler with retry and recovery mechanism.
- Structured logging and async-safe teardown.

Author: Erick Guadalupe Félix Flores
License: MIT
"""

import asyncio
import logging
import os
import re
import shutil
import sys
from datetime import datetime
from typing import Generator, AsyncGenerator, List

import allure
import pytest
import pytest_asyncio
from allure_commons.types import AttachmentType
from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright

# Custom imports
from helpers.redis_client import RedisClient
from pages.login_page import LoginPage
from helpers.database import AsyncPostgresConnector

# Ensure package imports work regardless of execution path
sys.path.insert(0, os.path.dirname(__file__))

# --- Logging configuration ----------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# --- Pytest event loop fixture -------------------------------------------------
@pytest_asyncio.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create a dedicated asyncio event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# --- Playwright and browser fixtures ------------------------------------------
@pytest_asyncio.fixture(scope="session")
async def playwright() -> AsyncGenerator[Playwright, None]:
    async with async_playwright() as p:
        yield p

@pytest_asyncio.fixture(scope="session")
async def browser(playwright: Playwright) -> AsyncGenerator[Browser, None]:
    """Launches the browser session"""
    browser = await playwright.chromium.launch()
    yield browser
    await browser.close()

@pytest_asyncio.fixture(scope="function")
async def context(browser: Browser) -> AsyncGenerator[BrowserContext, None]:
    """Creates a new isolated browser context per test."""
    context = await browser.new_context(
        locale="es-ES",
        ignore_https_errors=True,
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        ),
    )
    yield context
    await context.close()

# --- Screenshots directory cleanup --------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def clean_screenshots() -> None:
    """Clean screenshots folder before session start."""
    screenshots_dir = "screenshots"
    if os.path.exists(screenshots_dir):
        shutil.rmtree(screenshots_dir)
    os.makedirs(screenshots_dir, exist_ok=True)

# --- 502 handler --------------------------------------------------------------
async def add_502_handler(page: Page, max_retries: int = 10, timeout: float = 30.0):
    """
    Watches for HTTP 502 error popups and reloads the page when detected.
    Runs as an async background task.
    """
    retries = 0
    async def handle_reload():
        nonlocal retries
        if retries >= max_retries:
            logger.warning("❌ Max retries reached for 502 recovery.")
            return
        retries += 1
        logger.warning(f"⚠️ Detected 502 error. Attempting reload {retries}/{max_retries}...")
        try:
            await asyncio.wait_for(page.reload(), timeout=timeout)
            await page.wait_for_load_state("domcontentloaded")
            logger.info("✅ Page reloaded successfully.")
        except asyncio.TimeoutError:
            logger.error("Timeout while reloading page after 502.")
        except Exception as e:
            if "Target closed" in str(e) or "Page closed" in str(e):
                logger.warning("Page or browser closed — stopping watcher.")
                raise

    async def watch_loop():
        while retries < max_retries:
            try:
                if await page.locator("#error-information-popup-content > div.error-code").is_visible(timeout=1000):
                    await handle_reload()
            except Exception as e:
                if "Target closed" in str(e) or "Page closed" in str(e):
                    break
            await asyncio.sleep(1)

    return asyncio.create_task(watch_loop())

# --- Pages registry -----------------------------------------------------------
@pytest_asyncio.fixture(scope="function")
async def pages_registry() -> AsyncGenerator[List[Page], None]:
    """Keeps track of all opened pages during test execution."""
    registry: List[Page] = []
    yield registry
    registry.clear()

@pytest_asyncio.fixture(scope="function")
async def page(context: BrowserContext, pages_registry: list[Page]) -> AsyncGenerator[Page, None]:
    """Provides a single Playwright Page object per test."""
    page = await context.new_page()
    pages_registry.append(page)
    yield page
    await page.close()

# --- Login helpers ------------------------------------------------------------
@pytest_asyncio.fixture
async def login_to_environment():
    async def _connect_to_environment(page: Page, username: str, password: str, url: str):
        await LoginPage(page).change_user(username, password, url)
    return _connect_to_environment

# DRY helper for login fixtures
async def _login_factory(browser: Browser, pages_registry, base_url_env: str):
    async def _login(username: str, password: str):
        context = await browser.new_context(ignore_https_errors=True, viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        url = os.getenv(base_url_env)
        result_page = await LoginPage(page).login(username, password, base_url=url)
        pages_registry.append(result_page)
        task = await add_502_handler(result_page)
        return context, result_page, task
    return _login

@pytest_asyncio.fixture
async def login_admin_central(browser: Browser, pages_registry):
    """Fixture for admin central login."""
    sessions = []
    login = await _login_factory(browser, pages_registry, "ADMIN_USUARIOS_CENTRAL_URL")
    yield login
    for context, page, task in sessions:
        task.cancel()
        await context.close()

@pytest_asyncio.fixture
async def login_admin_local_a(browser: Browser, pages_registry):
    """Fixture for admin local A login."""
    sessions = []
    login = await _login_factory(browser, pages_registry, "ADMIN_USUARIOS_LOCAL_A_URL")
    yield login
    for context, page, task in sessions:
        task.cancel()
        await context.close()

@pytest_asyncio.fixture
async def login_admin_local_b(browser: Browser, pages_registry):
    """Fixture for admin local B login."""
    sessions = []
    login = await _login_factory(browser, pages_registry, "ADMIN_USUARIOS_LOCAL_B_URL")
    yield login
    for context, page, task in sessions:
        task.cancel()
        await context.close()

# --- Screenshot + Allure integration on failure -------------------------------
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture screenshots when a test fails."""
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        pages_registry = item.funcargs.get("pages_registry", [])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        match = re.search(r"\[([^\s\]]+)", item.nodeid)
        base_name = (match.group(1) if match else item.nodeid.split("[")[0])[:50]

        for i, page in enumerate(pages_registry):
            filename = f"screenshots/{base_name}_page{i+1}_{timestamp}.png"
            try:
                item.funcargs["event_loop"].run_until_complete(page.screenshot(path=filename))
                with open(filename, "rb") as f:
                    allure.attach(f.read(), name=os.path.basename(filename), attachment_type=AttachmentType.PNG)
                logger.info(f"📸 Screenshot captured and attached to Allure: {filename}")
            except Exception as e:
                logger.error(f"Error capturing screenshot: {e}")

# --- Database + Redis fixtures ------------------------------------------------
if os.getenv("DB_TEST") == "True":
    @pytest_asyncio.fixture(scope="module")
    async def db_session():
        """Async Postgres connection for Central DB."""
        connector = AsyncPostgresConnector(
            user=os.getenv("SQL_USER"),
            password=os.getenv("SQL_PASSWORD"),
            host=os.getenv("SQL_HOST"),
            port=os.getenv("SQL_PORT"),
            dbname=os.getenv("SQL_DBNAME"),
            echo=False,
        )
        async with connector.get_session() as session:
            yield session

    @pytest_asyncio.fixture(scope="function", autouse=True)
    async def close_redis():
        """Automatically closes all Redis connections after each test."""
        yield
        await RedisClient.close_all()
