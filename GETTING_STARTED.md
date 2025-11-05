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

### Example 1: Create Page Object for Your Module

First, create a page object class for your module:

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

### Example 2: Write Test Using Page Object

Then write tests that only call page object methods:

```python
# tests/test_my_module.py
import pytest
from pages.my_module_page import MyModulePage
from utils.config import Config

@pytest.mark.asyncio
async def test_create_item(page):
    """Test creating an item using page object."""
    # Initialize page object
    my_page = MyModulePage(page)
    base_url = Config.get_base_url()
    
    # Navigate using page object method
    await my_page.navigate_to_module(base_url)
    
    # Create item using page object method
    item_data = {
        'name': 'Test Item',
        'email': 'test@example.com',
    }
    await my_page.create_item(item_data)
    
    # Verify using page object method
    await my_page.verify_success_message('Item created')
```

Run the test:
```bash
pytest tests/test_my_module.py --headed
```

### Example 3: Login Test with Page Object

```python
import pytest
from pages.examples.authentication_page import AuthenticationPage
from utils.config import Config

@pytest.mark.asyncio
async def test_login(page):
    """Test login using page object."""
    # Initialize page object
    auth_page = AuthenticationPage(page)
    
    # Customize selectors if needed
    auth_page.username_selector = '#email'
    auth_page.password_selector = '#password'
    
    # Perform login using page object method
    await auth_page.perform_login(
        Config.get_test_username(),
        Config.get_test_password(),
        Config.get_base_url()
    )
    
    # Verify using page object method
    assert await auth_page.verify_login_success()
```

### Example 4: CRUD Operations with Page Object

```python
import pytest
from pages.examples.user_management_page import UserManagementPage
from utils.config import Config

@pytest.mark.asyncio
async def test_user_crud(page):
    """Test complete CRUD flow using page object."""
    # Initialize page object
    user_page = UserManagementPage(page)
    base_url = Config.get_base_url()
    
    # Navigate
    await user_page.navigate_to_module(base_url)
    
    # Create
    user_data = {
        'username': 'test_user',
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'role': 'Admin',
    }
    await user_page.create_user(user_data)
    await user_page.verify_success_message('User created')
    
    # Read/Search
    await user_page.search_user({'username': 'test_user'})
    
    # Update
    await user_page.edit_user({'role': 'Manager'})
    await user_page.verify_success_message('User updated')
    
    # Delete
    await user_page.delete_user()
    await user_page.verify_success_message('User deleted')
```

## 🎨 Customizing for Your Application

### 1. Create Page Objects for Your Modules

Always create a page object class that extends StandardWebPage:

```python
# pages/my_custom_module_page.py
from pages.standard_web_page import StandardWebPage

class MyCustomModulePage(StandardWebPage):
    """Page Object for your custom module."""
    
    def __init__(self, page):
        super().__init__(page)
        
        # Define ALL selectors for this module
        self.field1_input = 'input[name="field1"]'
        self.field2_select = 'select[name="field2"]'
        
        # Override base selectors if needed
        self.submit_button_selector = 'button.my-submit'
        self.table_selector = '#my-table'
    
    async def navigate_to_module(self, base_url):
        """Navigate to this module."""
        await self.page.goto(f"{base_url}/my-module")
    
    async def perform_module_action(self, data):
        """Custom action for this module."""
        # Implement your module-specific logic
        pass
```

### 2. Use Page Objects in Tests

Tests should ONLY call page object methods:

```python
# tests/test_my_module.py
import pytest
from pages.my_custom_module_page import MyCustomModulePage
from utils.config import Config

@pytest.mark.asyncio
async def test_my_module(page):
    """Test using page object - NO direct page interaction."""
    # Initialize page object
    my_page = MyCustomModulePage(page)
    
    # All actions through page object methods
    await my_page.navigate_to_module(Config.get_base_url())
    await my_page.perform_module_action(data)
    await my_page.verify_success_message('Success')
```

### 3. Page Object Model Best Practices

**✅ DO:**
- Create a page object class for each module
- Put ALL selectors in the page object
- Create methods for ALL actions
- Tests ONLY call page object methods
- Extend StandardWebPage for CRUD modules

**❌ DON'T:**
- Use selectors directly in test files
- Call page.click(), page.fill() in tests
- Mix page logic with test logic

## 🎯 Framework Components

### For Different Application Types

#### Django Application

Create page object extending StandardWebPage:
```python
# pages/django_admin_page.py
from pages.standard_web_page import StandardWebPage

class DjangoAdminPage(StandardWebPage):
    def __init__(self, page):
        super().__init__(page)
        self.submit_button_selector = 'input[name="_save"]'
        # Add Django-specific methods
```

Configuration:
```bash
# .env
BASE_URL=http://localhost:8000
DB_TEST=True
SQL_USER=django_user
SQL_PASSWORD=django_pass
SQL_DBNAME=django_db
```

#### React/Vue SPA

Create page object for SPA:
```python
# pages/spa_page.py
from pages.base_page import BasePage

class SPAPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.app_root = '[data-testid="app-root"]'
    
    async def wait_for_app_load(self):
        await self.wait_for_selector(self.app_root)
```

Configuration:
```bash
# .env
BASE_URL=http://localhost:3000
DB_TEST=False
BROWSER_LOCALE=en-US
```

#### Generic Web App

Use base page objects and extend as needed:
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
