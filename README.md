# 🎭 Playwright Python Async Template

A **production-ready test automation framework** built with **Playwright + Python**, designed for modern web applications with comprehensive UI, API, and database testing capabilities.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/playwright-1.46.0-green)](https://playwright.dev/python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Key Features

- 🎯 **Complete testing solution:** UI, API, and Database testing in one framework
- ⚡ **Fully async:** Built with async/await for optimal performance
- � **Flexible configuration:** Environment-based setup via `.env` files
- 🌐 **Multi-browser support:** Chromium, Firefox, and WebKit
- � **Parallel execution:** Auto-configured via `PYTEST_WORKERS` environment variable
- � **Smart screenshots:** Automatic capture on test failures
- � **Docker ready:** Full containerization support for CI/CD
- 📚 **Comprehensive docs:** Detailed guides for UI, API, and database testing
- � **Modular design:** Page Object Model with reusable components

---

## � Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/ErickFlores13/playwright-python-async-template.git
cd playwright-python-async-template

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install Playwright browsers
playwright install

# 6. Configure environment
cp .env.example .env
# Edit .env with your settings
```

### Minimal Configuration

Edit `.env` with your basic settings:

```bash
# Required
BASE_URL=https://your-application.com
TEST_USERNAME=test_user
TEST_PASSWORD=test_password

# Optional - Browser configuration
BROWSER=chromium                 # chromium | firefox | webkit
HEADLESS=true                    # true | false
PYTEST_WORKERS=auto              # auto | 1 | 2 | 4 | 8

# Optional - Enable database testing
DB_TEST=false                    # Set to true if needed
```

### Run Your First Test

```bash
# Run example tests
pytest tests/test_ui_examples.py -v

# Run with visible browser (debugging)
pytest tests/test_ui_examples.py --headed -v

# Run in parallel
pytest tests/ -n auto
```

---

## 🏗️ Project Structure

```
playwright-python-async-template/
├── pages/                      # Page Object Model
│   ├── base_page.py           # Core browser interactions
│   ├── standard_web_page.py   # Common UI patterns (CRUD, filters, etc.)
│   ├── login_page.py          # Authentication
│   └── examples/              # Example page objects
│
├── helpers/                    # Helper modules
│   ├── api_client.py          # API testing client
│   ├── database.py            # Database client (PostgreSQL, MySQL, etc.)
│   └── redis_client.py        # Redis client
│
├── utils/                      # Utilities
│   ├── config.py              # Configuration management
│   ├── consts.py              # Constants and enums
│   ├── exceptions.py          # Custom exceptions
│   └── test_helpers.py        # Test utilities
│
├── tests/                      # Test suites
│   ├── test_ui_examples.py    # UI testing examples
│   ├── test_api_examples.py   # API testing examples
│   ├── test_database_examples.py  # Database testing examples
│   └── test_crud_example.py   # Complete CRUD example
│
├── docs/                       # Documentation
│   ├── UI_TESTING.md          # UI testing guide
│   ├── API_TESTING.md         # API testing guide
│   └── DATABASE_TESTING.md    # Database testing guide
│
├── ci/                         # CI/CD configuration
│   └── Jenkinsfile            # Jenkins pipeline
│
├── conftest.py                 # Pytest configuration and fixtures
├── pytest.ini                  # Pytest settings
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── .env.example               # Environment template
└── README.md                   # This file
```

---

## � Documentation

Comprehensive guides for each testing type:

- **[UI Testing Guide](docs/UI_TESTING.md)** - Complete guide for UI automation
  - Page Object Model patterns
  - Form handling and validations
  - CRUD operations
  - Advanced UI interactions
  
- **[API Testing Guide](docs/API_TESTING.md)** - Complete guide for API testing
  - Authentication methods (Bearer, API Key, Basic Auth)
  - HTTP methods (GET, POST, PUT, PATCH, DELETE)
  - File uploads/downloads
  - Pagination and retry logic
  - Performance testing
  
- **[Database Testing Guide](docs/DATABASE_TESTING.md)** - Complete guide for database testing
  - PostgreSQL, MySQL, SQL Server, Oracle support
  - Direct queries and ORM usage
  - Data validation patterns
  - Redis integration

---

## 🎯 Testing Capabilities

### UI Testing

```python
from pages.base_page import BasePage

@pytest.mark.asyncio
async def test_ui(page):
    base_page = BasePage(page)
    await page.goto("https://your-app.com")
    await base_page.fill_data({
        "#username": "test_user",
        "#password": "test_pass"
    })
    await page.click("button[type='submit']")
```

👉 **See [UI Testing Guide](docs/UI_TESTING.md) for complete examples**

### API Testing

```python
@pytest.mark.asyncio
async def test_api(api_client):
    await api_client.set_bearer_token(os.getenv("API_BEARER_TOKEN"))
    users = await api_client.get("/users")
    assert len(users) > 0
```

👉 **See [API Testing Guide](docs/API_TESTING.md) for complete examples**

### Database Testing

```python
@pytest.mark.asyncio
async def test_database(db_client):
    user = await db_client.fetch_one(
        "SELECT * FROM users WHERE email = :email",
        {"email": "test@test.com"}
    )
    assert user["status"] == "active"
```

� **See [Database Testing Guide](docs/DATABASE_TESTING.md) for complete examples**

---

## ⚙️ Configuration

The framework uses environment variables for configuration. All settings are in `.env`:

### Core Settings

```bash
# Application
BASE_URL=https://your-app.com
TEST_USERNAME=test_user
TEST_PASSWORD=test_pass

# Browser
BROWSER=chromium                    # chromium | firefox | webkit
HEADLESS=true                       # true | false
VIEWPORT_WIDTH=1920
VIEWPORT_HEIGHT=1080

# Test Execution
PYTEST_WORKERS=auto                 # auto | 1 | 2 | 4 | 8
TIMEOUT=30000
SCREENSHOT_ON_FAILURE=true
```

### Optional Features

```bash
# API Testing
API_BASE_URL=https://api.example.com
API_BEARER_TOKEN=your_token

# Database Testing
DB_TEST=false                       # Set to true to enable
DB_TYPE=postgresql                  # postgresql | mysql | mssql | oracle
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
```

See `.env.example` for all available options.

---

## 🐳 Docker Support

### Quick Start

```bash
# Build and run tests
docker build -t playwright-tests .
docker run --rm \
  -e BASE_URL=https://your-app.com \
  -e TEST_USERNAME=test_user \
  -e TEST_PASSWORD=test_pass \
  playwright-tests
```

### CI/CD Integration

Example Jenkinsfile included in `ci/Jenkinsfile`.

---

## � Advanced Features

### Parallel Execution

Auto-configured via environment variable:

```bash
# .env
PYTEST_WORKERS=auto              # Auto-detect CPU cores
# or
PYTEST_WORKERS=4                 # Use 4 workers

# Run tests (parallel execution is automatic)
pytest tests/
```

### Custom Page Objects

```python
from pages.base_page import BasePage

class MyAppPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.login_button = '[data-testid="login"]'
    
    async def login(self, username, password):
        await self.fill_data({
            '#username': username,
            '#password': password,
        })
        await self.page.click(self.login_button)
```

### Hybrid UI + API Testing

```python
@pytest.mark.asyncio
async def test_hybrid(page, api_client):
    # UI login
    await page.goto(f"{os.getenv('BASE_URL')}/login")
    # ... perform login ...
    
    # Extract token from UI
    token = await page.evaluate("localStorage.getItem('token')")
    
    # Use token for API testing
    await api_client.set_bearer_token(token)
    user_data = await api_client.get("/users/me")
    
    # Verify UI and API data match
    ui_username = await page.text_content(".username")
    assert user_data["username"] == ui_username
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes using [Conventional Commits](https://www.conventionalcommits.org/)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [Playwright](https://playwright.dev/python/)
- Testing with [pytest](https://pytest.org/)
- Reporting with [Allure](https://docs.qameta.io/allure/)

---

## 🆘 Support & Resources

- **Documentation**: Check the `docs/` directory for detailed guides
- **Examples**: See `tests/` directory for working examples
- **Issues**: [GitHub Issues](https://github.com/ErickFlores13/playwright-python-async-template/issues)

### Troubleshooting

**Tests timing out?**
- Increase `TIMEOUT` in `.env`
- Use `--headed` mode to see what's happening

**Browser not found?**
```bash
playwright install
```

**Import errors?**
```bash
# Windows (PowerShell)
$env:PYTHONPATH = "${pwd}"

# Linux/macOS
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

**Made with ❤️ by [Erick Flores](https://github.com/ErickFlores13)**