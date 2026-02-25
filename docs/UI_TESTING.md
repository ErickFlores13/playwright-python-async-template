# UI Testing Guide

Complete guide for UI automation using the Playwright Python Async Framework.

> **Quick reference?** See [core/ui/README.md](../core/ui/README.md)  
> **AI-powered healing?** See [core/ui/ai/README.md](../core/ui/ai/README.md)

---

## Table of Contents

- [Overview](#overview)
- [Page Object Model](#page-object-model)
- [Form Interactions](#form-interactions)
- [Validation](#validation)
- [Browser Services](#browser-services)
- [Components Reference](#components-reference)
- [Test Markers](#test-markers)
- [Configuration](#configuration)
- [Complete Examples](#complete-examples)

---

## Overview

The UI testing layer is built on top of **Playwright** and follows the **Page Object Model (POM)** pattern. Every page object inherits from `BasePage`, which provides lazy-loaded services and convenience shortcuts.

```
BasePage
├── fill_data()          ← Auto-detecting form filler
├── edit_item()          ← Clear + refill
├── validate_edit_view() ← Assert form field values
├── validate_details_view() ← Assert read-only view
│
├── Services (accessed via self.<service>)
│   ├── attribute        ← DOM attribute manipulation
│   ├── element_resolver ← Element resolution & metadata
│   ├── strategy_factory ← Form-filling strategies
│   ├── screenshot       ← Evidence capture
│   ├── storage          ← LocalStorage / SessionStorage / Cookies
│   ├── tab_window       ← Multi-tab management
│   ├── validation       ← Element assertions
│   └── wait             ← Page-load waiting
```

---

## Page Object Model

### Creating a Page Object

Every page object must inherit from `BasePage` and call `super().__init__(page)`:

```python
from playwright.async_api import Page
from core.ui.base_page import BasePage

class ProductPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)          # Required!

        # Define selectors as instance variables
        self.search_input   = '#search'
        self.search_button  = '#searchBtn'
        self.results_list   = '.results-item'
        self.add_to_cart    = '[data-testid="add-cart"]'

    async def search(self, query: str) -> None:
        await self.fill_data({self.search_input: query})
        await self.page.click(self.search_button)
        await self.wait.wait_for_page_load()

    async def result_count(self) -> int:
        return await self.page.locator(self.results_list).count()
```

### Using in Tests

```python
async def test_product_search(page):
    await page.goto('https://shop.example.com/products')
    product_page = ProductPage(page)

    await product_page.search('laptop')

    count = await product_page.result_count()
    assert count > 0
```

---

## Form Interactions

### `fill_data()` — Create / Fill

Automatically detects the field type and uses the correct interaction strategy:

```python
await self.fill_data({
    '#name':            'John Doe',           # Text input
    '#email':           'john@example.com',   # Email input
    '#age':             '30',                 # Number input
    '#department':      'Engineering',        # <select> dropdown
    '#country':         'United States',      # Select2 dropdown
    '#active':          True,                 # Checkbox (check)
    '#premium':         False,                # Checkbox (uncheck)
    '#employment':      'full-time',          # Radio button (by value)
    '#start_date':      '2024-01-15',         # Date picker (YYYY-MM-DD)
    '#resume':          '/abs/path/file.pdf', # File upload (absolute path)
    '#submit':          'click',              # Button click
    '.benefits':        ['Health', 'Dental'], # Multiple checkboxes
})
```

### `edit_item()` — Clear and Refill

Clears existing values before filling. Use this when editing a form:

```python
await self.edit_item({
    '#name':       'Jane Smith',
    '#department': 'Marketing',
})
```

### `validate_edit_view()` — Assert Form Field Values

Checks that form fields contain the expected values:

```python
await self.validate_edit_view({
    '#name':       'Jane Smith',
    '#department': 'Marketing',
    '#active':     True,
})
```

### `validate_details_view()` — Assert Read-Only View

Checks that container elements display expected text:

```python
await self.validate_details_view({
    '#div_id_name':       'Jane Smith',
    '#div_id_department': 'Marketing',
    '#div_id_email':      'jane@example.com',
})
```

---

## Validation

The `validation` service provides assertion helpers:

```python
# Element state
await self.validation.assert_visible('#successMessage')
await self.validation.assert_not_visible('#errorMessage')

# Checkbox state
await self.validation.assert_checked('#agreeTerms')
await self.validation.assert_not_checked('#newsletter')

# Input value
await self.validation.assert_value('#username', 'john_doe')

# Message content
await self.validation.validate_message('#flash', 'Saved successfully', exact=False)

# Details view (shortcut to validate_details_view)
await self.validation.validate_record_information_in_details_view({
    '#div_id_name': 'John Doe',
})
```

---

## Browser Services

### `wait` — Smart Page Loading

```python
# Wait for page to finish loading (networkidle with domcontentloaded fallback)
await self.wait.wait_for_page_load()

# With custom timeout (milliseconds)
await self.wait.wait_for_page_load(timeout=60_000)
```

For element-level waits, use Playwright directly:

```python
await self.page.locator('#result').wait_for(state='visible', timeout=10_000)
```

### `screenshot` — Evidence Capture

```python
# Full-page screenshot (auto-timestamped, saved to screenshots/)
await self.screenshot.take_screenshot('before_submit')

# Element screenshot
await self.screenshot.take_element_screenshot('#error-banner', 'error_state')
```

### `storage` — Browser Storage

```python
# LocalStorage
await self.storage.set_local_storage('theme', 'dark')
theme = await self.storage.get_local_storage('theme')
await self.storage.clear_local_storage()

# SessionStorage
await self.storage.set_session_storage('temp_id', '42')
value = await self.storage.get_session_storage('temp_id')

# Cookies
await self.storage.add_cookie({'name': 'session', 'value': 'abc123', 'url': 'https://app.com'})
cookies = await self.storage.get_all_cookies()
await self.storage.clear_cookies()
```

### `tab_window` — Multi-Tab Management

```python
# Wait for a new tab to open after an action and switch to it
new_page = await self.tab_window.wait_for_new_tab_and_switch(
    lambda: self.page.click('#open-report')
)

# Close the current tab and switch to the previous one
await self.tab_window.close_current_tab()

# Refresh the page
await self.tab_window.refresh_page()

# Navigate browser history
await self.tab_window.go_back()
await self.tab_window.go_forward()

# Handle confirm/alert dialogs
message = await self.tab_window.handle_confirmation_dialog(
    trigger_action=lambda: self.page.click('#delete-btn'),
    accept=True,
    dialog_text='Are you sure?',
)
```

### `attribute` — DOM Attribute Manipulation

Useful for bypassing client-side validation to test server-side behaviour:

```python
# Remove HTML5 required constraint to submit empty value
await self.attribute.remove_attribute('#email', 'required')

# Remove pattern validation
await self.attribute.remove_attribute('#phone', 'pattern')

# Set an attribute
await self.attribute.set_attribute('#input', 'maxlength', '200')

# ARIA attributes
await self.attribute.remove_attribute('#field', 'aria-required')
```

---

## Components Reference

Components provide advanced control over specific element types. Access them
directly when `fill_data()` is insufficient:

```python
from core.ui.components.file  import FileComponent
from core.ui.components.table import TableComponent
from core.ui.components.modal import ModalComponent

class MyPage(BasePage):

    def get_file_upload(self) -> FileComponent:
        return FileComponent(self.page, '#resume')

    def get_results_table(self) -> TableComponent:
        return TableComponent(self.page, '#resultsTable')

    async def upload_with_preview(self, path: str) -> None:
        fc = self.get_file_upload()
        await fc.upload_files_with_preview_validation(
            file_paths=[path],
            preview_element='.file-preview',
            timeout=10_000,
        )

    async def row_count(self) -> int:
        table = self.get_results_table()
        rows = await table.get_rows()
        return await rows.count()
```

---

## Test Markers

Use pytest markers to categorise tests and run targeted subsets:

```python
import pytest

@pytest.mark.smoke_test
async def test_login(page):
    """Critical path — must pass before deeper tests."""
    ...

@pytest.mark.regression
async def test_form_validation(page):
    """Full regression coverage."""
    ...

@pytest.mark.integration
async def test_ui_plus_api(page, api_client):
    """Tests that combine UI and API layers."""
    ...

@pytest.mark.slow
@pytest.mark.regression
async def test_bulk_upload(page):
    """Slow test — excluded from quick runs."""
    ...
```

Running subsets:

```bash
pytest -m smoke_test          # Smoke tests only
pytest -m "regression and not slow"   # Fast regression
pytest -m integration         # Integration tests only
```

---

## Configuration

All browser settings are controlled via environment variables (`.env`):

| Variable | Default | Description |
|----------|---------|-------------|
| `BASE_URL` | `http://localhost:8000` | Application URL |
| `BROWSER` | `chromium` | `chromium` \| `firefox` \| `webkit` |
| `HEADLESS` | `true` | Run without a visible window |
| `VIEWPORT_WIDTH` | `1920` | Browser width in pixels |
| `VIEWPORT_HEIGHT` | `1080` | Browser height in pixels |
| `TIMEOUT` | `30000` | Default element timeout (ms) |
| `SCREENSHOT_ON_FAILURE` | `true` | Auto-capture screenshot on failure |
| `SCREENSHOTS_DIR` | `screenshots` | Directory to save screenshots |
| `TEST_MODE` | `local` | `local` \| `debug` (slow motion) |
| `CI` | `false` | Set `true` in CI/CD pipelines |
| `PYTEST_WORKERS` | `auto` | Parallel worker count |

---

## Complete Examples

### Example 1: Registration Form

```python
from core.ui.base_page import BasePage
from utils.test_helpers import TestDataGenerator

class RegistrationPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.first_name    = '#firstName'
        self.last_name     = '#lastName'
        self.email         = '#email'
        self.password      = '#password'
        self.agree_terms   = '#agreeTerms'
        self.submit        = '#submitBtn'

    def generate_user_data(self, **overrides):
        return {
            self.first_name:  overrides.get('first_name', TestDataGenerator.random_name('first')),
            self.last_name:   overrides.get('last_name',  TestDataGenerator.random_name('last')),
            self.email:       overrides.get('email',      TestDataGenerator.random_email()),
            self.password:    overrides.get('password',   TestDataGenerator.random_password()),
            self.agree_terms: True,
        }

    async def register(self, **overrides):
        data = self.generate_user_data(**overrides)
        await self.fill_data(data)
        await self.page.click(self.submit)
        return data

async def test_user_registration(page):
    reg = RegistrationPage(page)
    await page.goto('https://app.example.com/register')

    user_data = await reg.register(email='qa+test@example.com')

    await reg.validation.assert_visible('#successBanner')
```

### Example 2: Full CRUD Workflow

```python
from core.ui.base_page import BasePage
from utils.test_helpers import TestDataGenerator

class EmployeePage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        # Form selectors
        self.name     = '#name'
        self.email    = '#email'
        self.dept     = '#department'
        # Details view selectors
        self.name_d   = '#div_id_name'
        self.email_d  = '#div_id_email'
        self.dept_d   = '#div_id_department'
        # Stored data
        self.form_data    = {}
        self.details_data = {}

    def generate_data(self, **kw):
        name  = kw.get('name',  TestDataGenerator.random_name())
        email = kw.get('email', TestDataGenerator.random_email())
        dept  = kw.get('dept',  'Engineering')
        self.form_data    = {self.name: name, self.email: email, self.dept: dept}
        self.details_data = {self.name_d: name, self.email_d: email, self.dept_d: dept}
        return self.form_data, self.details_data

    async def create(self, **kw):
        form_data, _ = self.generate_data(**kw)
        await self.fill_data(form_data)
        await self.page.click('#submit')

    async def edit(self, **kw):
        form_data, _ = self.generate_data(**kw)
        await self.edit_item(form_data)
        await self.page.click('#submit')

    async def assert_edit_view(self):
        await self.validate_edit_view(self.form_data)

    async def assert_details_view(self):
        await self.validate_details_view(self.details_data)

async def test_employee_crud(page):
    emp = EmployeePage(page)
    await page.goto('https://app.example.com/employees')

    # CREATE
    await page.click('#addEmployee')
    await emp.create(name='Alice Johnson')

    # READ — details view
    await page.click('a:has-text("Alice Johnson")')
    await emp.assert_details_view()

    # UPDATE
    await page.click('#editBtn')
    await emp.edit(dept='Marketing')

    # Validate edit form
    await page.click('#editBtn')
    await emp.assert_edit_view()

    # DELETE
    await page.click('#deleteBtn')
    await emp.tab_window.handle_confirmation_dialog(
        trigger_action=lambda: None,
        accept=True,
    )
    await emp.validation.assert_not_visible('tr:has-text("Alice Johnson")')
```

---

See [core/ui/README.md](../core/ui/README.md) for the full framework reference.
