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
from helpers.database import DatabaseClient
from helpers.api_client import APIClient
from utils.config import Config

# Ensure package imports work regardless of execution path
sys.path.insert(0, os.path.dirname(__file__))

# --- Logging configuration ----------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# --- Pytest configuration hook for parallel execution -------------------------
def pytest_addoption(parser):
    """Add custom command line options and read environment variables."""
    # pytest-xdist parallel execution
    # If -n is not provided on command line, check PYTEST_WORKERS env var
    parser.addoption(
        "--workers",
        action="store",
        default=None,
        help="Number of workers for parallel execution (overrides PYTEST_WORKERS env var)"
    )


def pytest_configure(config):
    """
    Configure pytest based on environment variables.
    
    Automatically enables parallel execution if PYTEST_WORKERS is set
    and -n option is not provided on command line.
    """
    # Check if -n option was provided on command line
    # If not, use PYTEST_WORKERS from environment
    if config.getoption('numprocesses', None) is None:
        workers = Config.get_pytest_workers()
        if workers and workers.lower() != 'none':
            # Set the numprocesses option for pytest-xdist
            config.option.numprocesses = workers
            logger.info(f"🚀 Parallel execution enabled: {workers} workers (from PYTEST_WORKERS)")

# --- Pytest event loop fixture -------------------------------------------------
@pytest_asyncio.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None]:
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
    """
    Launches the browser session with configuration from environment variables.
    
    Browser type is determined by BROWSER env var (chromium, firefox, webkit).
    Headless mode is controlled by HEADLESS env var (true/false).
    """
    # Get browser configuration from Config
    browser_type = Config.get_browser_type()
    headless = Config.is_headless()
    
    # Select browser based on configuration
    if browser_type == 'firefox':
        browser = await playwright.firefox.launch(headless=headless)
    elif browser_type == 'webkit':
        browser = await playwright.webkit.launch(headless=headless)
    else:  # Default to chromium
        browser = await playwright.chromium.launch(headless=headless)
    
    logger.info(f"Browser launched: {browser_type}, headless={headless}")
    yield browser
    await browser.close()

@pytest_asyncio.fixture(scope="function")
async def context(browser: Browser) -> AsyncGenerator[BrowserContext, None]:
    """
    Creates a new isolated browser context per test.
    
    Configuration comes from environment variables:
    - VIEWPORT_WIDTH, VIEWPORT_HEIGHT: Browser viewport size
    - BROWSER_LOCALE: Browser locale (e.g., en-US, es-ES)
    - USER_AGENT: Custom user agent string
    """
    # Get configuration from Config
    viewport = Config.get_viewport_size()
    locale = Config.get_browser_locale()
    user_agent = Config.get_user_agent()
    
    context = await browser.new_context(
        viewport=viewport,
        locale=locale,
        user_agent=user_agent,
        ignore_https_errors=True,
    )
    yield context
    await context.close()

# --- Screenshots directory cleanup --------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def clean_screenshots() -> None:
    """
    Clean screenshots folder before session start.
    
    Screenshots directory is determined by SCREENSHOTS_DIR env var.
    """
    screenshots_dir = Config.get_screenshots_dir()
    if os.path.exists(screenshots_dir):
        shutil.rmtree(screenshots_dir)
    os.makedirs(screenshots_dir, exist_ok=True)
    logger.info(f"Screenshots directory cleaned: {screenshots_dir}")

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
    """
    Hook to capture screenshots when a test fails.
    
    Screenshots are only captured if SCREENSHOT_ON_FAILURE=true in .env
    """
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        # Check if screenshots should be captured
        if not Config.should_screenshot_on_failure():
            logger.debug("Screenshot on failure disabled by config")
            return
        
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


@pytest_asyncio.fixture
async def api_client(playwright):
    """
    Provides API client factory for creating clients to different APIs.
    
    Returns a factory function that creates API clients with custom base URLs.
    Default uses API_BASE_URL from environment if no URL is provided.
    
    Example:
        @pytest.mark.asyncio
        async def test_single_api(api_client):
            # Use default API_BASE_URL from .env
            client = await api_client()
            await client.set_bearer_token(os.getenv("API_BEARER_TOKEN"))
            response = await client.get("/users")
        
        @pytest.mark.asyncio
        async def test_multiple_apis(api_client):
            # Test integration between two different APIs
            auth_api = await api_client("https://auth.example.com")
            data_api = await api_client("https://api.example.com")
            
            # Login to auth API
            login_resp = await auth_api.post("/auth/login", data={...})
            token = login_resp["token"]
            
            # Use token with data API
            await data_api.set_bearer_token(token)
            users = await data_api.get("/users")
            
        @pytest.mark.asyncio
        async def test_env_based_apis(api_client):
            # Use environment variables for different services
            auth_client = await api_client(os.getenv("AUTH_API_URL"))
            payment_client = await api_client(os.getenv("PAYMENT_API_URL"))
            notification_client = await api_client(os.getenv("NOTIFICATION_API_URL"))
    """
    contexts = []
    
    async def _create_client(base_url: str = None, headers: dict = None):
        """
        Create an API client for a specific base URL.
        
        Args:
            base_url: Base URL for the API. If None, uses API_BASE_URL from .env
            headers: Additional headers to include in all requests
        
        Returns:
            APIClient instance configured for the specified API
        """
        url = base_url or os.getenv("API_BASE_URL")
        if not url:
            raise ValueError(
                "No API base URL provided. Either pass base_url parameter or set API_BASE_URL in .env"
            )
        
        default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Merge custom headers with defaults
        if headers:
            default_headers.update(headers)
        
        request_context = await playwright.request.new_context(
            base_url=url,
            extra_http_headers=default_headers
        )
        contexts.append(request_context)
        
        return APIClient(request_context, url)
    
    yield _create_client
    
    # Cleanup all created contexts
    for ctx in contexts:
        await ctx.dispose()


# --- Database fixtures --------------------------------------------------------
@pytest_asyncio.fixture
async def db_client():
    """
    Provides SQL database client (PostgreSQL, MySQL, SQL Server, Oracle).
    
    Only activates if DB_TEST=true in environment variables.
    Uses environment variables for configuration (DB_TYPE, DB_HOST, etc.).
    Provides basic query execution methods - users write their own queries.
    
    Example:
        @pytest.mark.asyncio
        async def test_database(db_client):
            # Basic query
            user = await db_client.fetch_one(
                "SELECT * FROM users WHERE email = :email",
                {"email": "test@test.com"}
            )
            assert user["status"] == "active"
            
            # Use SQLAlchemy ORM directly if needed
            async with db_client.session_maker() as session:
                # Your ORM queries here
                pass
    """
    if os.getenv("DB_TEST", "false").lower() != "true":
        pytest.skip("Database testing disabled (DB_TEST is not true)")
    
    client = DatabaseClient()
    await client.connect()
    yield client
    await client.disconnect()


# --- Redis fixture ------------------------------------------------------------
@pytest_asyncio.fixture(scope="function", autouse=True)
async def close_redis():
    """Automatically closes all Redis connections after each test."""
    yield
    await RedisClient.close_all()


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
