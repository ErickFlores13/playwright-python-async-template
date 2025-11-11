# UI Testing Guide

Complete guide for UI testing in this Playwright template. This template provides a powerful Page Object Model (POM) architecture with 70+ reusable methods in `BasePage` and `StandardWebPage`.

---

## Table of Contents
1. [Quick Start](#quick-start)
2. [Page Object Model (POM)](#page-object-model-pom)
3. [Data Generation Pattern](#data-generation-pattern)
4. [Common UI Operations](#common-ui-operations)
5. [CRUD Workflows](#crud-workflows)
6. [Advanced Interactions](#advanced-interactions)
7. [Best Practices](#best-practices)

---

## Quick Start

### Basic Setup

**1. Configure `.env`:**
```bash
BASE_URL=https://your-application.com
TEST_USERNAME=test_user
TEST_PASSWORD=test_password

# Browser Configuration
BROWSER=chromium           # chromium, firefox, webkit
HEADLESS=true             # true for CI, false for debugging
TIMEOUT=30000             # Test timeout in milliseconds
```

**2. Create Your Page Object:**
```python
from pages.standard_web_page import StandardWebPage

class UsersPage(StandardWebPage):
    # Selectors
    first_name_input = "input[name='firstName']"
    create_button = "button.create"
    
    async def create_user(self, name):
        await self.fill_input(self.first_name_input, name)
        await self.page.click(self.create_button)
```

**3. Use in Tests:**
```python
@pytest.mark.asyncio
async def test_create_user(page):
    users_page = UsersPage(page)
    await page.goto("https://example.com/users")
    await users_page.create_user("John Doe")
```

**4. See Examples:**
Check `tests/test_ui_examples.py` for 15+ complete working examples of all UI operations.

---

## Page Object Model (POM)

This template implements **Pure POM** - tests should NEVER contain selectors or direct Playwright calls.

### Architecture Layers

```
BasePage (1,579 lines, 70+ methods)
    ↓
StandardWebPage (793 lines, 30+ methods)
    ↓
Your Page Objects (e.g., UsersPage, ProductsPage)
    ↓
Tests (clean, readable, business-focused)
```

### Why POM?

✅ **Maintainability** - Change selector once, all tests update  
✅ **Readability** - Tests read like business requirements  
✅ **Reusability** - Share methods across multiple pages  
✅ **Testability** - Easy to mock and unit test  

---

### Creating a Page Object

**Step 1: Define Selectors**
```python
from pages.standard_web_page import StandardWebPage

class ProductsPage(StandardWebPage):
    # Form selectors
    product_name_input = "input[name='productName']"
    price_input = "input[name='price']"
    category_select = "select[name='category']"
    active_checkbox = "input[name='active']"
    
    # Action selectors
    save_button = "button.save"
    search_button = "button.search"
    delete_button = "button.delete"
    
    # Table/Validation selectors
    products_table = "table.products"
    no_data_message = ".no-data-message"
```

**Step 2: Add High-Level Methods**
```python
    async def create_product(self, name, price, category):
        """Create a new product."""
        await self.fill_input(self.product_name_input, name)
        await self.fill_input(self.price_input, str(price))
        await self.select_dropdown_option(self.category_select, category)
        await self.page.click(self.save_button)
    
    async def search_by_name(self, name):
        """Search for product by name."""
        await self.fill_input(self.product_name_input, name)
        await self.page.click(self.search_button)
    
    async def is_product_visible_in_table(self, product_name):
        """Check if product appears in results table."""
        return await self.is_visible(f"{self.products_table} td:has-text('{product_name}')")
```

**Step 3: Use in Tests**
```python
@pytest.mark.asyncio
async def test_product_creation(page):
    products_page = ProductsPage(page)
    await page.goto("https://example.com/products")
    
    # Clean, readable test
    await products_page.create_product("Laptop", 1299.99, "Electronics")
    await products_page.search_by_name("Laptop")
    
    assert await products_page.is_product_visible_in_table("Laptop")
```

---

## Data Generation Pattern

The **data generation pattern** is the recommended approach for managing test data. It centralizes data creation in Page Objects and uses random generation for test isolation.

### Implementation

**In Your Page Object:**
```python
from utils.test_helpers import TestDataGenerator
import random

class UsersPage(StandardWebPage):
    # Selectors
    first_name_input = "input[name='firstName']"
    last_name_input = "input[name='lastName']"
    email_input = "input[name='email']"
    role_select = "select[name='role']"
    
    def __init__(self, page):
        super().__init__(page)
        # Storage for generated data
        self.data = None
        self.data_filters = None
    
    async def generate_user_data(self, **kwargs):
        """
        Generate random user data with optional overrides.
        
        Args:
            **kwargs: Override specific fields (first_name, email, etc.)
        """
        # Random defaults
        first_name = kwargs.get('first_name', TestDataGenerator.random_string(8).title())
        last_name = kwargs.get('last_name', TestDataGenerator.random_string(10).title())
        email = kwargs.get('email', TestDataGenerator.random_email())
        role = kwargs.get('role', random.choice(['User', 'Admin', 'Manager']))
        
        # Store in dictionaries (selector: value)
        self.data = {
            self.first_name_input: first_name,
            self.last_name_input: last_name,
            self.email_input: email,
            self.role_select: role,
        }
        
        # Filters use different selectors
        self.data_filters = {
            "input[name='filterFirstName']": first_name,
            "input[name='filterEmail']": email,
        }
```

**In Your Tests:**
```python
@pytest.mark.asyncio
async def test_user_creation(page):
    users_page = UsersPage(page)
    await page.goto("https://example.com/users")
    
    # Generate random data
    await users_page.generate_user_data()
    
    # Use generated data
    await users_page.fill_data(users_page.data)  # BasePage method
    await users_page.click_save_button()
    
    # Search with same data
    await users_page.search_with_filters(users_page.data_filters)  # StandardWebPage method
    
    # Verify
    await users_page.validate_table_data(
        data_filters=users_page.data_filters,
        filter_button_selector=users_page.search_button,
        table_selector=users_page.users_table
    )

@pytest.mark.asyncio
async def test_specific_user(page):
    users_page = UsersPage(page)
    await page.goto("https://example.com/users")
    
    # Override specific fields
    await users_page.generate_user_data(
        first_name="Admin",
        email="admin@example.com",
        role="Administrator"
    )
    
    await users_page.fill_data(users_page.data)
```

### Benefits

✅ **Test Isolation** - Each test uses unique random data  
✅ **Flexibility** - Override specific fields when needed  
✅ **Reusability** - Same data for create/search/validate  
✅ **Maintainability** - Data logic in one place  

---

## Common UI Operations

BasePage provides 70+ methods. Here are the most commonly used:

### Element Visibility

```python
# Check if element is visible
is_visible = await page_object.is_visible("button.submit")

# Check if element is hidden
is_hidden = await page_object.is_hidden(".loading-spinner")

# Wait for element
await page_object.wait_for_selector(".dashboard-content", timeout=30000)
```

### Form Interactions

```python
# Fill text input
await page_object.fill_input("input[name='username']", "johndoe")

# Select dropdown option
await page_object.select_dropdown_option("select[name='country']", "United States")

# Check/uncheck checkbox
await page_object.check_checkbox("input[name='terms']")
await page_object.uncheck_checkbox("input[name='newsletter']")

# Upload file
await page_object.upload_file("input[type='file']", "/path/to/file.pdf")
```

### Text Extraction

```python
# Get text content
username = await page_object.get_text(".username-display")

# Get attribute value
href = await page_object.get_attribute("a.profile-link", "href")

# Get all text from multiple elements
names = await page_object.get_all_text("table tr td:first-child")
```

### Mouse Actions

```python
# Hover
await page_object.hover(".menu-item")

# Double-click
await page_object.double_click(".file-item")

# Right-click
await page_object.right_click(".context-menu-trigger")

# Drag and drop
await page_object.drag_and_drop(
    source_selector=".draggable-item",
    target_selector=".drop-zone"
)
```

### Checkboxes & State

```python
# Check if checkbox is checked
is_active = await page_object.is_checked("input[name='active']")

# Toggle checkbox
await page_object.check_checkbox("input[name='subscribe']")
```

### Screenshots

```python
# Full page screenshot
screenshot_path = await page_object.take_screenshot("test_name")

# Element screenshot
await page_object.take_element_screenshot(".error-message", "error_state")
```

### Dialogs

```python
# Handle confirmation dialog
dialog_text = await page_object.handle_confirmation_dialog(
    trigger_action=lambda: page.click("button.delete"),
    accept=True  # True = OK, False = Cancel
)

# Handle prompt dialog
input_text = await page_object.handle_prompt_dialog(
    trigger_action=lambda: page.click("button.rename"),
    input_text="New Name"
)
```

### Downloads

```python
# Download file
file_path = await page_object.download_file(
    download_trigger_selector="button.download",
    expected_filename="report.pdf"
)
```

### Navigation

```python
# Go back
await page_object.go_back()

# Refresh page
await page_object.refresh_page()

# Wait for page load
await page_object.wait_for_page_load()
```

### Cookies & Storage

```python
# Set cookie
await page_object.set_cookie(
    name="session_token",
    value="abc123",
    domain="example.com"
)

# Get cookie
cookie = await page_object.get_cookie("session_token")

# Local storage
await page_object.set_local_storage("user_prefs", '{"theme": "dark"}')
prefs = await page_object.get_local_storage("user_prefs")

# Clear all storage
await page_object.clear_all_storage()
```

### Scrolling

```python
# Scroll element into view
await page_object.scroll_into_view(".footer-content")

# Scroll to bottom
await page_object.scroll_to_bottom()
```

---

## CRUD Workflows

`StandardWebPage` provides high-level workflow methods for common CRUD operations.

### Create Item

```python
@pytest.mark.asyncio
async def test_create(page):
    users_page = UsersPage(page)
    await page.goto("https://example.com/users")
    
    # Generate data
    await users_page.generate_user_data()
    
    # Create workflow: fill form + click save + verify success
    await users_page.create_item_workflow(
        form_data=users_page.data,
        create_button_selector=users_page.save_button,
        success_message_selector=".alert-success"
    )
```

### Search/Filter

```python
@pytest.mark.asyncio
async def test_search(page):
    users_page = UsersPage(page)
    await page.goto("https://example.com/users")
    
    # Search workflow: fill filters + click search
    await users_page.search_with_filters(
        data_filters=users_page.data_filters,
        filter_button_selector=users_page.search_button
    )
```

### Edit Item

```python
@pytest.mark.asyncio
async def test_edit(page):
    users_page = UsersPage(page)
    await page.goto("https://example.com/users")
    
    # Edit workflow: click edit + fill form + save
    await users_page.edit_item_workflow(
        edit_data={"input[name='role']": "Manager"},
        edit_button_selector=users_page.edit_button,
        save_button_selector=users_page.save_button,
        success_message_selector=".alert-success"
    )
```

### Delete Item

```python
@pytest.mark.asyncio
async def test_delete(page):
    users_page = UsersPage(page)
    await page.goto("https://example.com/users")
    
    # Delete workflow: click delete + confirm
    await users_page.delete_item(
        delete_button_selector=users_page.delete_button,
        confirm_delete_button_selector="button.confirm-delete"
    )
```

### Validate Table Data

```python
@pytest.mark.asyncio
async def test_validate_table(page):
    users_page = UsersPage(page)
    await page.goto("https://example.com/users")
    
    # Generate and create user
    await users_page.generate_user_data(first_name="John")
    await users_page.create_item_workflow(...)
    
    # Validate appears in table
    await users_page.validate_table_data(
        data_filters=users_page.data_filters,
        filter_button_selector=users_page.search_button,
        table_selector=users_page.users_table
    )
```

### Validate No Data

```python
@pytest.mark.asyncio
async def test_validate_deleted(page):
    users_page = UsersPage(page)
    await page.goto("https://example.com/users")
    
    # After deletion, verify not in table
    await users_page.validate_no_data_in_table(
        data_filters=users_page.data_filters,
        filter_button_selector=users_page.search_button,
        no_data_selector=users_page.no_data_message
    )
```

---

## Advanced Interactions

### Tab Management

```python
@pytest.mark.asyncio
async def test_multiple_tabs(page):
    users_page = UsersPage(page)
    await page.goto("https://example.com/users")
    
    # Open link in new tab
    async with page.context.expect_page() as new_page_info:
        await page.click("a[target='_blank']")
    
    new_page = await new_page_info.value
    
    # Switch to new tab
    await users_page.switch_to_new_tab()
    
    # Work in new tab...
    
    # Close tab
    await users_page.close_current_tab()
```

### Dynamic Elements

```python
# Wait for element to appear
await page_object.wait_for_selector(".dynamic-content", timeout=10000)

# Wait for element to disappear
await page_object.wait_for_selector_hidden(".loading-spinner", timeout=30000)

# Wait for text to appear
await page_object.wait_for_text("Welcome back!", timeout=5000)
```

### Iframes

```python
# Switch to iframe
await page_object.switch_to_frame("iframe#payment-form")

# Work inside iframe...
await page_object.fill_input("input[name='cardNumber']", "4242424242424242")

# Switch back to main content
await page_object.switch_to_default_content()
```

### Table Operations

```python
# Extract all table data
table_data = await page_object.extract_table_data(
    table_selector="table.users",
    headers=["Name", "Email", "Role"]
)

# Find row by criteria
row_index = await page_object.find_table_row_by_criteria(
    table_selector="table.users",
    criteria={"Email": "john@example.com"}
)

# Click action in specific row
await page_object.click_table_row_action(
    table_selector="table.users",
    row_criteria={"Name": "John Doe"},
    action_selector="button.edit"
)
```

### Pagination

```python
# Extract data from all pages
all_data = await page_object.extract_all_paginated_data(
    table_selector="table.users",
    next_button_selector="button.next-page",
    max_pages=10
)

# Search across pages
results = await page_object.search_across_all_pages(
    search_criteria={"Email": "john@example.com"},
    table_selector="table.users",
    next_button_selector="button.next-page",
    max_pages=20
)
```

### Select2 Dropdowns

```python
# Select option in Select2 dropdown
await page_object.select_option_in_select2(
    select_selector="#country-select",
    option_text="United States"
)

# Multi-select in Select2
await page_object.select_multiple_in_select2(
    select_selector="#tags-select",
    options=["Python", "JavaScript", "TypeScript"]
)
```

---

## Best Practices

### ✅ DO

**1. Use Pure POM - No Selectors in Tests**
```python
# Good ✅
@pytest.mark.asyncio
async def test_login(page):
    login_page = LoginPage(page)
    await login_page.login("user@example.com", "password123")
    assert await login_page.is_logged_in()

# Bad ❌
@pytest.mark.asyncio
async def test_login(page):
    await page.fill("input[name='username']", "user@example.com")  # Direct selector
    await page.click("button[type='submit']")  # Direct selector
```

**2. Use Data Generation Pattern**
```python
# Good ✅
await users_page.generate_user_data()
await users_page.fill_data(users_page.data)

# Bad ❌
await page.fill("input[name='firstName']", "John")  # Hardcoded data
await page.fill("input[name='lastName']", "Doe")
```

**3. Create High-Level Workflow Methods**
```python
# Good ✅
async def create_user_workflow(self, **kwargs):
    """Complete user creation workflow."""
    await self.generate_user_data(**kwargs)
    await self.fill_data(self.data)
    await self.click_save_button()
    await self.verify_success_message()

# Then in test:
await users_page.create_user_workflow(role="Admin")

# Bad ❌ - Too many low-level steps in test
await users_page.fill_input(...)
await users_page.select_dropdown(...)
await page.click(...)
await page.wait_for_selector(...)
```

**4. Use Descriptive Method Names**
```python
# Good ✅
async def is_user_profile_visible(self):
    return await self.is_visible(self.user_profile_selector)

async def search_by_email(self, email):
    await self.fill_input(self.email_filter_input, email)
    await self.page.click(self.search_button)

# Bad ❌
async def check(self):
    return await self.is_visible(self.selector)
```

**5. Wait for Page Loads**
```python
# Good ✅
await page_object.wait_for_page_load()
await page_object.wait_for_selector(".dashboard-content")

# Bad ❌
await asyncio.sleep(2)  # Arbitrary wait
```

**6. Use Parameterized Selectors for Similar Elements**
```python
# Good ✅
async def click_menu_item(self, item_name):
    selector = f"nav .menu-item:has-text('{item_name}')"
    await self.page.click(selector)

# Usage
await page_object.click_menu_item("Settings")
await page_object.click_menu_item("Profile")

# Bad ❌ - Separate method for each menu item
async def click_settings(self): ...
async def click_profile(self): ...
```

---

### ❌ DON'T

**1. Don't Mix Test Logic with Page Objects**
```python
# Bad ❌ - Assertions in Page Object
async def create_user(self, name):
    await self.fill_input(self.name_input, name)
    assert await self.is_visible(".success")  # DON'T

# Good ✅ - Assertions in test
@pytest.mark.asyncio
async def test_create_user(page):
    users_page = UsersPage(page)
    await users_page.create_user("John")
    assert await users_page.is_success_visible()  # Assertion in test
```

**2. Don't Hardcode URLs in Page Objects**
```python
# Bad ❌
async def navigate_to_users(self):
    await self.page.goto("https://example.com/users")

# Good ✅
@pytest.mark.asyncio
async def test_users(page):
    users_page = UsersPage(page)
    await page.goto(f"{os.getenv('BASE_URL')}/users")
    await users_page.create_user(...)
```

**3. Don't Use Overly Complex Selectors**
```python
# Bad ❌
complex_selector = "div.container > div:nth-child(3) > table > tbody > tr:first-child > td:nth-child(2)"

# Good ✅
# Ask developers to add data-testid attributes
simple_selector = "[data-testid='user-email']"

# Or use more stable selectors
text_selector = "table tr:has-text('john@example.com') td.email"
```

**4. Don't Repeat Yourself (DRY)**
```python
# Bad ❌ - Repeated code
async def create_admin(self):
    await self.fill_input(self.name_input, "Admin")
    await self.select_dropdown_option(self.role_select, "Administrator")
    await self.page.click(self.save_button)

async def create_user(self):
    await self.fill_input(self.name_input, "User")
    await self.select_dropdown_option(self.role_select, "Regular User")
    await self.page.click(self.save_button)

# Good ✅ - Parameterized method
async def create_user_with_role(self, name, role):
    await self.fill_input(self.name_input, name)
    await self.select_dropdown_option(self.role_select, role)
    await self.page.click(self.save_button)
```

---

## Summary

This Playwright template provides **production-ready UI testing** with:

✅ **Pure POM Architecture** - 70+ methods in BasePage, 30+ in StandardWebPage  
✅ **Data Generation Pattern** - Random data with TestDataGenerator  
✅ **High-Level Workflows** - CRUD operations, search, validation  
✅ **Advanced Interactions** - Tabs, dialogs, downloads, drag-and-drop  
✅ **Robust Waiting** - Smart waits, no hardcoded sleeps  
✅ **Screenshot Support** - Automatic capture on failure  
✅ **Multi-Browser** - Chromium, Firefox, WebKit support  
✅ **CI/CD Ready** - Headless mode, parallel execution  

---

## Reference

### Key Files

```bash
pages/
├── base_page.py              # 70+ core methods (visibility, forms, mouse, etc.)
├── standard_web_page.py      # 30+ workflow methods (CRUD, filters, tables)
├── login_page.py             # Generic login implementation
└── examples/
    └── demo_page.py          # Complete example with data generation

tests/
└── test_ui_examples.py       # 15 working examples

utils/
├── test_helpers.py           # TestDataGenerator utility
└── config.py                 # Configuration management
```

### Environment Variables

```bash
# Required
BASE_URL=https://your-app.com
TEST_USERNAME=test_user
TEST_PASSWORD=test_password

# Optional
BROWSER=chromium              # chromium, firefox, webkit
HEADLESS=true                 # true/false
TIMEOUT=30000                 # milliseconds
VIEWPORT_WIDTH=1920
VIEWPORT_HEIGHT=1080
SCREENSHOT_ON_FAILURE=true    # Auto-screenshot on test failure
```

### Running Tests

```bash
# Run all UI tests
pytest tests/test_ui_examples.py

# Run specific test
pytest tests/test_ui_examples.py::test_complete_crud_workflow

# Run with headed browser (see browser)
HEADLESS=false pytest tests/test_ui_examples.py

# Run with specific browser
BROWSER=firefox pytest tests/test_ui_examples.py

# Parallel execution
pytest tests/ -n auto

# Generate HTML report
pytest tests/ --html=report.html

# Generate Allure report
pytest tests/ --alluredir=allure-results
allure serve allure-results
```

---

**Need Help?**
- See `tests/test_ui_examples.py` for 15 complete examples
- See `pages/examples/demo_page.py` for data generation implementation
- See `pages/base_page.py` for all available methods
- Check existing page objects in your project for patterns

---

*Author: Erick Guadalupe Félix Flores*  
*License: MIT*
