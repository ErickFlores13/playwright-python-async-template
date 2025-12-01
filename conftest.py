"""
conftest.py — Core pytest configuration for async Playwright tests.

Includes:
- Browser management with Strategy pattern
- Database (Postgres) and Redis connections
- Structured logging and async-safe teardown
- Test fixtures (browser, page, context, etc.)

Note: Pytest hooks are defined in core/reporting/pytest_hooks.py

Author: Erick Guadalupe Félix Flores
License: MIT
"""

import asyncio
import logging
import os
import shutil
import sys
from typing import Generator, AsyncGenerator, List

import pytest
import pytest_asyncio
from playwright.async_api import BrowserContext, Page

# Custom imports
from helpers.redis_client import RedisClient
from pages.base_pages.login_page import LoginPage
from helpers.database import DatabaseClient
from helpers.api_client import APIClient
from utils.config import Config
from core.utils.logger_config import configure_logging
from core.ui.browser.browser_manager import BrowserManager
from core.ui.browser.strategies.strategy_factory import get_browser_strategy

# Import pytest hooks from dedicated module
from core.reporting.pytest_hooks import pytest_runtest_makereport  # noqa: F401

# Ensure package imports work regardless of execution path
sys.path.insert(0, os.path.dirname(__file__))

# --- Get logger for this module -----------------------------------------------
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
    
    Sets up:
    - Centralized logging configuration
    - Automatic parallel execution if PYTEST_WORKERS is set
    """
    # Configure centralized logging
    log_level = logging.DEBUG if Config.is_debug() else logging.INFO
    log_to_file = Config.is_ci_environment()
    
    configure_logging(
        level=log_level,
        log_to_file=log_to_file
    )
    
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
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create a dedicated asyncio event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# --- Browser Manager with Strategy Pattern ------------------------------------
@pytest_asyncio.fixture(scope="session")
async def browser_manager() -> AsyncGenerator[BrowserManager, None]:
    """
    Provides BrowserManager for the entire test session.
    
    Strategy is selected based on environment variables:
    - CI=true → CIStrategy (headless, video recording, optimized for CI)
    - TEST_MODE=debug → DebugStrategy (slow motion, devtools, visible)
    - Default → LocalStrategy (respects BROWSER, HEADLESS from config)
    
    The strategy pattern eliminates complex if/else logic and makes
    browser configuration easy to extend and maintain.
    """
    strategy = get_browser_strategy()
    manager = BrowserManager(strategy)
    
    await manager.start()
    logger.info(f"✅ Browser Manager started with {strategy.__class__.__name__}")
    
    yield manager
    
    await manager.stop()
    logger.info("Browser Manager stopped")

@pytest_asyncio.fixture(scope="function")
async def context(browser_manager: BrowserManager) -> AsyncGenerator[BrowserContext, None]:
    """
    Creates a new isolated browser context per test.
    
    Context options come from the active strategy.
    Tests can override options by using browser_manager.new_context() directly.
    """
    ctx = await browser_manager.new_context()
    yield ctx
    await ctx.close()

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
# --- Page fixture (modern approach) ------------------------------------------
@pytest_asyncio.fixture(scope="function")
async def page(context: BrowserContext) -> AsyncGenerator[Page, None]:
    """
    Provides a single Playwright Page object per test.
    
    The page is automatically closed after the test completes.
    """
    page = await context.new_page()
    yield page
    await page.close()

# --- Login helpers ------------------------------------------------------------
@pytest_asyncio.fixture
async def login(page: Page):
    async def _connect_to_environment(username: str, password: str, url: str):
        return await LoginPage(page).login(username, password, url)
    return _connect_to_environment

# --- API Client fixture -------------------------------------------------------
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


