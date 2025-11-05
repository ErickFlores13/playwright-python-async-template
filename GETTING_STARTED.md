# 🚀 Getting Started Guide

This guide will help you get started with the Playwright Python Async Template for your web automation needs, regardless of what web framework your application uses.

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ErickFlores13/playwright-python-async-template.git
cd playwright-python-async-template
```

### 2. Create a Virtual Environment

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

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers

```bash
playwright install
```

This will download the necessary browser binaries (Chromium, Firefox, WebKit).

### 5. Configure Environment Variables

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

## 🎯 Quick Start Examples

### Example 1: Simple Login Test

Create a file `tests/test_my_app.py`:

```python
import pytest
from pages.login_page import LoginPage
from utils.config import Config


@pytest.mark.asyncio
async def test_login(page):
    """Test basic login functionality."""
    login_page = LoginPage(page)
    
    # Customize selectors for your app
    login_page.username_selector = '#email'
    login_page.password_selector = '#password'
    login_page.submit_button_selector = 'button[type="submit"]'
    
    # Navigate and login
    await page.goto(Config.get_base_url())
    await login_page.login(
        Config.get_test_username(),
        Config.get_test_password()
    )
    
    # Verify login success
    assert await login_page.is_logged_in()
```

Run the test:
```bash
pytest tests/test_my_app.py --headed
```

### Example 2: Test a Form

```python
import pytest
from pages.base_page import BasePage


@pytest.mark.asyncio
async def test_create_item(page):
    """Test creating a new item."""
    base_page = BasePage(page)
    
    await page.goto('https://your-app.com/items/create')
    
    # Fill form data
    form_data = {
        'input[name="title"]': 'Test Item',
        'textarea[name="description"]': 'Test Description',
        'select[name="category"]': 'Category A',
        'input[type="checkbox"]': True,
    }
    
    await base_page.fill_data(form_data)
    await page.click('button[type="submit"]')
    
    # Verify success
    await base_page.is_visible('text=Item created successfully')
```

### Example 3: Test Table Filtering

```python
import pytest
from pages.standard_web_page import StandardWebPage


@pytest.mark.asyncio
async def test_filter_table(page):
    """Test filtering table data."""
    web_page = StandardWebPage(page)
    
    await page.goto('https://your-app.com/items')
    
    # Configure selectors
    web_page.filter_button_selector = 'button:has-text("Filter")'
    
    # Apply filters
    filters = {
        'input[name="search"]': 'Test',
        'select[name="status"]': 'Active',
    }
    
    await web_page.validate_table_data(filters)
```

## 🎨 Customizing for Your Application

### 1. Customize Page Objects

Create a page object specific to your application:

```python
# pages/my_app_page.py
from pages.base_page import BasePage


class MyAppPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        
        # Override selectors for your app
        self.submit_button_selector = '.btn-primary'
        self.delete_button_selector = '.btn-delete'
        
    async def navigate_to_dashboard(self):
        """Custom method for your app."""
        await self.page.click('[data-testid="dashboard-link"]')
        await self.page.wait_for_load_state('networkidle')
```

### 2. Configure for Different Frameworks

#### Django Application
```bash
# .env
BASE_URL=http://localhost:8000
DB_TEST=True
SQL_USER=django_user
SQL_PASSWORD=django_pass
SQL_DBNAME=django_db
```

#### React/Vue SPA
```bash
# .env
BASE_URL=http://localhost:3000
DB_TEST=False
BROWSER_LOCALE=en-US
```

#### Generic Web App
```bash
# .env
BASE_URL=https://your-webapp.com
DB_TEST=False
HEADLESS=false
```

## 🧪 Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_my_app.py
```

### Run with Browser Visible (Headed Mode)
```bash
pytest --headed
```

### Run in Parallel
```bash
pytest -n auto
```

### Run with Allure Report
```bash
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

### Run Specific Test
```bash
pytest tests/test_my_app.py::test_login
```

## 📊 Viewing Reports

### Generate Allure Report
```bash
# Run tests with allure
pytest --alluredir=reports/allure-results

# View report
allure serve reports/allure-results
```

## 🎓 Framework Features

### BasePage Methods

The `BasePage` class provides core functionality:

- `fill_data(data)` - Fill form fields
- `search_with_filters(filters)` - Apply filters
- `edit_item(data)` - Edit existing records
- `delete_item()` - Delete records
- `check_message(message)` - Verify messages
- `is_visible(selector)` - Check element visibility
- `wait_for_selector(selector)` - Wait for elements

### StandardWebPage Methods

The `StandardWebPage` class extends BasePage with additional features:

- `validate_table_data(filters)` - Validate table results
- `validate_no_data_in_table(filters)` - Verify empty results
- `fields_validations(data, selector, type)` - Test form validations
- `validate_filter(type, view, filters)` - Test filter operations
- `validate_button_operations(type, method, data)` - Test cancel/back buttons

### Configuration

Use `Config` class for environment settings:

```python
from utils.config import Config

# Get configuration values
base_url = Config.get_base_url()
username = Config.get_test_username()
is_headless = Config.is_headless()
viewport = Config.get_viewport_size()
```

## 🐳 Running with Docker

### Build Docker Image
```bash
docker build -t playwright-tests .
```

### Run Tests in Container
```bash
docker run --rm \
  -v $(pwd)/reports:/app/reports \
  -e BASE_URL=https://your-app.com \
  playwright-tests
```

## 🔍 Debugging Tests

### Debug Mode
```bash
# Set environment variable
PWDEBUG=1 pytest tests/test_my_app.py --headed
```

### Screenshots
Screenshots are automatically captured on test failure and saved to `screenshots/` directory.

### Verbose Output
```bash
pytest -v -s tests/test_my_app.py
```

## 📝 Best Practices

1. **Use Page Objects**: Encapsulate page-specific logic in page object classes
2. **Use Config**: Store all configuration in `.env` file
3. **Use Descriptive Selectors**: Prefer `data-testid` or semantic selectors
4. **Keep Tests Independent**: Each test should be able to run standalone
5. **Use Fixtures**: Leverage pytest fixtures for setup/teardown
6. **Handle Waits Properly**: Use explicit waits instead of sleep

## 🆘 Troubleshooting

### Browser Not Found
```bash
# Reinstall browsers
playwright install
```

### Import Errors
```bash
# Ensure you're in the project root and virtual environment is activated
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Tests Timing Out
- Increase timeout in `conftest.py`
- Check network connectivity
- Use `--headed` mode to see what's happening

### Database Connection Issues
- Set `DB_TEST=False` if you don't need database testing
- Verify database credentials in `.env`

## 📚 Next Steps

1. Explore the example tests in `tests/examples/`
2. Customize page objects for your application
3. Add your own test cases
4. Set up CI/CD integration
5. Configure Allure reporting

## 🔗 Resources

- [Playwright Documentation](https://playwright.dev/python/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Allure Reports](https://docs.qameta.io/allure/)
- [GitHub Repository](https://github.com/ErickFlores13/playwright-python-async-template)

## 💡 Need Help?

- Check the examples in `tests/examples/`
- Review the API documentation in the code
- Open an issue on GitHub
- Check Playwright documentation

---

**Happy Testing! 🎉**
