# Contributing to Playwright Python Async Template

Thank you for your interest in contributing to this project! This document provides guidelines and instructions for contributing.

## 🎯 Ways to Contribute

- 🐛 **Bug Reports**: Report bugs via GitHub issues
- 💡 **Feature Requests**: Suggest new features or improvements
- 📝 **Documentation**: Improve or add documentation
- 🔧 **Code Contributions**: Submit bug fixes or new features
- 💬 **Discussion**: Share ideas and help others

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- Virtual environment tool (venv, virtualenv, conda)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/playwright-python-async-template.git
   cd playwright-python-async-template
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

4. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📝 Code Guidelines

### Python Style Guide

- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and single-purpose

### Code Style Example

```python
async def my_function(param: str) -> bool:
    """
    Short description of what the function does.
    
    Args:
        param: Description of the parameter
        
    Returns:
        Description of return value
        
    Example:
        >>> result = await my_function("test")
    """
    # Implementation here
    return True
```

### Testing Guidelines

1. **Write Tests**: All new features should include tests
2. **Run Tests**: Ensure all tests pass before submitting
   ```bash
   pytest tests/
   ```
3. **Test Coverage**: Aim for high test coverage
4. **Example Tests**: Add example tests when appropriate

### Documentation

- Update README.md if adding features
- Update GETTING_STARTED.md for user-facing changes
- Add inline comments for complex logic
- Include docstrings for all public methods

## 🔄 Pull Request Process

### Before Submitting

1. **Update Documentation**: Ensure all docs are updated
2. **Run Tests**: All tests should pass
3. **Code Quality**: Follow style guidelines
4. **Commit Messages**: Use clear, descriptive messages

### Commit Message Format

```
type: Short description (50 chars max)

Longer description if needed. Explain what and why, not how.

Closes #issue_number
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat: Add support for custom browser configurations

Allow users to pass custom browser launch options through
environment variables.

Closes #42
```

```
fix: Handle timeout errors in async page loads

Added proper error handling for timeout scenarios when
pages take too long to load.

Fixes #38
```

### Submitting PR

1. **Push Changes**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request** on GitHub

3. **Fill PR Template**:
   - Description of changes
   - Related issue number
   - Testing performed
   - Screenshots (if UI changes)

4. **Wait for Review**: Maintainers will review your PR

5. **Address Feedback**: Make requested changes if needed

## 🐛 Bug Reports

### Before Reporting

- Check if bug already exists in issues
- Test with latest version
- Gather necessary information

### Bug Report Template

```markdown
**Description**
A clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., Windows 10, macOS 12, Ubuntu 20.04]
- Python version: [e.g., 3.11.2]
- Framework version: [e.g., 1.0.0]
- Browser: [e.g., Chromium 128.0]

**Additional Context**
- Error messages
- Screenshots
- Log files
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Feature Description**
Clear description of the feature.

**Use Case**
Explain the use case and why it's needed.

**Proposed Solution**
Your idea for how to implement it.

**Alternatives Considered**
Other approaches you've thought about.

**Additional Context**
Any other relevant information.
```

## 🔍 Code Review Process

### What We Look For

1. **Functionality**: Does it work as intended?
2. **Tests**: Are there adequate tests?
3. **Documentation**: Is it well documented?
4. **Code Quality**: Is it clean and maintainable?
5. **Breaking Changes**: Are they necessary and documented?

### Review Timeline

- Initial review within 48-72 hours
- Feedback provided constructively
- Multiple iterations if needed

## 📋 Project Structure

When contributing, be aware of the project structure:

```
.
├── pages/              # Page object classes
├── helpers/            # Helper utilities (DB, Redis, etc.)
├── utils/              # Configuration and constants
├── tests/              # Test files
│   └── examples/       # Example tests
├── .github/            # GitHub workflows
├── conftest.py         # Pytest configuration
├── requirements.txt    # Dependencies
└── docs/               # Additional documentation
```

## 🎨 Adding New Page Objects

When adding new page objects:

```python
# pages/my_new_page.py
from pages.base_page import BasePage

class MyNewPage(BasePage):
    """
    Page object for [describe the page].
    
    This page provides methods for [describe functionality].
    """
    
    def __init__(self, page):
        super().__init__(page)
        # Define selectors
        self.my_selector = '#my-element'
    
    async def my_action(self):
        """
        Description of what this action does.
        """
        await self.page.click(self.my_selector)
```

## 🧪 Adding Tests

When adding new tests:

```python
# tests/test_my_feature.py
import pytest
from pages.my_new_page import MyNewPage

@pytest.mark.asyncio
class TestMyFeature:
    """Test suite for my feature."""
    
    async def test_something(self, page):
        """Test that something works correctly."""
        my_page = MyNewPage(page)
        await my_page.my_action()
        # Add assertions
```

## 📊 Performance Considerations

- Use async/await properly
- Avoid unnecessary waits
- Use efficient selectors
- Minimize page reloads

## 🔒 Security

- Don't commit secrets or credentials
- Use environment variables for sensitive data
- Review code for security issues
- Report security vulnerabilities privately

## 📞 Getting Help

- **Questions**: Open a discussion on GitHub
- **Bugs**: Create an issue
- **Chat**: [If you have a chat channel]

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes (for significant contributions)
- README acknowledgments (for major features)

---

Thank you for contributing! 🎉
