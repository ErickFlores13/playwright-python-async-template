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
- 🔹 **Automatic reporting:** Screenshots on failure
- 🔹 **Async by default:** Fully asynchronous for better performance
- 🔹 **Parallel execution:** Run tests in parallel using `pytest-xdist`
- 🔹 **Docker support:** Containerized execution for consistent environments
- 🔹 **Example tests included:** Comprehensive examples for different use cases

---

## 🚀 Getting Started

### 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### 🔧 Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/ErickFlores13/playwright-python-async-template.git
cd playwright-python-async-template
```

#### 2. Create a Virtual Environment

**Linux / macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Install Playwright Browsers

```bash
playwright install
```

This will download the necessary browser binaries (Chromium, Firefox, WebKit).

#### 5. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and configure for your application:

**Minimal Configuration:**
```bash
# Required
BASE_URL=https://your-application.com
TEST_USERNAME=your_test_user
TEST_PASSWORD=your_test_password

# Optional - disable if not needed
DB_TEST=False
```

---

## 🏗️ Project Structure

```bash
.
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
└── README.md                     # This file
```

### 🎯 Quick Start

First, run the framework validation to ensure everything is configured correctly:

```bash
# This test runs without @pytest.mark.skip and validates your setup
pytest tests/examples/test_complete_real_world_example.py::test_framework_configuration_validation -v
```

Run basic configuration tests (these work with any setup):

```bash
pytest tests/examples/test_configuration_and_utilities.py -v
```

### 🔧 Run Example Tests

All example tests have `@pytest.mark.skip` decorators. To use them:

1. **Remove the skip decorator**
2. **Customize selectors for your application**
3. **Run the tests**

```bash
# Run example tests (headed mode to see browser)
pytest tests/examples/ --headed

# Run specific test
pytest tests/examples/test_base_page_features.py -v
```

## 📚 Framework Examples & Usage

### 🎯 Overview

The framework provides comprehensive examples demonstrating every feature, organized into focused test files that showcase specific aspects of the framework.

### 📁 Example Files Structure

```
tests/examples/
├── test_base_page_features.py              # Core BasePage functionality
├── test_standard_web_page_features.py      # CRUD operations with StandardWebPage
├── test_backend_integration.py             # Database and Redis integration
├── test_configuration_and_utilities.py     # Configuration and utilities
├── test_complete_real_world_example.py     # Complete e-commerce example
└── __init__.py                             # Package initialization
```

### 🚀 Running Examples

#### Framework Validation
Run this first to ensure everything is configured correctly:

```bash
pytest tests/examples/test_complete_real_world_example.py::test_framework_configuration_validation -v
```

#### Configuration Tests
Basic tests that work with any setup:

```bash
pytest tests/examples/test_configuration_and_utilities.py -v
```

#### Custom Examples
All other example tests have `@pytest.mark.skip` decorators. To use them:

1. **Remove the skip decorator**
2. **Customize selectors for your application**
3. **Run the tests**

### 📋 Example Categories

#### 🔧 BasePage Features (`test_base_page_features.py`)

Demonstrates core page object functionality:

- **Form handling**: All input types (text, select, checkbox, radio, file upload)
- **Element interactions**: Click, wait, visibility checks
- **Select2 components**: Advanced dropdown handling
- **Screenshots**: Debugging and failure capture
- **Waiting mechanisms**: Various wait strategies
- **Error handling**: Exception handling and validation

**Key Methods Demonstrated:**
```python
await page_object.fill_data(form_data)              # Universal form filling
await page_object.is_visible(selector)              # Element visibility
await page_object.wait_for_selector(selector)       # Smart waiting
await page_object.take_screenshot(name)             # Screenshot capture
await page_object.select2_select(selector, option)  # Select2 handling
```

**To Use:**
1. Create your page object extending `BasePage`
2. Customize selectors in your `__init__` method
3. Use the demonstrated patterns for your forms

#### 📊 StandardWebPage Features (`test_standard_web_page_features.py`)

Demonstrates CRUD operations and business logic:

- **Create operations**: Form filling and submission
- **Read operations**: Table validation and searching
- **Update operations**: Editing existing records
- **Delete operations**: Confirmation dialogs and cleanup
- **Filtering**: Advanced search and filter combinations
- **Validation**: Form field validation testing
- **Navigation**: Button operations and page flow

**Key Methods Demonstrated:**
```python
await crud_page.search_with_filters(filters)        # Search functionality
await crud_page.validate_table_data(expected)       # Table validation
await crud_page.fields_validations(data, field, type) # Form validation
await crud_page.cancel_button_operations(operation) # Navigation
await crud_page.check_message(message)              # Success/error messages
```

#### 🎯 Quick Usage Examples

**Example 1: Create Page Object for Your Module**

```python
# pages/my_module_page.py
from pages.standard_web_page import StandardWebPage

class MyModulePage(StandardWebPage):
    """Page Object for My Module."""

    def __init__(self, page):
        super().__init__(page)

        # Define selectors for your module
        self.name_input = 'input[name="name"]'
        self.email_input = 'input[name="email"]'
        self.submit_button_selector = 'button[type="submit"]'

    async def navigate_to_module(self, base_url):
        """Navigate to the module."""
        await self.page.goto(f"{base_url}/my-module")

    async def create_item(self, item_data):
        """Create a new item."""
        form_data = {
            self.name_input: item_data['name'],
            self.email_input: item_data['email'],
        }
        await self.fill_data(form_data)
        await self.page.click(self.submit_button_selector)
```

**Example 2: Test React/Vue SPA**

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

**Example 3: Test CRUD Operations**

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

# Basic settings
base_url = Config.get_base_url()
username = Config.get_test_username()
password = Config.get_test_password()

# Browser settings
browser_type = Config.get_browser_type()  # chromium, firefox, webkit
is_headless = Config.is_headless()
timeout = Config.get_test_timeout()

# Optional features
db_enabled = Config.is_db_testing_enabled()
custom_url = Config.get_custom_url('ADMIN_USUARIOS_URL')
```

## 📊 Reporting

### Screenshots on Failure

The framework automatically captures screenshots when tests fail for easier debugging.

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

# Application URLs (customize for your specific app)
ADMIN_USUARIOS_URL=https://your-admin-url.com
ADMIN_USUARIOS_CENTRAL_URL=https://your-central-admin-url.com
ADMIN_USUARIOS_LOCAL_A_URL=https://your-local-a-admin-url.com
ADMIN_USUARIOS_LOCAL_B_URL=https://your-local-b-admin-url.com

# Browser settings
BROWSER=chromium               # chromium, firefox, webkit
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
REDIS_DB=0

# Test execution
PYTEST_WORKERS=auto           # Parallel execution workers
TIMEOUT=30000                 # Timeout in milliseconds

# Reporting
SCREENSHOT_ON_FAILURE=true

# Optional Discord notifications
DISCORD_WEBHOOK_URL=your_discord_webhook_url_here
```

See `.env.example` for complete configuration options.

### Configuration Validation

The framework validates required configuration on startup:

```python
from utils.config import Config

# This will raise ValueError if BASE_URL is not set
Config.validate_required_config()

# Get all current configuration (useful for debugging)
all_config = Config.get_all_config()
print(all_config)
```

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
- [Examples Documentation](EXAMPLES.md) - Comprehensive framework examples  
- [Example Tests](tests/examples/) - Real-world example code
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