# Browser Configuration Strategies

This directory contains browser configuration strategies that control how Playwright browsers are launched and configured based on different testing scenarios.

## Overview

The Strategy Pattern is used to manage browser configuration, making it easy to:
- Switch between different browser configurations without code changes
- Add new configurations without modifying existing code
- Control everything through environment variables
- Keep configuration logic isolated and testable

## Available Strategies

### 1. LocalStrategy (Default)

**When to use:**
- Local development
- Interactive debugging with visible browser
- Respecting developer preferences from `.env`

**Configuration:**
```bash
# No special env vars needed - this is the default
pytest -s -k test_name
```

**Internal Settings:**
- **Browser Type:** From `BROWSER` env var (chromium/firefox/webkit)
- **Headless:** From `HEADLESS` env var (default: false for visibility)
- **Viewport:** From `VIEWPORT_WIDTH` and `VIEWPORT_HEIGHT` env vars
- **Locale:** From `BROWSER_LOCALE` env var
- **User Agent:** From `USER_AGENT` env var
- **Slow Motion:** 50ms if `DEBUG=true`, else 0ms
- **Window:** Maximized (chromium only)
- **Video Recording:** Disabled

**Best for:**
- Writing new tests
- Debugging existing tests
- Exploratory testing
- Local test runs

---

### 2. CIStrategy

**When to use:**
- CI/CD pipelines (GitHub Actions, Jenkins, GitLab CI)
- Automated test runs in containerized environments
- When you need video recordings for failure analysis

**Configuration:**
```bash
CI=true pytest
```

**Internal Settings:**
- **Browser Type:** Always chromium (most stable for CI)
- **Headless:** Always true (no display in CI)
- **Viewport:** Fixed 1920x1080 (consistency)
- **Locale:** From `BROWSER_LOCALE` env var
- **User Agent:** Default chromium
- **Slow Motion:** 0ms (fast execution)
- **Window:** Not applicable (headless)
- **Video Recording:** Enabled (saves to `screenshots/videos/`)
- **Browser Args:**
  - `--no-sandbox` (required in Docker)
  - `--disable-dev-shm-usage` (prevents memory issues)
  - `--disable-gpu` (not needed in headless)
  - `--disable-software-rasterizer` (performance)
  - `--disable-blink-features=AutomationControlled` (stealth)

**Best for:**
- Continuous integration
- Regression testing
- Production deployment validation
- Failure analysis (videos)

---

### 3. DebugStrategy

**When to use:**
- Investigating test failures
- Understanding complex page interactions
- Stepping through test execution
- Learning how tests work

**Configuration:**
```bash
TEST_MODE=debug pytest -s -k test_name
```

**Internal Settings:**
- **Browser Type:** From `BROWSER` env var (chromium/firefox/webkit)
- **Headless:** Always false (must see the browser)
- **Viewport:** From `VIEWPORT_WIDTH` and `VIEWPORT_HEIGHT` env vars
- **Locale:** From `BROWSER_LOCALE` env var
- **User Agent:** From `USER_AGENT` env var
- **Slow Motion:** 500ms (half second between each action)
- **DevTools:** Auto-opened
- **Window:** Maximized (chromium only)
- **Video Recording:** Disabled

**Best for:**
- Debugging flaky tests
- Understanding timing issues
- Investigating element interactions
- Training/demonstrations

---

## Strategy Selection Logic

The framework automatically selects the strategy based on environment variables:

```
┌─────────────────────────────────────┐
│ Is CI=true?                         │
│   ├─ YES → CIStrategy               │
│   └─ NO  → Continue                 │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│ Is TEST_MODE=debug?                 │
│   ├─ YES → DebugStrategy            │
│   └─ NO  → LocalStrategy (default)  │
└─────────────────────────────────────┘
```

## Usage Examples

### Local Development (Default)
```bash
# Uses LocalStrategy with your .env settings
pytest tests/

# With specific browser
BROWSER=firefox pytest tests/

# Headless mode locally
HEADLESS=true pytest tests/
```

### Debug Mode
```bash
# Slow motion + DevTools
TEST_MODE=debug pytest -s -k test_login

# Debug with Firefox
TEST_MODE=debug BROWSER=firefox pytest -s -k test_checkout
```

### CI/CD Pipeline
```bash
# In GitHub Actions, Jenkins, etc.
CI=true pytest tests/

# CI with specific locale
CI=true BROWSER_LOCALE=es-ES pytest tests/
```

## Creating New Strategies

To add a new strategy (e.g., MobileStrategy):

1. **Create the strategy file:** `mobile_strategy.py`
```python
from core.ui.browser.strategies.browser_strategy import BrowserStrategy
from playwright.async_api import devices

class MobileStrategy(BrowserStrategy):
    def __init__(self, device_name: str = "iPhone 13"):
        self.device = devices[device_name]
    
    def get_browser_type(self) -> str:
        return "chromium"
    
    def get_launch_options(self) -> dict:
        return {"headless": Config.is_headless()}
    
    def get_context_options(self) -> dict:
        return {**self.device}
```

2. **Update strategy factory:** `strategy_factory.py`
```python
elif test_mode == 'mobile':
    device = os.getenv('DEVICE', 'iPhone 13')
    return MobileStrategy(device)
```

3. **Use it:**
```bash
TEST_MODE=mobile pytest
TEST_MODE=mobile DEVICE="Pixel 5" pytest
```

## Environment Variables Reference

| Variable | Used By | Default | Description |
|----------|---------|---------|-------------|
| `CI` | All | `false` | Triggers CIStrategy when `true` |
| `TEST_MODE` | All | `local` | Options: `local`, `debug` |
| `BROWSER` | Local, Debug | `chromium` | Browser type: `chromium`, `firefox`, `webkit` |
| `HEADLESS` | Local | `true` | Run browser in headless mode |
| `VIEWPORT_WIDTH` | Local, Debug | `1920` | Browser viewport width |
| `VIEWPORT_HEIGHT` | Local, Debug | `1080` | Browser viewport height |
| `BROWSER_LOCALE` | All | `en-US` | Browser locale (e.g., `es-ES`, `fr-FR`) |
| `USER_AGENT` | Local, Debug | Default | Custom user agent string |
| `DEBUG` | Local | `true` | Enables 50ms slow motion in LocalStrategy |

## Architecture Benefits

✅ **Separation of Concerns** - Configuration logic separated from test logic  
✅ **Open/Closed Principle** - Add new strategies without modifying existing code  
✅ **Environment-Driven** - Everything controlled via environment variables  
✅ **Easy Testing** - Each strategy can be unit tested independently  
✅ **Zero Test Changes** - Tests remain the same regardless of strategy  
✅ **Maintainable** - Configuration centralized in strategy classes  

## Related Files

- `browser_strategy.py` - Abstract base class defining the interface
- `strategy_factory.py` - Factory function for strategy selection
- `../browser_manager.py` - Uses strategies to manage browser lifecycle
- `../../../conftest.py` - Pytest integration using BrowserManager