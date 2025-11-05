# 🧩 Playwright Python Automation Framework

A **modular, scalable, and maintainable test automation framework** built with **Playwright + Python**, designed for **any modern web application** - Django, React, Vue, Angular, or generic web apps.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/playwright-1.46.0-green)](https://playwright.dev/python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 Key Features

- 🔹 **Universal compatibility:** Works with **Django, React, Vue, Angular, and any web application**
- 🔹 **Modular architecture:** Clean separation between `BasePage`, `StandardWebPage`, and custom page objects
- 🔹 **Optional backend testing:** Built-in support for **PostgreSQL** and **Redis** (enable only if needed)
- 🔹 **Flexible configuration:** Environment-based configuration via `.env` files
- 🔹 **CI/CD ready:** GitHub Actions workflow included, easy Jenkins integration
- 🔹 **Automatic reporting:** Generates **Allure Reports** with screenshots on failure
- 🔹 **Async by default:** Fully asynchronous for better performance
- 🔹 **Parallel execution:** Run tests in parallel using `pytest-xdist`
- 🔹 **Docker support:** Containerized execution for consistent environments
- 🔹 **Example tests included:** Comprehensive examples for different use cases

---

## 🏗️ Project Structure

```bash
.
├── .github/
│   └── workflows/
│       └── playwright-tests.yml  # GitHub Actions CI/CD workflow
│
├── pages/
│   ├── base_page.py              # Core reusable Playwright actions (click, fill, wait, etc.)
│   ├── standard_web_page.py      # Common UI actions (filters, CRUD, validations)
│   └── login_page.py             # Generic login page implementation
│
├── helpers/
│   ├── database.py               # PostgreSQL client (optional, for backend validations)
│   └── redis_client.py           # Redis client (optional, for cache validations)
│
├── utils/
│   ├── consts.py                 # Centralized constants and enums
│   └── config.py                 # Configuration management from environment variables
│
├── tests/
│   └── examples/                 # Example test suites
│       ├── test_login_example.py
│       ├── test_crud_example.py
│       └── test_generic_webapp_example.py
│
├── conftest.py                   # Pytest fixtures and global configuration
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker configuration for CI/CD
├── docker-compose.yml            # Multi-container setup with DB and Redis
├── .env.example                  # Environment variables template
├── GETTING_STARTED.md            # Detailed getting started guide
└── README.md                     # This file
```

## ⚙️ Quick Setup

### 1. Clone and Install

```bash
git clone https://github.com/ErickFlores13/playwright-python-async-template.git
cd playwright-python-async-template

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/macOS
# or
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### 2. Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your settings
# Minimal configuration:
BASE_URL=https://your-application.com
TEST_USERNAME=test_user
TEST_PASSWORD=test_password
DB_TEST=False  # Set to True only if you need database testing
```

### 3. Run Your First Test

```bash
# Run example tests (headed mode to see browser)
pytest tests/examples/test_login_example.py --headed

# Run all tests
pytest

# Run with Allure report
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

📚 **New to the framework?** Check out [GETTING_STARTED.md](GETTING_STARTED.md) for detailed instructions and examples!

## 🧪 Usage Examples

### Example 1: Test Any Web Application

```python
import pytest
from pages.base_page import BasePage
from utils.config import Config

@pytest.mark.asyncio
async def test_web_app(page):
    """Test any web application."""
    base_page = BasePage(page)
    
    # Navigate to your app
    await page.goto(Config.get_base_url())
    
    # Fill a form
    await base_page.fill_data({
        'input[name="email"]': 'user@example.com',
        'input[name="password"]': 'password123',
    })
    
    # Submit
    await page.click('button[type="submit"]')
    
    # Verify result
    await base_page.is_visible('text=Welcome')
```

### Example 2: Test React/Vue SPA

```python
@pytest.mark.asyncio
async def test_spa(page):
    """Test single-page application."""
    base_page = BasePage(page)
    
    await page.goto('http://localhost:3000')
    
    # Wait for React/Vue to load
    await page.wait_for_selector('[data-testid="app-root"]')
    
    # Interact with components
    await page.click('[data-testid="nav-products"]')
    await base_page.is_visible('[data-testid="products-list"]')
```

### Example 3: Test CRUD Operations

```python
from pages.standard_web_page import StandardWebPage

@pytest.mark.asyncio
async def test_crud(page):
    """Test Create, Read, Update, Delete."""
    web_page = StandardWebPage(page)
    
    # Create
    await page.goto('http://yourapp.com/items/create')
    await web_page.fill_data({
        'input[name="title"]': 'Test Item',
        'input[name="price"]': '99.99',
    })
    await page.click('button[type="submit"]')
    
    # Verify
    await web_page.check_message('Item created successfully')
```

### Example 4: Test with Database Validation (Optional)

```python
@pytest.mark.asyncio
async def test_with_db(page, db_session):
    """Test with database validation (requires DB_TEST=True)."""
    from sqlalchemy import text
    
    # Perform UI action
    # ... your test code ...
    
    # Validate in database
    result = await db_session.execute(
        text("SELECT * FROM items WHERE title = :title"),
        {"title": "Test Item"}
    )
    item = result.fetchone()
    assert item is not None
```

📖 **More examples** in `tests/examples/` directory!

## 🎯 Adapting to Your Application

### Customize for Django

```python
# pages/django_page.py
from pages.standard_web_page import StandardWebPage

class DjangoAdminPage(StandardWebPage):
    def __init__(self, page):
        super().__init__(page)
        # Override Django-specific selectors
        self.submit_button_selector = 'input[name="_save"]'
        self.delete_button_selector = '.deletelink'
```

### Customize for React/Vue

```python
# pages/spa_page.py
from pages.base_page import BasePage

class SPAPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        # Use data-testid attributes
        self.app_root = '[data-testid="app-root"]'
    
    async def wait_for_spa_load(self):
        await self.page.wait_for_selector(self.app_root)
```

### Customize Selectors

Just override the selectors in your page objects:

```python
login_page = LoginPage(page)
login_page.username_selector = '#email'  # Your app uses #email
login_page.password_selector = '#password'
login_page.submit_button_selector = '.login-btn'
```

## 🐳 Docker Support

### Quick Start with Docker

```bash
# Build image
docker build -t playwright-tests .

# Run tests
docker run --rm \
  -e BASE_URL=https://your-app.com \
  -e TEST_USERNAME=test_user \
  -e TEST_PASSWORD=test_pass \
  -v $(pwd)/reports:/app/reports \
  playwright-tests
```

### Using Docker Compose (with PostgreSQL & Redis)

```bash
# Start all services
docker-compose up

# Run only tests
docker-compose run playwright-tests

# With custom environment
BASE_URL=https://your-app.com docker-compose up
```

### CI/CD Integration

**GitHub Actions** workflow is included in `.github/workflows/playwright-tests.yml`:
- Runs tests on multiple browsers (Chromium, Firefox, WebKit)
- Generates Allure reports
- Uploads artifacts on failure
- Supports GitHub Pages deployment for reports

**Jenkins**: Use the Dockerfile or docker-compose.yml in your Jenkinsfile:
```groovy
pipeline {
    agent any
    stages {
        stage('Test') {
            steps {
                sh 'docker-compose up --abort-on-container-exit'
            }
        }
    }
}
```

## 🧱 Framework Architecture

The framework follows the **Page Object Model (POM)** pattern for maintainability and reusability.

### Core Components

| Component | Purpose | When to Use |
|-----------|---------|-------------|
| `BasePage` | Generic browser interactions (click, fill, wait, validate) | For any web testing - base class for all pages |
| `StandardWebPage` | CRUD operations, table validation, filters | For applications with standard forms and tables |
| `LoginPage` | Generic login functionality | Customize for your app's authentication |
| `Config` | Environment-based configuration | Access settings from .env file |
| `consts.py` | Enums and constants | Use predefined validation/filter/button types |

### Page Object Pattern

```python
# 1. Create a page object for your application
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

# 2. Use in tests
@pytest.mark.asyncio
async def test_my_feature(page):
    my_page = MyAppPage(page)
    await my_page.login('user', 'pass')
```

## 🎨 Key Features Explained

### 1. Universal Form Handling

The `fill_data()` method automatically detects field types:
- Text inputs, textareas
- Checkboxes and radio buttons
- Select dropdowns
- File uploads
- Select2 components (if present)

### 2. Smart Waiting

Built-in waiting strategies:
- `wait_for_selector()` - Wait for elements
- `wait_for_load_state()` - Wait for page load
- Automatic waits for Playwright actions

### 3. Comprehensive Validation

Multiple validation methods:
- Form field validation (`fields_validations`)
- Table data validation (`validate_table_data`)
- Message verification (`check_message`)
- Element visibility checks

### 4. Flexible Configuration

Environment-driven configuration:
```python
from utils.config import Config

base_url = Config.get_base_url()
username = Config.get_test_username()
is_headless = Config.is_headless()
```

## 📊 Reporting

### Allure Reports

Allure provides beautiful, interactive test reports:

```bash
# Generate and view report
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

Features:
- ✅ Test execution timeline
- 📸 Screenshots on failure (auto-captured)
- 📊 Test statistics and trends
- 🔍 Detailed error logs
- 📈 Historical data tracking

### Custom Notifications (Optional)

Configure Discord webhook in `.env`:
```bash
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your-webhook
```

## 🔧 Configuration Options

All configuration via `.env` file:

```bash
# Required
BASE_URL=https://your-app.com
TEST_USERNAME=test_user
TEST_PASSWORD=test_password

# Browser settings
BROWSER_TYPE=chromium          # chromium, firefox, webkit
HEADLESS=true                  # true for CI, false for debugging
VIEWPORT_WIDTH=1920
VIEWPORT_HEIGHT=1080

# Optional database testing
DB_TEST=False                  # Enable only if needed
SQL_USER=postgres
SQL_PASSWORD=password
SQL_HOST=localhost
SQL_PORT=5432
SQL_DBNAME=test_db

# Optional Redis testing  
REDIS_HOST=localhost
REDIS_PORT=6379

# Test execution
PYTEST_WORKERS=auto           # Parallel execution workers
TEST_TIMEOUT=30000            # Timeout in milliseconds

# Reporting
ALLURE_RESULTS_DIR=reports/allure-results
SCREENSHOT_ON_FAILURE=true
```

See `.env.example` for complete configuration options.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Playwright](https://playwright.dev/python/)
- Testing with [pytest](https://pytest.org/)
- Reporting with [Allure](https://docs.qameta.io/allure/)

## 📚 Documentation

- [Getting Started Guide](GETTING_STARTED.md) - Detailed setup and usage
- [Example Tests](tests/examples/) - Real-world examples
- [API Documentation](pages/) - Inline code documentation

## 💡 Use Cases

This framework is perfect for:
- ✅ E2E testing of web applications
- ✅ Regression testing
- ✅ CI/CD integration
- ✅ Cross-browser testing
- ✅ Form validation testing
- ✅ CRUD operation testing
- ✅ API + UI combined testing (optional)

## 🐛 Troubleshooting

**Tests timing out?**
- Increase `TEST_TIMEOUT` in `.env`
- Use `--headed` mode to see what's happening

**Import errors?**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Browser not found?**
```bash
playwright install
```

**Need help?**
- Check [GETTING_STARTED.md](GETTING_STARTED.md)
- Review [example tests](tests/examples/)
- Open an issue on GitHub