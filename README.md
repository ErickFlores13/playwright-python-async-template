# playwright-python-async-template# 🧩 Playwright Python Automation Framework

A **modular, scalable, and maintainable test automation framework** built with **Playwright + Python**, designed for modern web applications.

---

## 🚀 Key Features

- 🔹 **Modular architecture:** separation between `BasePage`, `StandardWebPage`, and module-specific `PageObjects`.
- 🔹 **Compatible with Django, React, and generic web apps.**
- 🔹 **Database integration:** built-in support for **PostgreSQL** and **Redis** for backend validations.
- 🔹 **Fully CI/CD ready:** seamless **Jenkins** integration via Docker agents.
- 🔹 **Automatic reporting:** generates and publishes **Allure Reports**.
- 🔹 **Discord notifications:** execution results sent automatically with report links.
- 🔹 **Parallel execution** using `pytest-xdist`.
- 🔹 **Comprehensive documentation** and technical usage guide included.

---

## 🏗️ Project Structure

```bash
.
├── conftest.py               # Global Pytest configuration and fixtures
├── base_page.py              # Core base class with reusable interaction methods
├── standard_web_page.py      # Generic methods for web page interactions
├── consts.py                 # Global constants and selectors
├── redis_client.py           # Redis connection client
├── database.py               # PostgreSQL connection and query module
├── requirements.txt          # Project dependencies
├── Dockerfile                # Docker setup for CI/CD execution
├── README.md                 # Project documentation
└── tests/                    # Test cases and suites
```

## ⚙️ Setup and Installation

Clone the repository:
```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Configure environment variables.

## 🧪 Running Tests

Local execution:
```bash
pytest --headed --alluredir=reports/allure-results
```

View Allure report:
```bash
allure serve reports/allure-results
```

Run in parallel:
```bash
pytest -n auto
```

### 🐳 Run with Docker
```bash
docker build -t playwright-framework .
docker run --rm -v $(pwd)/reports:/app/reports playwright-framework
```

## 🔔 Notifications

After each run, the framework sends a Discord notification containing:

- Execution status (✅ Passed / ❌ Failed)
- Total executed tests
- Direct link to the Allure report

## 🧱 Framework Design

The framework follows the Page Object Model (POM) pattern, structured for scalability and reusability.

## 🧱 Framework Design

The framework follows the **Page Object Model (POM)** pattern, structured for scalability and reusability.

| File | Description |
|------|--------------|
| `base_page.py` | Core class that provides generic browser interaction methods such as click, fill, wait, and assertions. |
| `standard_web_page.py` | Defines reusable web-level actions like filtering, validating table data, and handling buttons. |
| `consts.py` | Centralized constants and selectors used across the framework. |
| `database.py` | Manages PostgreSQL connections and query execution for backend validations. |
| `redis_client.py` | Provides connection and interaction methods with Redis for cache or queue validation. |
| `conftest.py` | Contains global Pytest fixtures, hooks, and environment setup. |
| `Dockerfile` | Container configuration for running tests in CI/CD environments. |
| `requirements.txt` | List of dependencies required for the framework. |
| `tests/` | Directory containing test suites and modular test files. |


## 🧩 Integrations

- Jenkins CI/CD: Dockerized pipeline with Allure report publishing
- Discord Webhook: automated result notifications
- Allure Report: interactive HTML reports with failure screenshots

## 📚 Future Enhancements

- Implement optimized parallel test suites
- Add mobile automation (Appium integration)
- Include visual regression testing
- Expand multi-browser support (Chrome, Firefox, WebKit)

### 👨‍💻 Author

Erick Guadalupe Félix Flores
Senior QA Automation Engineer
Certifications: Scrum Developer Certified Expert · ITIL V4