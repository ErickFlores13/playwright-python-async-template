# UI Framework - User Guide

**For:** QA Testers & SDETs
**Purpose:** Learn how to use the framework to automate test cases

> **Maintaining/Extending the framework?** See [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)

---

## Table of Contents

- [Quick Start](#quick-start)
- [The Core Pattern](#the-core-pattern)
- [Supported Field Types](#supported-field-types)
- [Common Usage Examples](#common-usage-examples)
- [Services Reference](#services-reference)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Create a Page Object

```python
from playwright.async_api import Page
from core.ui.base_page import BasePage

class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)  # Required!

        # Define your selectors
        self.username = '#username'
        self.password = '#password'
        self.login_btn = '#loginBtn'

    async def login(self, username: str, password: str):
        # Use strategy_factory to fill forms automatically
        await self.strategy_factory.fill_data({
            self.username: username,
            self.password: password,
        })
        await self.page.click(self.login_btn)
```

### 2. Use in Your Tests

```python
async def test_login(page: Page):
    await page.goto('https://yourapp.com/login')

    login_page = LoginPage(page)
    await login_page.login('testuser', 'password123')

    # Use validation service
    await login_page.validation.assert_visible('#dashboard')
```

**That's it!** The framework automatically:

- ✅ Detects field types (input, select, checkbox, etc.)
- ✅ Uses the correct interaction method for each field
- ✅ Waits for elements to be ready
- ✅ Handles errors with retries

---

## The Core Pattern

### 90% Use Case: Strategy Pattern

**The framework's killer feature** - automatic field type detection and interaction.

```python
class EmployeeFormPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # 1. Define selectors as instance variables
        self.name = '#name'
        self.dept = '#department'
        self.start_date = '#startDate'
        self.resume = '#resume'
        self.benefits = '.benefits-checkbox'

    async def fill_form(self, data: dict):
        # 2. Pass selectors and values to strategy_factory
        await self.strategy_factory.fill_data({
            self.name: 'John Doe',
            self.dept: 'Engineering',       # Select dropdown
            self.start_date: '2024-01-15',  # Date picker
            self.resume: 'C:/resume.pdf',   # File upload
            self.benefits: ['Health', '401k'], # Multiple checkboxes
        })
```

**How it works:**

1. You provide `{selector: value}` dict
2. Framework detects field type automatically
3. Uses appropriate strategy (input, select, checkbox, etc.)
4. Fills the field correctly

### 10% Use Case: Direct Components

For advanced features, use components directly:

```python
from core.ui.components.file import FileComponent
from core.ui.components.table import TableComponent

class EmployeeFormPage(BasePage):
    def get_resume_component(self) -> FileComponent:
        """Helper method to get FileComponent"""
        return FileComponent(self.page, '#resume')

    async def upload_resume_with_validation(self, path: str):
        # Advanced: Upload with preview validation
        resume = self.get_resume_component()
        await resume.upload_files_with_preview_validation(
            file_paths=[path],
            preview_element='.file-preview',
            timeout=5000
        )
```

---

## Supported Field Types

The strategy pattern automatically handles these field types:

| Field Type | HTML Example | Value Format | Example |
|------------|-------------|--------------|---------|
| **Text Input** | `<input type="text">` | String | `'#name': 'John Doe'` |
| **Email Input** | `<input type="email">` | String | `'#email': 'john@example.com'` |
| **Number Input** | `<input type="number">` | String/Number | `'#age': '30'` |
| **Textarea** | `<textarea>` | String | `'#notes': 'Some notes'` |
| **Select Dropdown** | `<select>` | Option text | `'#dept': 'Engineering'` |
| **Checkbox (Single)** | `<input type="checkbox">` | Boolean | `'#agree': True` |
| **Checkboxes (Multiple)** | Multiple checkboxes | List of labels | `'.benefits': ['Health', 'Dental']` |
| **Radio Button** | `<input type="radio">` | Value attribute | `'input[name="type"]': 'full-time'` |
| **Date Picker** | `<input type="date">` | YYYY-MM-DD | `'#startDate': '2024-01-15'` |
| **File Upload** | `<input type="file">` | Absolute path | `'#resume': 'C:/file.pdf'` |
| **Select2** | Enhanced dropdown | Option text | `'#country': 'United States'` |
| **Button** | `<button>` | `'click'` or None | `'#submit': 'click'` |

### Multiple Values

**Multiple Checkboxes:**

```python
await self.strategy_factory.fill_data({
    '.benefits-checkbox': ['Health Insurance', 'Dental', '401k']
})
```

**Multiple Files:**

```python
await self.strategy_factory.fill_data({
    '#documents': ['C:/file1.pdf', 'C:/file2.pdf', 'C:/file3.pdf']
})
```

**Dynamic Forms (Formsets):**

```python
# Click button multiple times to add rows, fill each row
await self.strategy_factory.fill_data({
    '#addContact': [
        {'#contactName': 'John', '#contactPhone': '555-0001'},
        {'#contactName': 'Jane', '#contactPhone': '555-0002'},
    ]
})
```

---

## Data Generation Best Practices

### Centralized Data Factory Pattern

**Use `TestDataGenerator` for consistent test data** (available in `utils/test_helpers.py`)

#### Basic Usage

```python
from utils.test_helpers import TestDataGenerator

class EmployeeFormPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # Define selectors
        self.name = '#name'
        self.email = '#email'
        self.phone = '#phone'
        self.start_date = '#startDate'
        self.department = '#department'
        self.salary = '#salary'

    def generate_employee_data(self, **kwargs):
        """
        Generate employee form data with random values.
        Override specific fields using kwargs.

        Returns:
            dict: Selector-to-value mapping for fill_data

        Example:
            # All random
            data = page.generate_employee_data()

            # Override specific fields
            data = page.generate_employee_data(
                name='John Doe',
                department='Engineering'
            )
        """
        return {
            self.name: kwargs.get('name', TestDataGenerator.random_name()),
            self.email: kwargs.get('email', TestDataGenerator.random_email()),
            self.phone: kwargs.get('phone', TestDataGenerator.random_phone()),
            self.start_date: kwargs.get('start_date', TestDataGenerator.random_future_date()),
            self.department: kwargs.get('department', 'Engineering'),
            self.salary: kwargs.get('salary', TestDataGenerator.random_price(30000, 150000)),
        }

    async def create_employee(self, **kwargs):
        """Create employee with generated data"""
        data = self.generate_employee_data(**kwargs)
        await self.strategy_factory.fill_data(data)
        await self.page.click('#submit')
```

#### Complete CRUD Workflow with Data Generation

```python
class EmployeeFormPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # Form selectors
        self.name = '#name'
        self.email = '#email'
        self.department = '#dept'
        self.start_date = '#startDate'

        # Details view selectors (containers)
        self.name_container = '#div_id_name'
        self.email_container = '#div_id_email'
        self.dept_container = '#div_id_department'
        self.date_container = '#div_id_start_date'

        # Store generated data
        self.form_data = {}
        self.validation_data = {}

    def generate_employee_data(self, **kwargs):
        """
        Generate both form data and validation data.

        Args:
            **kwargs: Override any field value

        Returns:
            tuple: (form_data, validation_data)
        """
        # Generate base values
        name = kwargs.get('name', TestDataGenerator.random_name())
        email = kwargs.get('email', TestDataGenerator.random_email())
        department = kwargs.get('department', 'Engineering')
        start_date = kwargs.get('start_date', TestDataGenerator.random_future_date())

        # Form data (for fill_data/edit_item/validate_edit_view)
        form_data = {
            self.name: name,
            self.email: email,
            self.department: department,
            self.start_date: start_date,
        }

        # Validation data (for details view)
        validation_data = {
            self.name_container: name,
            self.email_container: email,
            self.dept_container: department,
            self.date_container: self._format_date_for_display(start_date),
        }

        # Store for later use
        self.form_data = form_data
        self.validation_data = validation_data

        return form_data, validation_data

    def _format_date_for_display(self, date_str: str) -> str:
        """Convert YYYY-MM-DD to display format if needed"""
        # Example: "2024-01-15" -> "15 de Enero de 2024"
        from datetime import datetime
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        # Add your format logic here
        return date_str  # Simplified

    async def create_employee(self, **kwargs):
        """Create employee and store data for validation"""
        form_data, validation_data = self.generate_employee_data(**kwargs)
        await self.strategy_factory.fill_data(form_data)
        await self.page.click('#submit')

    async def edit_employee(self, **kwargs):
        """Edit employee with new data"""
        form_data, validation_data = self.generate_employee_data(**kwargs)
        await self.strategy_factory.edit_item(form_data)
        await self.page.click('#submit')

    async def validate_in_edit_view(self):
        """Validate form fields have correct values"""
        await self.strategy_factory.validate_edit_view(self.form_data)

    async def validate_in_details_view(self):
        """Validate read-only details view"""
        await self.validation.validate_record_information_in_details_view(
            self.validation_data
        )
```

#### Test Usage

```python
async def test_employee_crud_workflow(page: Page):
    await page.goto('https://app.com/employees')

    emp_page = EmployeeFormPage(page)

    # CREATE with specific values
    await emp_page.create_employee(
        name='John Doe',
        department='Engineering'
        # email, start_date auto-generated
    )

    # Validate in details view
    await page.click('#viewDetails')
    await emp_page.validate_in_details_view()

    # EDIT with new values
    await page.click('#editButton')
    await emp_page.edit_employee(
        department='Sales',
        # name, email kept from previous generation
    )

    # Validate in edit form
    await page.click('#editButton')
    await emp_page.validate_in_edit_view()
```

### Available Data Generators

```python
from utils.test_helpers import TestDataGenerator

# Strings
TestDataGenerator.random_string(10)           # 'AbCdEfGhIj'
TestDataGenerator.random_alphanumeric(10)     # 'A1b2C3d4E5'
TestDataGenerator.random_username(8)          # 'user1234'

# Numbers
TestDataGenerator.random_number(1, 100)       # 42
TestDataGenerator.random_decimal(0, 100, 2)   # 45.67
TestDataGenerator.random_price(10, 1000)      # '549.99'
TestDataGenerator.random_digits(5)            # '12345'

# Dates
TestDataGenerator.random_date()               # '2024-06-15'
TestDataGenerator.random_future_date(365)     # Date within next year
TestDataGenerator.random_past_date(365)       # Date within last year
TestDataGenerator.format_date_in_spanish('2024-01-15')  # '15 de Enero de 2024'

# Contact Info
TestDataGenerator.random_email()              # 'abc123@gmail.com'
TestDataGenerator.random_email('company.com') # 'xyz789@company.com'
TestDataGenerator.random_phone('us')          # '(555) 123-4567'
TestDataGenerator.random_phone('simple')      # '5551234567'

# Names
TestDataGenerator.random_name('first')        # 'John'
TestDataGenerator.random_name('last')         # 'Smith'
TestDataGenerator.random_name('full')         # 'John Smith'
TestDataGenerator.random_company_name()       # 'Tech Solutions'

# Others
TestDataGenerator.random_boolean()            # True or False
TestDataGenerator.random_password(12)         # 'aB3!xY9@zQ1#'
TestDataGenerator.random_url()                # 'https://example.com/path'
TestDataGenerator.random_address()            # {'street': ..., 'city': ...}
```

### Pattern: Reusable Data Generation Methods

```python
class RegistrationPage(BasePage):
    def generate_user_data(self, **kwargs):
        """Generate registration data"""
        return {
            self.first_name: kwargs.get('first_name', TestDataGenerator.random_name('first')),
            self.last_name: kwargs.get('last_name', TestDataGenerator.random_name('last')),
            self.email: kwargs.get('email', TestDataGenerator.random_email()),
            self.password: kwargs.get('password', TestDataGenerator.random_password()),
            self.agree_terms: kwargs.get('agree_terms', True),
        }

    async def register_user(self, **kwargs):
        """Register with auto-generated data"""
        data = self.generate_user_data(**kwargs)
        await self.strategy_factory.fill_data(data)
        await self.page.click('#submit')
        return data  # Return for assertions in test

# In test:
async def test_registration(page: Page):
    reg_page = RegistrationPage(page)

    # Test 1: All random
    user_data = await reg_page.register_user()

    # Test 2: Specific email domain
    user_data = await reg_page.register_user(
        email=TestDataGenerator.random_email('mycompany.com')
    )

    # Test 3: Known credentials
    user_data = await reg_page.register_user(
        email='test@example.com',
        password='Test123!'
    )
```

---

## Common Usage Examples

### Example 1: Simple Registration Form

```python
class RegistrationPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        self.first_name = '#firstName'
        self.last_name = '#lastName'
        self.email = '#email'
        self.password = '#password'
        self.agree_terms = '#agreeTerms'
        self.submit = '#submitBtn'

    async def register(self, first_name: str, last_name: str,
                      email: str, password: str):
        await self.strategy_factory.fill_data({
            self.first_name: first_name,
            self.last_name: last_name,
            self.email: email,
            self.password: password,
            self.agree_terms: True,
        })
        await self.page.click(self.submit)
        await self.validation.assert_visible('#successMessage')
```

### Example 2: Complete CRUD Workflow

```python
class EmployeeManagementPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # Form field selectors
        self.name_input = '#name'
        self.email_input = '#email'
        self.dept_select = '#department'
        self.start_date = '#startDate'

        # Details view container selectors
        self.name_detail = '#div_id_name'
        self.email_detail = '#div_id_email'
        self.dept_detail = '#div_id_department'
        self.date_detail = '#div_id_start_date'

        # Store test data
        self.form_data = {}
        self.details_data = {}

    def generate_employee_data(self, **kwargs):
        """Generate employee data with random defaults"""
        from utils.test_helpers import TestDataGenerator

        name = kwargs.get('name', TestDataGenerator.random_name())
        email = kwargs.get('email', TestDataGenerator.random_email())
        dept = kwargs.get('department', 'Engineering')
        date = kwargs.get('start_date', TestDataGenerator.random_future_date())

        # Form data (for filling/editing)
        self.form_data = {
            self.name_input: name,
            self.email_input: email,
            self.dept_select: dept,
            self.start_date: date,
        }

        # Details view data (for validation)
        self.details_data = {
            self.name_detail: name,
            self.email_detail: email,
            self.dept_detail: dept,
            self.date_detail: date,  # Or formatted: '15 de Enero de 2024'
        }

        return self.form_data, self.details_data

    async def create_employee(self, **kwargs):
        """CREATE: Generate and fill form"""
        form_data, _ = self.generate_employee_data(**kwargs)
        await self.strategy_factory.fill_data(form_data)
        await self.page.click('#submitBtn')
        await self.validation.assert_visible('#successMessage')

    async def edit_employee(self, **kwargs):
        """UPDATE: Generate new data and edit"""
        form_data, _ = self.generate_employee_data(**kwargs)
        await self.strategy_factory.edit_item(form_data)
        await self.page.click('#submitBtn')
        await self.validation.assert_visible('#successMessage')

    async def validate_edit_view(self):
        """Validate form fields in edit view"""
        await self.strategy_factory.validate_edit_view(self.form_data)

    async def validate_details_view(self):
        """Validate read-only details view"""
        await self.validation.validate_record_information_in_details_view(
            self.details_data
        )

# Test usage
async def test_employee_full_workflow(page: Page):
    await page.goto('https://app.com/employees')

    emp_page = EmployeeManagementPage(page)

    # CREATE with specific name, random email/date
    await page.click('#addEmployee')
    await emp_page.create_employee(name='John Doe')

    # Navigate to details and validate
    await page.click('a:has-text("John Doe")')
    await emp_page.validate_details_view()

    # EDIT - update department
    await page.click('#editButton')
    await emp_page.edit_employee(department='Sales')

    # Validate updated values in edit form
    await page.click('#editButton')
    await emp_page.validate_edit_view()

    # Validate in details view again
    await page.click('#viewDetails')
    await emp_page.validate_details_view()
```

### Example 3: Complex Form with All Field Types

```python
class EmployeeFormPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # Text inputs
        self.name = '#name'
        self.email = '#email'

        # Dropdowns
        self.department = '#department'
        self.manager = '#manager'  # Select2

        # Checkboxes
        self.benefits = '.benefits-checkbox'

        # Radio buttons
        self.employment_type = 'input[name="employmentType"]'

        # Date picker
        self.start_date = '#startDate'

        # File upload
        self.resume = '#resume'

    async def create_employee(self, employee_data: dict):
        """
        employee_data example:
        {
            'name': 'John Doe',
            'email': 'john@example.com',
            'department': 'Engineering',
            'manager': 'Jane Smith',
            'benefits': ['Health', 'Dental', '401k'],
            'employment_type': 'full-time',
            'start_date': '2024-01-15',
            'resume_path': 'C:/docs/resume.pdf'
        }
        """
        await self.strategy_factory.fill_data({
            self.name: employee_data['name'],
            self.email: employee_data['email'],
            self.department: employee_data['department'],
            self.manager: employee_data['manager'],
            self.benefits: employee_data['benefits'],
            self.employment_type: employee_data['employment_type'],
            self.start_date: employee_data['start_date'],
            self.resume: employee_data['resume_path'],
        })

        await self.page.click('#submitBtn')
```

### Example 3: Complex Form with All Field Types

```python
class EmployeeFormPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # Text inputs
        self.name = '#name'
        self.email = '#email'

        # Dropdowns
        self.department = '#department'
        self.manager = '#manager'  # Select2

        # Checkboxes
        self.benefits = '.benefits-checkbox'

        # Radio buttons
        self.employment_type = 'input[name="employmentType"]'

        # Date picker
        self.start_date = '#startDate'

        # File upload
        self.resume = '#resume'

    async def create_employee(self, employee_data: dict):
        """
        employee_data example:
        {
            'name': 'John Doe',
            'email': 'john@example.com',
            'department': 'Engineering',
            'manager': 'Jane Smith',
            'benefits': ['Health', 'Dental', '401k'],
            'employment_type': 'full-time',
            'start_date': '2024-01-15',
            'resume_path': 'C:/docs/resume.pdf'
        }
        """
        await self.strategy_factory.fill_data({
            self.name: employee_data['name'],
            self.email: employee_data['email'],
            self.department: employee_data['department'],
            self.manager: employee_data['manager'],
            self.benefits: employee_data['benefits'],
            self.employment_type: employee_data['employment_type'],
            self.start_date: employee_data['start_date'],
            self.resume: employee_data['resume_path'],
        })

        await self.page.click('#submitBtn')
```

### Example 4: File Upload with Validation (Advanced)

```python
class DocumentUploadPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.document_input = '#documentUpload'

    def get_document_component(self) -> FileComponent:
        """Helper to get FileComponent for advanced operations"""
        return FileComponent(self.page, self.document_input)

    async def upload_document_with_preview(self, file_path: str):
        """Upload document and validate preview appears"""
        doc_component = self.get_document_component()

        # Advanced feature: Upload with preview validation
        await doc_component.upload_files_with_preview_validation(
            file_paths=[file_path],
            preview_element='.document-preview',
            timeout=10000
        )

        await self.validation.assert_visible('#uploadSuccess')
```

### Example 4: File Upload with Validation (Advanced)

```python
class DocumentUploadPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.document_input = '#documentUpload'

    def get_document_component(self) -> FileComponent:
        """Helper to get FileComponent for advanced operations"""
        return FileComponent(self.page, self.document_input)

    async def upload_document_with_preview(self, file_path: str):
        """Upload document and validate preview appears"""
        doc_component = self.get_document_component()

        # Advanced feature: Upload with preview validation
        await doc_component.upload_files_with_preview_validation(
            file_paths=[file_path],
            preview_element='.document-preview',
            timeout=10000
        )

        await self.validation.assert_visible('#uploadSuccess')
```

### Example 5: Table Interaction

```python
class EmployeeListPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.employee_table = '#employeeTable'

    def get_table_component(self) -> TableComponent:
        return TableComponent(self.page, self.employee_table)

    async def get_employee_count(self) -> int:
        table = self.get_table_component()
        rows = await table.get_rows()
        return await rows.count()

    async def get_employee_data(self) -> list:
        table = self.get_table_component()
        return await table.get_row_texts()

    async def click_employee_row(self, index: int):
        table = self.get_table_component()
        await table.click_row(index)
```

### Example 5: Table Interaction

```python
class EmployeeListPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.employee_table = '#employeeTable'

    def get_table_component(self) -> TableComponent:
        return TableComponent(self.page, self.employee_table)

    async def get_employee_count(self) -> int:
        table = self.get_table_component()
        rows = await table.get_rows()
        return await rows.count()

    async def get_employee_data(self) -> list:
        table = self.get_table_component()
        return await table.get_row_texts()

    async def click_employee_row(self, index: int):
        table = self.get_table_component()
        await table.click_row(index)
```

### Example 6: Multi-Tab Workflow

```python
class ReportPage(BasePage):
    async def download_pdf_report(self):
        # Click button that opens PDF in new tab
        await self.page.click('#viewPdfReport')

        # Wait for new tab
        pdf_page = await self.tab_window.wait_for_new_page()

        # Switch to new tab
        await self.tab_window.switch_to_page(pdf_page)

        # Download from new tab
        file_comp = FileComponent(pdf_page, selector=None)
        path = await file_comp.download_and_verify_file(
            download_trigger='#downloadBtn',
            expected_filename='report.pdf'
        )

        # Switch back to original tab
        await self.tab_window.switch_to_original_tab()

        return path
```

---

## Services Reference

All page objects inheriting from `BasePage` have access to these services:

### 1. strategy_factory (Form Filling & Validation)

**Use for:** 90% of form interactions, editing, and validation

#### fill_data - Create/Fill Forms

```python
# Automatic field type detection and filling
await self.strategy_factory.fill_data({
    '#textField': 'value',
    '#dropdown': 'Option 1',
    '#checkbox': True,
    '#file': 'C:/file.pdf',
})
```

#### edit_item - Clear & Refill Fields

```python
# Clear existing values and fill with new data
await self.strategy_factory.edit_item({
    '#name': 'Updated Name',
    '#email': 'newemail@example.com',
    '#department': 'Sales',
})
# Equivalent to:
# await self.strategy_factory.clear_fields(data)
# await self.strategy_factory.fill_data(data)
```

#### validate_edit_view - Validate Form Fields

```python
# Validate that fields in edit form have expected values
await self.strategy_factory.validate_edit_view({
    '#name': 'John Doe',
    '#department': 'Engineering',
    '#status': True,  # Checkbox checked
})
```

### 2. validation (Assertions)

**Use for:** Page state and element validation

#### Standard Assertions

```python
# Element visibility
await self.validation.assert_visible('#successMsg')
await self.validation.assert_not_visible('#errorMsg')

# Element text
await self.validation.assert_element_text('#status', 'Active')

# Page URL
await self.validation.assert_url_contains('/dashboard')

# Element count
await self.validation.assert_element_count('.items', 5)
```

#### validate_record_information_in_details_view - Details View Validation

```python
# Validate displayed values in read-only details view
# Uses same data structure as fill_data but with container selectors
await self.validation.validate_record_information_in_details_view({
    '#div_id_name': 'John Doe',              # Text container
    '#div_id_email': 'john@example.com',     # Text container
    '#div_id_active': True,                  # Checkbox in container
    '#div_id_benefits': ['Health', 'Dental'], # Multiple values in container
})
```

### 3. wait (Smart Waiting)

**Use for:** Page load and element waiting

```python
# Wait for page load (smart fallback: networkidle → domcontentloaded)
await self.wait.wait_for_page_load()

# Wait for specific load state
await self.wait.wait_for_load_state('domcontentloaded')

# Wait for element (custom timeout)
await self.wait.wait_for_element('#result', state='visible', timeout=10000)

# Wait for navigation
await self.wait.wait_for_navigation(url_pattern='/success')
```

### 4. screenshot (Evidence Capture)

**Use for:** Capturing test evidence

```python
# Full page screenshot (auto-timestamped)
await self.screenshot.take_screenshot('test_failure')
# Saves to: screenshots/20241202_143052_test_failure.png

# Element screenshot
await self.screenshot.take_element_screenshot('#errorMsg', 'error_state')
```

### 5. storage (Cookies & Local Storage)

**Use for:** Session management, feature flags

```python
# Cookies
await self.storage.add_cookie({'name': 'sessionId', 'value': 'abc123'})
cookies = await self.storage.get_all_cookies()
await self.storage.clear_cookies()

# Local Storage
await self.storage.set_local_storage('theme', 'dark')
theme = await self.storage.get_local_storage('theme')
await self.storage.clear_local_storage()

# Session Storage
await self.storage.set_session_storage('temp', 'value')
```

### 6. tab_window (Multi-Tab Management)

**Use for:** Multi-page workflows (PDFs, external links)

```python
# Wait for new tab to open
new_page = await self.tab_window.wait_for_new_page()

# Switch between tabs
await self.tab_window.switch_to_tab(1)  # By index
await self.tab_window.switch_to_original_tab()

# Open new tab manually
new_page = await self.tab_window.open_new_tab('https://example.com')

# Close tabs
await self.tab_window.close_tab(1)
await self.tab_window.close_all_except_first()
```

### 7. attribute (DOM Manipulation)

**Use for:** Backend testing - remove client-side validation

```python
# Remove HTML5 validation to test server-side validation
await self.attribute.remove_attribute('#email', 'required')
await self.attribute.remove_attribute('#phone', 'pattern')

# Modify attributes
await self.attribute.set_attribute('#input', 'maxlength', '100')

# Get attribute value
value = await self.attribute.get_attribute('#input', 'placeholder')
```

---

## Best Practices

### 1. Always Inherit from BasePage

```python
# ✅ Good
class MyPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)  # Required!

# ❌ Bad
class MyPage:
    def __init__(self, page: Page):
        self.page = page
```

### 2. Centralize Selectors

```python
# ✅ Good - Selectors as instance variables
class FormPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # Centralized selectors
        self.name = '#name'
        self.email = '#email'

    async def fill_form(self, name, email):
        await self.strategy_factory.fill_data({
            self.name: name,
            self.email: email,
        })

# ❌ Bad - Hardcoded selectors
class FormPage(BasePage):
    async def fill_form(self, name, email):
        await self.strategy_factory.fill_data({
            '#name': name,  # Where is this defined?
            '#email': email,
        })
```

### 3. Use Strategy Pattern for 90% of Cases

```python
# ✅ Good - Use strategy_factory
async def fill_form(self, data):
    await self.strategy_factory.fill_data(data)

# ❌ Bad - Manual field type checking (framework does this!)
async def fill_form(self, selector, value):
    element = self.page.locator(selector)
    tag = await element.evaluate('el => el.tagName')

    if tag == 'input':
        await element.fill(value)
    elif tag == 'select':
        await element.select_option(value)
    # ... etc (don't do this!)
```

### 4. Create Helper Methods for Components

```python
class FormPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.resume_input = '#resume'

    # Helper method for component access
    def get_resume_component(self) -> FileComponent:
        return FileComponent(self.page, self.resume_input)

    async def upload_resume_with_validation(self, path: str):
        resume = self.get_resume_component()
        await resume.upload_files_with_preview_validation(
            file_paths=[path],
            preview_element='.preview'
        )
```

### 5. Use Validation Service for Assertions

```python
# ✅ Good - Use validation service
async def submit_form(self):
    await self.page.click('#submit')
    await self.validation.assert_visible('#success')

# ❌ Bad - Direct assertions in page object
async def submit_form(self):
    await self.page.click('#submit')
    assert await self.page.locator('#success').is_visible()
```

### 6. Document Expected Data Formats

```python
async def create_employee(self, employee_data: dict):
    """
    Create new employee.

    Args:
        employee_data: Employee information

    Expected Format:
        {
            'name': str,
            'email': str,
            'department': str (dropdown option text),
            'start_date': str (YYYY-MM-DD format),
            'resume_path': str (absolute file path),
            'benefits': list[str] (checkbox labels),
        }

    Example:
        await page.create_employee({
            'name': 'John Doe',
            'email': 'john@example.com',
            'department': 'Engineering',
            'start_date': '2024-01-15',
            'resume_path': 'C:/docs/resume.pdf',
            'benefits': ['Health', 'Dental', '401k'],
        })
    """
    await self.strategy_factory.fill_data({...})
```

### 7. Use Dynamic Selectors When Needed

```python
# For repetitive form sections
async def fill_emergency_contacts(self, contacts: list):
    for i, contact in enumerate(contacts):
        await self.strategy_factory.fill_data({
            f'#contactName{i}': contact['name'],
            f'#contactPhone{i}': contact['phone'],
        })
```

---

## Troubleshooting

### Problem: Field not filling correctly

**Symptoms:** Value not appearing after `fill_data()`

**Solutions:**

1. **Check selector is correct**

   ```python
   # Verify in browser console: document.querySelector('#yourSelector')
   ```

2. **Wait for page to load**

   ```python
   await self.wait.wait_for_page_load()
   await self.strategy_factory.fill_data({...})
   ```

3. **Check field type detection**

   ```python
   # Debug what type was detected
   field = await self.element_resolver.resolve_field('#field')
   print(f"Tag: {field.tag}, Type: {field.input_type}")
   ```

4. **Use component directly if strategy fails**

   ```python
   from core.ui.components.input import InputComponent
   input_comp = InputComponent(self.page, '#field')
   await input_comp.fill('value')
   ```

### Problem: Select dropdown not working

**Symptoms:** Dropdown doesn't select option

**Solutions:**

1. **Check option text matches exactly (case-sensitive)**

   ```python
   # ❌ Wrong
   '#dept': 'engineering'  # Lowercase

   # ✅ Correct
   '#dept': 'Engineering'  # Matches <option>Engineering</option>
   ```

2. **For Select2 dropdowns, framework auto-detects**

   ```python
   # Should work automatically
   await self.strategy_factory.fill_data({
       '#country': 'United States'  # Select2 auto-detected
   })

   # If not, use component directly
   from core.ui.components.select2 import Select2Component
   select2 = Select2Component(self.page, '#country')
   await select2.select_option('United States')
   ```

### Problem: File upload failing

**Symptoms:** File not uploading or validation failing

**Solutions:**

1. **Use absolute paths**

   ```python
   # ❌ Wrong
   '#resume': 'resume.pdf'

   # ✅ Correct
   '#resume': 'C:/Users/username/Documents/resume.pdf'
   # Or
   '#resume': r'C:\Users\username\Documents\resume.pdf'
   ```

2. **Increase timeout for large files**

   ```python
   file_comp = FileComponent(self.page, '#file')
   await file_comp.upload_files_with_preview_validation(
       file_paths=[path],
       preview_element='.preview',
       timeout=30000  # Increase from default
   )
   ```

### Problem: Page load timeout

**Symptoms:** `wait_for_page_load()` timing out

**Solutions:**

1. **Framework has smart fallback, but you can be explicit**

   ```python
   # Skip networkidle, just wait for DOM
   await self.wait.wait_for_load_state('domcontentloaded')
   ```

2. **Increase timeout**

   ```python
   await self.wait.wait_for_page_load(timeout=60000)  # 60 seconds
   ```

3. **Wait for specific element instead**

   ```python
   await self.wait.wait_for_element('#result', state='visible')
   ```

### Problem: Service not found

**Symptoms:** `AttributeError: 'MyPage' object has no attribute 'strategy_factory'`

**Solution:**

```python
# Make sure you inherit from BasePage and call super()
from core.ui.base_page import BasePage

class MyPage(BasePage):  # ← Inherit
    def __init__(self, page: Page):
        super().__init__(page)  # ← Call super().__init__()
```

### Problem: Multiple checkboxes - only first one checking

**Symptoms:** Only first checkbox gets checked when passing list

**Solution:**

```python
# Make sure checkbox labels match exactly
# HTML: <label>Health Insurance<input type="checkbox"></label>

# ✅ Correct - matches label text exactly
await self.strategy_factory.fill_data({
    '.benefits': ['Health Insurance', 'Dental Insurance']
})

# ❌ Wrong - doesn't match full label
await self.strategy_factory.fill_data({
    '.benefits': ['Health', 'Dental']  # Labels have "Insurance" suffix!
})
```

---

## Framework vs Manual Playwright

### Code Comparison

**Manual Playwright (verbose):**

```python
class FormPageManual:
    async def fill_form(self, data):
        for selector, value in data.items():
            element = page.locator(selector)
            tag = await element.evaluate('el => el.tagName')
            input_type = await element.get_attribute('type')

            if tag == 'INPUT' and input_type == 'text':
                await element.fill(value)
            elif tag == 'SELECT':
                await element.select_option(value)
            elif tag == 'INPUT' and input_type == 'checkbox':
                if value:
                    await element.check()
                else:
                    await element.uncheck()
            # ... 5 more type checks
```

**With Framework (clean):**

```python
class FormPage(BasePage):
    async def fill_form(self, data):
        await self.strategy_factory.fill_data(data)  # Done!
```

### Benefits

| Feature | Manual Playwright | With Framework |
|---------|------------------|----------------|
| **Code Volume** | Baseline | 30-40% less code |
| **Type Detection** | Manual for each field | Automatic |
| **File Upload/Download** | Manual implementation | Built-in with validation |
| **Multi-Tab** | Manual context switching | Service handles it |
| **Maintenance** | Update every page object | Fix once, all benefit |

---

## Additional Resources

- **Full Example:** See `pages/examples/complex_form_page.py` for complete implementation
- **Comparison:** See `pages/examples/complex_form_page_vanilla.py` for manual Playwright version
- **Framework Extension:** See [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md) for maintaining/extending

---

## Quick Reference

### CRUD Workflow Pattern

```python
from core.ui.base_page import BasePage
from utils.test_helpers import TestDataGenerator

class MyPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)  # Required!

        # Form selectors
        self.name = '#name'
        self.email = '#email'

        # Details view selectors (containers)
        self.name_detail = '#div_id_name'
        self.email_detail = '#div_id_email'

        # Data storage
        self.form_data = {}
        self.details_data = {}

    def generate_data(self, **kwargs):
        """Generate test data with random defaults"""
        name = kwargs.get('name', TestDataGenerator.random_name())
        email = kwargs.get('email', TestDataGenerator.random_email())

        self.form_data = {self.name: name, self.email: email}
        self.details_data = {self.name_detail: name, self.email_detail: email}
        return self.form_data, self.details_data

    async def create(self, **kwargs):
        """CREATE"""
        form_data, _ = self.generate_data(**kwargs)
        await self.strategy_factory.fill_data(form_data)
        await self.page.click('#submit')

    async def edit(self, **kwargs):
        """UPDATE"""
        form_data, _ = self.generate_data(**kwargs)
        await self.strategy_factory.edit_item(form_data)
        await self.page.click('#submit')

    async def validate_edit_view(self):
        """Validate form fields"""
        await self.strategy_factory.validate_edit_view(self.form_data)

    async def validate_details_view(self):
        """Validate details view"""
        await self.validation.validate_record_information_in_details_view(
            self.details_data
        )
```

### Essential Operations

```python
# FILL FORM (Create)
await self.strategy_factory.fill_data({
    '#field': 'value'
})

# EDIT FORM (Clear + Fill)
await self.strategy_factory.edit_item({
    '#field': 'new value'
})

# VALIDATE FORM FIELDS (Edit View)
await self.strategy_factory.validate_edit_view({
    '#field': 'expected value'
})

# VALIDATE DETAILS VIEW (Read-Only)
await self.validation.validate_record_information_in_details_view({
    '#div_id_field': 'expected value'
})

# WAIT & VALIDATE
await self.wait.wait_for_page_load()
await self.validation.assert_visible('#result')

# SCREENSHOT
await self.screenshot.take_screenshot('evidence')

# GENERATE TEST DATA
from utils.test_helpers import TestDataGenerator
data = {
    '#name': TestDataGenerator.random_name(),
    '#email': TestDataGenerator.random_email(),
    '#date': TestDataGenerator.random_future_date(),
}
```
