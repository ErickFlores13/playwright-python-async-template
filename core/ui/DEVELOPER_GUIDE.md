# UI Framework - Developer Guide

**For:** Senior SDETs & Framework Maintainers
**Purpose:** Maintain, scale, and enhance the framework following best practices

> **Just using the framework?** See [README.md](./README.md) for user documentation

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Design Patterns](#design-patterns)
- [Core Components](#core-components)
- [Services Deep Dive](#services-deep-dive)
- [Adding New Features](#adding-new-features)
- [Code Style Guidelines](#code-style-guidelines)
- [Performance Considerations](#performance-considerations)
- [Testing the Framework](#testing-the-framework)
- [Troubleshooting & Debugging](#troubleshooting--debugging)

---

## Architecture Overview

### High-Level Structure

```
core/ui/
├── base_page.py              # BasePage with lazy-loaded services (DI container)
├── components/               # Reusable UI components (10% usage)
│   ├── button.py
│   ├── checkbox.py
│   ├── datepicker.py
│   ├── file.py              # Advanced: upload/download with validation
│   ├── input.py
│   ├── modal.py
│   ├── radio.py
│   ├── select.py
│   ├── select2.py
│   └── table.py
├── services/                 # Cross-cutting services
│   ├── attribute.py         # DOM attribute manipulation
│   ├── screenshot.py        # Screenshot capture
│   ├── storage.py           # Cookie/localStorage management
│   ├── tab_window.py        # Multi-tab/window handling
│   ├── validation.py        # Domain-specific assertions
│   ├── wait.py              # Smart wait strategies
│   └── form/                # Form automation (Strategy Pattern)
│       ├── element_resolver.py    # Field type detection
│       ├── strategy_factory.py    # Strategy dispatcher
│       ├── field.py               # Field abstraction
│       ├── base_strategy.py       # Strategy interface
│       └── strategies/            # Type-specific strategies
│           ├── input_strategy.py
│           ├── select_strategy.py
│           ├── checkbox_strategy.py
│           ├── radio_strategy.py
│           ├── datepicker_strategy.py
│           ├── file_strategy.py
│           ├── button_strategy.py
│           └── select2_strategy.py
└── utils/
    ├── exceptions.py        # Custom exceptions
    └── playwright_utils.py  # Smart locators, retry logic
```

### Dependency Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      Test Layer                             │
│  (test_ui_examples.py, test_employee.py, etc.)             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ uses
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Page Object Layer                         │
│  (LoginPage, EmployeeFormPage, etc.)                       │
│                  extends BasePage                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ inherits from
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      BasePage                               │
│  - Lazy-loads services via @cached_property                │
│  - Provides: strategy_factory, validation, wait, etc.      │
└──┬──────────┬──────────┬──────────┬──────────┬─────────────┘
   │          │          │          │          │
   │ uses     │ uses     │ uses     │ uses     │ uses
   ▼          ▼          ▼          ▼          ▼
┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────────┐
│Strat │  │Valid │  │Wait  │  │Scree │  │Storage   │
│egy   │  │ation │  │      │  │nshot │  │TabWindow │
└──┬───┘  └──────┘  └──────┘  └──────┘  └──────────┘
   │
   │ delegates to
   ▼
┌─────────────────────────────────────────────┐
│          Strategy Pattern Layer             │
│  - ElementResolver (field type detection)  │
│  - StrategyFactory (strategy selection)    │
│  - Strategies (type-specific logic)        │
└────────────┬────────────────────────────────┘
             │
             │ uses
             ▼
┌─────────────────────────────────────────────┐
│          Component Layer                    │
│  (InputComponent, SelectComponent, etc.)   │
└─────────────────────────────────────────────┘
```

### Design Philosophy

1. **Separation of Concerns**
   - **Components:** UI element interactions (input, select, table, etc.)
   - **Services:** Cross-cutting functionality (validation, wait, storage)
   - **Strategies:** Field type-specific filling logic
   - **BasePage:** Dependency injection container

2. **Lazy Loading**
   - Services instantiated only when accessed via `@cached_property`
   - Reduces memory footprint
   - Speeds up page object initialization

3. **Convention over Configuration**
   - Automatic field type detection
   - Smart defaults with override capability
   - Minimal boilerplate for common cases

4. **90/10 Rule**
   - 90% of operations use strategy pattern (simple, automatic)
   - 10% use direct components (advanced features)

---

## Design Patterns

### 1. Strategy Pattern (Form Filling)

**Intent:** Select algorithm at runtime based on field type

**Implementation:**

```python
# Strategy Interface
class BaseFieldStrategy:
    async def can_handle(self, field: Field) -> bool:
        """Check if strategy can handle this field type"""
        raise NotImplementedError

    async def fill(self, field: Field, value: Any) -> None:
        """Fill the field with the value"""
        raise NotImplementedError
```

```python
# Concrete Strategy
class InputStrategy(BaseFieldStrategy):
    async def can_handle(self, field: Field) -> bool:
        return field.tag == "input" and field.input_type in ["text", "email", ...]

    async def fill(self, field: Field, value: Any) -> None:
        input_comp = InputComponent(field.page, field.selector)
        await input_comp.fill(str(value))
```

```python
# Context (Factory)
class StrategyFactory:
    def __init__(self, element_resolver: ElementResolver):
        self.resolver = element_resolver
        self.strategies = [
            InputStrategy(),
            SelectStrategy(),
            CheckboxStrategy(),
            # ...
        ]

    async def get_strategy(self, field: Field) -> BaseFieldStrategy:
        for strategy in self.strategies:
            if await strategy.can_handle(field):
                return strategy
        raise FormFillingError(f"No strategy found for {field.selector}")

    async def fill_data(self, data: dict):
        for selector, value in data.items():
            field = await self.resolver.resolve_field(selector)
            strategy = await self.get_strategy(field)
            await strategy.fill(field, value)
```

**Benefits:**

- ✅ Open/Closed Principle: Add new field types without modifying existing code
- ✅ Single Responsibility: Each strategy handles one field type
- ✅ Easy to test strategies in isolation

### 2. Factory Pattern (Strategy Selection)

**Intent:** Create strategies without specifying exact class

**Implementation:**

```python
class StrategyFactory:
    async def get_strategy(self, field: Field) -> BaseFieldStrategy:
        """Factory method: Returns strategy based on field properties"""
        for strategy in self.strategies:
            if await strategy.can_handle(field):
                return strategy
        raise FormFillingError(...)
```

**Benefits:**

- ✅ Encapsulates strategy selection logic
- ✅ Central place to register new strategies
- ✅ Clients don't need to know concrete strategy classes

### 3. Page Object Model

**Intent:** Encapsulate page structure and behavior

**Implementation:**

```python
class EmployeeFormPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # Selectors (structure)
        self.name = '#name'
        self.dept = '#department'

    # Behavior
    async def create_employee(self, name: str, dept: str):
        await self.strategy_factory.fill_data({
            self.name: name,
            self.dept: dept,
        })
```

**Benefits:**

- ✅ Single place to update selectors
- ✅ Reusable page methods
- ✅ Tests remain readable

### 4. Dependency Injection (Services)

**Intent:** Provide dependencies without coupling

**Implementation:**

```python
class BasePage:
    @cached_property
    def strategy_factory(self) -> StrategyFactory:
        """Lazy-loaded dependency"""
        return StrategyFactory(self.element_resolver)

    @cached_property
    def validation(self) -> Validation:
        return Validation(self.page)
```

**Benefits:**

- ✅ Services instantiated only when needed
- ✅ Easy to mock for testing
- ✅ Consistent service access across all pages

### 5. Template Method (Component Pattern)

**Intent:** Define skeleton of algorithm, let subclasses override steps

**Implementation:**

```python
class BaseComponent:
    def __init__(self, page: Page, selector: str, timeout: int = 30000):
        self.page = page
        self.selector = selector
        self.timeout = timeout
        self.locator = page.locator(selector)

    async def wait_for_visible(self):
        """Common waiting logic"""
        await self.locator.wait_for(state="visible", timeout=self.timeout)

class InputComponent(BaseComponent):
    async def fill(self, value: str):
        await self.wait_for_visible()  # Template method
        await self.locator.fill(value)  # Specific implementation
```

---

## Core Components

### BasePage (Dependency Injection Container)

**Responsibility:** Provide lazy-loaded services to page objects

**Key Concepts:**

1. **Lazy Loading with `@cached_property`:**

   ```python
   @cached_property
   def strategy_factory(self) -> StrategyFactory:
       return StrategyFactory(self.element_resolver)
   ```

   - First access: Creates and caches instance
   - Subsequent accesses: Returns cached instance
   - Memory efficient: Only created if used

2. **Service Registration:**

   ```python
   # Available services:
   - attribute: Attribute
   - element_resolver: ElementResolver
   - strategy_factory: StrategyFactory
   - screenshot: Screenshot
   - storage: Storage
   - tab_window: TabWindow
   - validation: Validation
   - wait: Wait
   ```

3. **Extension Point:**

   ```python
   # Add new service:
   @cached_property
   def my_new_service(self) -> MyNewService:
       return MyNewService(self.page)
   ```

### ElementResolver (Field Type Detection)

**Responsibility:** Determine field type from selector

**How it Works:**

```python
async def resolve_field(self, selector: str) -> Field:
    """
    1. Locate element using smart locators
    2. Extract tag name, type, classes, attributes
    3. Return Field object with metadata
    """
    locator = resolve_locator(self.page, selector)  # Smart retry logic

    tag = await locator.evaluate("el => el.tagName.toLowerCase()")
    input_type = await locator.get_attribute("type") or ""
    classes = await locator.get_attribute("class") or ""

    return Field(
        selector=selector,
        locator=locator,
        page=self.page,
        tag=tag,
        input_type=input_type,
        classes=classes,
    )
```

**Field Object:**

```python
@dataclass
class Field:
    selector: str
    locator: Locator
    page: Page
    tag: str           # "input", "select", "button", etc.
    input_type: str    # "text", "checkbox", "radio", etc.
    classes: str       # Class attribute value
```

### StrategyFactory (Strategy Dispatcher)

**Responsibility:** Select and execute appropriate strategy

**Key Methods:**

1. **get_strategy:**

   ```python
   async def get_strategy(self, field: Field) -> BaseFieldStrategy:
       for strategy in self.strategies:
           if await strategy.can_handle(field):
               return strategy
       raise FormFillingError(...)
   ```

2. **fill_data (Main Entry Point):**

   ```python
   async def fill_data(self, data: dict):
       for selector, value in data.items():
           field = await self.resolver.resolve_field(selector)
           strategy = await self.get_strategy(field)

           # Special case: formsets (button + list of dicts)
           if isinstance(value, list) and field.tag == "button":
               for item in value:
                   await strategy.fill(field, None)  # Click button
                   await self.fill_data(item)        # Fill row
           else:
               await strategy.fill(field, value)
   ```

**Strategy Registration:**

```python
def __init__(self, element_resolver: ElementResolver):
    self.resolver = element_resolver
    self.strategies = [
        ButtonStrategy(),
        CheckboxStrategy(),
        DatepickerStrategy(),
        FileStrategy(),
        InputStrategy(),
        RadioStrategy(),
        SelectStrategy(),
        Select2Strategy(),
    ]
```

**Order Matters:** Strategies checked in list order, first match wins.

---

## Services Deep Dive

### Validation Service

**Purpose:** Domain-specific assertions with consistent error messages

**Design Decision:** Use Playwright's `expect()` under the hood, but provide higher-level API

```python
class Validation:
    async def assert_visible(self, selector: str, timeout: int = 30000):
        """Wrapper around Playwright's expect with logging"""
        logger.debug(f"Asserting element visible: {selector}")
        await expect(self.page.locator(selector)).to_be_visible(timeout=timeout)

    async def assert_element_text(self, selector: str, expected: str):
        """Domain-specific: Check element text matches"""
        await expect(self.page.locator(selector)).to_have_text(expected)
```

**Why not use Playwright's expect() directly?**

- ✅ Consistent logging across framework
- ✅ Domain-specific assertions (e.g., `assert_url_contains`)
- ✅ Single place to add retries or custom error messages

### Wait Service

**Purpose:** Smart waiting with fallback strategies

**Key Implementation:**

```python
async def wait_for_page_load(self, timeout: int = 30000):
    """Smart waiting: Try networkidle, fallback to domcontentloaded"""
    try:
        await self.page.wait_for_load_state("networkidle", timeout=timeout)
        logger.debug("Page reached networkidle")
    except PlaywrightTimeoutError:
        logger.warning("Networkidle not reached, falling back to domcontentloaded")
        await self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
```

**Why Fallback?**

- Government/enterprise apps often have long-running AJAX
- `networkidle` may timeout unnecessarily
- `domcontentloaded` is more forgiving

### TabWindow Service

**Purpose:** Manage multi-tab/window workflows

**Design Challenges:**

1. **New tab detection:**

   ```python
   async def wait_for_new_page(self, timeout: int = 30000) -> Page:
       """Wait for new page to open (from link/button click)"""
       async with self.page.context.expect_page(timeout=timeout) as page_info:
           new_page = await page_info.value
       return new_page
   ```

2. **Context tracking:**

   ```python
   def __init__(self, page: Page):
       self.original_page = page  # Track original for switch_back
       self.page = page
   ```

3. **Tab switching:**

   ```python
   async def switch_to_tab(self, index: int):
       """Switch to tab by index"""
       pages = self.page.context.pages
       if index < len(pages):
           self.page = pages[index]
           await self.page.bring_to_front()
   ```

### Storage Service

**Purpose:** Cookie and storage management

**Implementation Notes:**

```python
async def add_cookie(self, cookie: dict):
    """Add cookie to browser context"""
    await self.page.context.add_cookies([cookie])

async def set_local_storage(self, key: str, value: str):
    """Set localStorage via JS evaluation"""
    await self.page.evaluate(
        f"localStorage.setItem('{key}', '{value}')"
    )
```

**Why Evaluate for Storage?**

- Playwright doesn't have native localStorage API
- Direct JS evaluation is most reliable

---

## Adding New Features

### Adding a New Field Type Strategy

**Scenario:** Need to support `<input type="color">` color pickers

**Steps:**

1. **Create Strategy File:** `core/ui/services/form/strategies/color_picker_strategy.py`

```python
from core.ui.services.form.base_strategy import BaseFieldStrategy
from core.ui.services.form.field import Field

class ColorPickerStrategy(BaseFieldStrategy):
    """Strategy for handling color picker inputs"""

    async def can_handle(self, field: Field) -> bool:
        """Check if this is a color picker"""
        return field.tag == "input" and field.input_type == "color"

    async def fill(self, field: Field, value: str) -> None:
        """
        Fill color picker with hex value.

        Args:
            field: Field object
            value: Hex color code (e.g., "#ff5733")
        """
        logger.debug(f"Filling color picker {field.selector} with {value}")

        # Color inputs accept hex format
        await field.locator.fill(value)

        logger.debug(f"Color picker {field.selector} filled")
```

2. **Register in StrategyFactory:** `core/ui/services/form/strategy_factory.py`

```python
from core.ui.services.form.strategies.color_picker_strategy import ColorPickerStrategy

class StrategyFactory:
    def __init__(self, element_resolver: ElementResolver):
        self.resolver = element_resolver
        self.strategies = [
            ButtonStrategy(),
            CheckboxStrategy(),
            ColorPickerStrategy(),  # ← Add here
            DatepickerStrategy(),
            # ... rest of strategies
        ]
```

3. **Test the Strategy:**

```python
async def test_color_picker_strategy(page):
    await page.goto('https://example.com/form')

    form_page = FormPage(page)
    await form_page.strategy_factory.fill_data({
        '#brandColor': '#ff5733',  # Should use ColorPickerStrategy
    })

    # Validate
    color_value = await page.locator('#brandColor').input_value()
    assert color_value == '#ff5733'
```

### Adding a New Component

**Scenario:** Need slider component for range inputs

**Steps:**

1. **Create Component File:** `core/ui/components/slider.py`

```python
import logging
from playwright.async_api import Page, Locator

logger = logging.getLogger(__name__)

class SliderComponent:
    """Component for range slider interactions"""

    def __init__(self, page: Page, selector: str, timeout: int = 30000):
        self.page = page
        self.selector = selector
        self.timeout = timeout
        self.locator: Locator = page.locator(selector)

    async def wait_for_visible(self):
        """Wait for slider to be visible"""
        await self.locator.wait_for(state="visible", timeout=self.timeout)

    async def set_value(self, value: int):
        """Set slider to specific value"""
        await self.wait_for_visible()
        logger.debug(f"Setting slider {self.selector} to {value}")

        # Set value via fill (works for range inputs)
        await self.locator.fill(str(value))

    async def get_value(self) -> int:
        """Get current slider value"""
        value = await self.locator.input_value()
        return int(value)

    async def slide_to_percentage(self, percentage: float):
        """
        Slide to percentage position (0-100).
        Useful when exact value is unknown.
        """
        await self.wait_for_visible()

        # Get slider bounding box
        box = await self.locator.bounding_box()
        if not box:
            raise ValueError(f"Could not get bounding box for {self.selector}")

        # Calculate position
        x = box['x'] + (box['width'] * percentage / 100)
        y = box['y'] + box['height'] / 2

        # Click at position
        await self.page.mouse.click(x, y)
```

2. **Create Corresponding Strategy:** `core/ui/services/form/strategies/slider_strategy.py`

```python
from core.ui.services.form.base_strategy import BaseFieldStrategy
from core.ui.services.form.field import Field
from core.ui.components.slider import SliderComponent

class SliderStrategy(BaseFieldStrategy):
    """Strategy for handling range sliders"""

    async def can_handle(self, field: Field) -> bool:
        return field.tag == "input" and field.input_type == "range"

    async def fill(self, field: Field, value: int) -> None:
        slider = SliderComponent(field.page, field.selector)
        await slider.set_value(value)
```

3. **Register Strategy:**

```python
# In StrategyFactory.__init__
self.strategies = [
    # ...
    SliderStrategy(),  # ← Add
    # ...
]
```

4. **Export Component:** `core/ui/components/__init__.py`

```python
from core.ui.components.slider import SliderComponent

__all__ = [
    'SliderComponent',
    # ... other components
]
```

### Adding a New Service

**Scenario:** Need clipboard service for copy/paste testing

**Steps:**

1. **Create Service File:** `core/ui/services/clipboard.py`

```python
import logging
from playwright.async_api import Page

logger = logging.getLogger(__name__)

class Clipboard:
    """Service for clipboard operations"""

    def __init__(self, page: Page):
        self.page = page

    async def copy_text(self, text: str):
        """Copy text to clipboard"""
        logger.debug(f"Copying text to clipboard: {text[:50]}...")

        await self.page.evaluate(f"""
            navigator.clipboard.writeText(`{text}`);
        """)

    async def get_clipboard_text(self) -> str:
        """Get text from clipboard"""
        logger.debug("Getting clipboard text")

        text = await self.page.evaluate("""
            navigator.clipboard.readText();
        """)

        return text

    async def paste_into_field(self, selector: str):
        """Paste clipboard content into field"""
        logger.debug(f"Pasting into {selector}")

        # Focus field
        await self.page.locator(selector).focus()

        # Trigger paste (Ctrl+V or Cmd+V)
        await self.page.keyboard.press('Control+V')
```

2. **Add to BasePage:** `core/ui/base_page.py`

```python
from core.ui.services.clipboard import Clipboard

class BasePage:
    # ... existing services

    @cached_property
    def clipboard(self) -> Clipboard:
        """Service for clipboard operations"""
        return Clipboard(self.page)
```

3. **Document in README:**

```markdown
### clipboard (Clipboard Operations)

**Use for:** Copy/paste testing

\`\`\`python
# Copy text
await self.clipboard.copy_text('Test data')

# Get clipboard content
text = await self.clipboard.get_clipboard_text()

# Paste into field
await self.clipboard.paste_into_field('#description')
\`\`\`
```

---

## Code Style Guidelines

### 1. Logging

**Always log operations:**

```python
# ✅ Good
async def fill(self, field: Field, value: str):
    logger.debug(f"Filling {field.selector} with value: {value}")
    await field.locator.fill(value)
    logger.debug(f"Successfully filled {field.selector}")

# ❌ Bad - No logging
async def fill(self, field: Field, value: str):
    await field.locator.fill(value)
```

**Log Levels:**

- `DEBUG`: Detailed operation flow
- `INFO`: Important state changes
- `WARNING`: Fallback strategies, unexpected but handled situations
- `ERROR`: Exceptions before re-raising

### 2. Type Hints

**Always use type hints:**

```python
# ✅ Good
async def fill_data(self, data: Dict[str, Any]) -> None:
    ...

def get_component(self) -> FileComponent:
    ...

# ❌ Bad - No type hints
async def fill_data(self, data):
    ...
```

### 3. Docstrings

**Use Google-style docstrings:**

```python
async def upload_files_with_preview_validation(
    self,
    file_paths: list[str],
    preview_element: str,
    timeout: int = 5000
) -> None:
    """
    Upload files and validate preview elements appear.

    Args:
        file_paths: List of absolute file paths to upload
        preview_element: Selector for preview container/items
        timeout: Maximum wait time for preview validation (ms)

    Raises:
        ValidationError: If preview count doesn't match uploaded files

    Example:
        >>> await file_comp.upload_files_with_preview_validation(
        ...     file_paths=['C:/file1.pdf', 'C:/file2.pdf'],
        ...     preview_element='.file-preview-item',
        ...     timeout=5000
        ... )
    """
```

### 4. Error Handling

**Use custom exceptions:**

```python
# ✅ Good
from core.utils.exceptions import FormFillingError

if not strategy:
    raise FormFillingError(
        f"No strategy found for field {field.selector}",
        field_selector=field.selector
    )

# ❌ Bad - Generic exception
if not strategy:
    raise Exception("No strategy found")
```

**Define Custom Exceptions:**

```python
# core/utils/exceptions.py

class FrameworkException(Exception):
    """Base exception for framework"""
    pass

class FormFillingError(FrameworkException):
    """Error during form filling operations"""
    def __init__(self, message: str, field_selector: str = None):
        super().__init__(message)
        self.field_selector = field_selector

class ValidationError(FrameworkException):
    """Error during validation operations"""
    pass
```

### 5. Naming Conventions

```python
# Classes: PascalCase
class StrategyFactory:
    pass

# Methods/Functions: snake_case
async def fill_data(self, data: dict):
    pass

# Private Methods: _leading_underscore
async def _internal_helper(self):
    pass

# Constants: UPPER_SNAKE_CASE
DEFAULT_TIMEOUT = 30000

# Services (in BasePage): snake_case
@cached_property
def strategy_factory(self) -> StrategyFactory:
    pass
```

---

## Performance Considerations

### 1. Lazy Loading Services

**Why:** Avoid instantiating unused services

```python
# ✅ Good - Lazy loading with @cached_property
class BasePage:
    @cached_property
    def strategy_factory(self) -> StrategyFactory:
        return StrategyFactory(self.element_resolver)  # Created only when accessed

# ❌ Bad - Eager loading
class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.strategy_factory = StrategyFactory(...)  # Always created
```

### 2. Batch Operations

**Why:** Reduce round-trips to browser

```python
# ✅ Good - Single strategy.fill_data call
await self.strategy_factory.fill_data({
    '#field1': 'value1',
    '#field2': 'value2',
    '#field3': 'value3',
})

# ❌ Bad - Multiple calls
await self.strategy_factory.fill_data({'#field1': 'value1'})
await self.strategy_factory.fill_data({'#field2': 'value2'})
await self.strategy_factory.fill_data({'#field3': 'value3'})
```

### 3. Smart Locators with Retry

**Why:** Handle stale elements automatically

```python
# core/utils/playwright_utils.py

def resolve_locator(page: Page, selector: str) -> Locator:
    """
    Create smart locator with auto-retry.
    Playwright's built-in auto-wait handles most cases.
    """
    return page.locator(selector)  # Playwright handles retries
```

### 4. Avoid Unnecessary Waits

```python
# ✅ Good - Let Playwright auto-wait
await self.page.locator('#field').fill('value')

# ❌ Bad - Explicit wait when not needed
await self.page.wait_for_selector('#field', state='visible')
await self.page.locator('#field').fill('value')  # Already waits!
```

---

## Testing the Framework

### Unit Testing Strategies

**Test Strategy Isolation:**

```python
# tests/unit/test_input_strategy.py

import pytest
from unittest.mock import Mock, AsyncMock
from core.ui.services.form.strategies.input_strategy import InputStrategy
from core.ui.services.form.field import Field

@pytest.mark.asyncio
async def test_input_strategy_can_handle():
    strategy = InputStrategy()

    # Mock field for text input
    field = Mock(spec=Field)
    field.tag = "input"
    field.input_type = "text"

    assert await strategy.can_handle(field) == True

@pytest.mark.asyncio
async def test_input_strategy_cannot_handle_select():
    strategy = InputStrategy()

    field = Mock(spec=Field)
    field.tag = "select"
    field.input_type = ""

    assert await strategy.can_handle(field) == False
```

### Integration Testing

**Test Full Strategy Flow:**

```python
# tests/integration/test_strategy_factory.py

import pytest
from playwright.async_api import Page
from core.ui.services.form.element_resolver import ElementResolver
from core.ui.services.form.strategy_factory import StrategyFactory

@pytest.mark.asyncio
async def test_fill_data_text_input(page: Page):
    await page.set_content("""
        <input id="name" type="text" />
    """)

    resolver = ElementResolver(page)
    factory = StrategyFactory(resolver)

    await factory.fill_data({'#name': 'John Doe'})

    value = await page.locator('#name').input_value()
    assert value == 'John Doe'

@pytest.mark.asyncio
async def test_fill_data_select_dropdown(page: Page):
    await page.set_content("""
        <select id="dept">
            <option value="eng">Engineering</option>
            <option value="sales">Sales</option>
        </select>
    """)

    resolver = ElementResolver(page)
    factory = StrategyFactory(resolver)

    await factory.fill_data({'#dept': 'Engineering'})

    selected = await page.locator('#dept').input_value()
    assert selected == 'eng'
```

### E2E Testing

**Test Real-World Scenarios:**

```python
# tests/e2e/test_employee_form.py

from pages.examples.complex_form_page import ComplexFormPage

@pytest.mark.asyncio
async def test_create_employee_full_workflow(page: Page):
    await page.goto('https://demo.app/employee/new')

    form_page = ComplexFormPage(page)

    await form_page.fill_employee_form({
        form_page.first_name_input: 'John',
        form_page.last_name_input: 'Doe',
        form_page.department_select: 'Engineering',
        form_page.start_date_picker: '2024-01-15',
        form_page.resume_input: 'C:/test_files/resume.pdf',
    })

    await page.click('#submitBtn')
    await form_page.validation.assert_visible('#successMessage')
```

---

## Troubleshooting & Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Common Issues

**1. Strategy Not Selected:**

```python
# Debug: Check what strategies can handle field
async def debug_strategy_selection(self, selector: str):
    field = await self.element_resolver.resolve_field(selector)
    print(f"Field: tag={field.tag}, type={field.input_type}, classes={field.classes}")

    for strategy in self.strategies:
        can_handle = await strategy.can_handle(field)
        print(f"{strategy.__class__.__name__}: {can_handle}")
```

**2. Element Not Found:**

```python
# Use Playwright's inspector
# Set environment variable before running tests:
# PWDEBUG=1 pytest tests/test_example.py

# Or pause in code:
await page.pause()  # Opens Playwright Inspector
```

**3. Timing Issues:**

```python
# Increase default timeout
class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.timeout = 60000  # Increase from 30000
```

### Performance Profiling

```python
import time

async def fill_data_with_profiling(self, data: dict):
    start = time.time()

    for selector, value in data.items():
        field_start = time.time()

        field = await self.resolver.resolve_field(selector)
        strategy = await self.get_strategy(field)
        await strategy.fill(field, value)

        field_time = time.time() - field_start
        print(f"{selector}: {field_time:.3f}s")

    total_time = time.time() - start
    print(f"Total fill_data time: {total_time:.3f}s")
```

---

## Best Practices Summary

### DO

- ✅ Use `@cached_property` for lazy-loaded services
- ✅ Log all operations at appropriate levels
- ✅ Use type hints for all methods
- ✅ Write docstrings with examples
- ✅ Use custom exceptions with context
- ✅ Test strategies in isolation
- ✅ Follow naming conventions
- ✅ Keep strategies focused (single responsibility)

### DON'T

- ❌ Eager-load services in `__init__`
- ❌ Hardcode selectors in framework code
- ❌ Use generic `Exception` class
- ❌ Skip logging for "small" operations
- ❌ Modify existing strategies to handle new field types (create new strategy instead)
- ❌ Couple components to specific page structures
- ❌ Skip type hints "for now"

---

## Extending for Scale

### Multi-Application Support

**Problem:** Supporting multiple applications with different field patterns

**Solution:** Application-specific strategy subclasses

```python
# core/ui/services/form/strategies/app_specific/

class GovernmentDatepickerStrategy(DatepickerStrategy):
    """Handle government app's custom datepicker widget"""

    async def can_handle(self, field: Field) -> bool:
        # Check for government-specific class
        return "gov-datepicker" in field.classes

    async def fill(self, field: Field, value: str) -> None:
        # Custom implementation for government widget
        await field.locator.click()
        await field.page.locator('.gov-calendar-input').fill(value)
        await field.page.keyboard.press('Enter')
```

Register before standard strategies:

```python
self.strategies = [
    GovernmentDatepickerStrategy(),  # Check custom first
    DatepickerStrategy(),             # Fallback to standard
    # ...
]
```

### Plugin Architecture

**For truly extensible framework:**

```python
# core/ui/plugin_manager.py

class PluginManager:
    def __init__(self):
        self.custom_strategies = []

    def register_strategy(self, strategy: BaseFieldStrategy):
        """Allow external registration of strategies"""
        self.custom_strategies.append(strategy)

    def get_all_strategies(self) -> list[BaseFieldStrategy]:
        """Return all strategies (custom + built-in)"""
        return self.custom_strategies + [
            InputStrategy(),
            SelectStrategy(),
            # ... built-ins
        ]

# Usage in StrategyFactory:
class StrategyFactory:
    def __init__(self, element_resolver: ElementResolver, plugin_manager: PluginManager = None):
        self.resolver = element_resolver
        self.plugin_manager = plugin_manager or PluginManager()
        self.strategies = self.plugin_manager.get_all_strategies()
```

---

## Contributing Guidelines

1. **Fork & Branch:** Create feature branch from `main`
2. **Code:** Follow style guidelines above
3. **Test:** Add unit + integration tests
4. **Document:** Update README.md and this guide
5. **PR:** Submit with clear description of changes

**PR Template:**

```markdown
## Description
[Describe the change]

## Type of Change
- [ ] Bug fix
- [ ] New feature (new strategy/component/service)
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Type hints added
- [ ] Docstrings added
- [ ] Logging added
- [ ] README.md updated
- [ ] DEVELOPER_GUIDE.md updated
```

---

**Questions?** Contact the SDET team or open an issue.
