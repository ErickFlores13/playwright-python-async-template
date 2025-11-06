# 🧩 Jenkins CI Pipeline Template

This repository includes a **Jenkins pipeline template** designed for running automated test suites with **Playwright + Pytest + Allure** inside a controlled **Docker environment**.  
It’s fully adaptable for both small projects and enterprise-level frameworks.

---

## 🚀 Overview

This pipeline automates the full test lifecycle:

1. **Checkout the repository**
2. **Set up the Python environment** inside Docker
3. **Install Playwright browsers**
4. **Execute test suites** (smoke, regression, etc.)
5. **Generate Allure reports**
6. **Publish HTML results to Jenkins**
7. **Send test results via Discord notification**

---

## 🧱 Folder Structure

ci/
 ├── Jenkinsfile          # Main CI pipeline configuration  
 └── README.md            # This documentation file  

If your framework template has a standard structure, your project root may look like this:

project-root/
 ├── pages/
 │   ├── base_page.py
 │   └── standard_web_page.py
 ├── helpers/
 │   ├── redis_client.py
 │   └── database.py
 ├── utils/
 │   └── consts.py
 ├── tests/
 │   └── test_suites/
 ├── Dockerfile
 ├── Jenkinsfile
 ├── requirements.txt
 └── pytest.ini

---

## ⚙️ Environment Variables

The following variables should be configured in **Jenkins** (either in the job or pipeline configuration):

| Variable | Description | Example |
|-----------|--------------|----------|
| `DISCORD_WEBHOOK` | Webhook credential for Discord notifications | `credentials('discord-webhook-id')` |
| `REPORT_URL` | Base URL for published test reports | `https://reports.company.com/myproject` |
| `GITHUB_SSH_KEY` | Credential for accessing private GitHub repositories | `credentials('github-ssh-key-id')` |

---

## 🧪 Test Configuration

By default, the pipeline executes tests marked as `@pytest.mark.smoke_test`.  
You can change the marker or add other test categories as needed:

pytest --alluredir=report/${env.REPORT_NAME} \
       -v --ignore=.python_packages/ \
       -m smoke_test --reruns 3 --reruns-delay 3

To execute all tests instead:

pytest --alluredir=report/${env.REPORT_NAME} -v --ignore=.python_packages/

---

## 📦 Docker Integration

The `Build and Run Tests` stage runs inside a **Docker container** built from your project’s `Dockerfile`.  
This ensures reproducible results and eliminates environment drift.

Example `Dockerfile` (minimal):

FROM python:3.11-slim  
WORKDIR /app  
COPY . .  
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    playwright install --with-deps

---

## 📢 Notifications

At the end of the build, the pipeline automatically sends a **Discord message** summarizing the execution result.

Example message:

🚀 my-qa-framework - Test Execution  
✅ Result: SUCCESS  
🔗 Job: QA-Automation/my-qa-template  
📄 Report: https://reports.company.com/my-qa-template/2025-11-05_03-00-00

---

## 🧹 Post Actions

| Status | Action |
|---------|---------|
| ✅ **Success** | Displays a success message and keeps report |
| ❌ **Failure** | Sends Discord alert with report link |
| ⚠️ **Unstable** | Marks flaky or rerun-failed tests |
| 🧽 **Always** | Cleans the workspace to free disk space |

---

## 🧭 Customization

To adapt this pipeline for your project:
1. Update the repository URL and branch in the `Checkout` stage.
2. Replace credential IDs (`discord-webhook-id`, `github-ssh-key-id`).
3. Modify test commands or tags according to your suite.
4. Optionally, adjust the cron schedule under the `triggers` section.

---

## 📚 Summary

| Feature | Description |
|----------|-------------|
| **Language** | Python 3 + Playwright |
| **Test Runner** | Pytest |
| **Reporting** | Allure |
| **Notification** | Discord |
| **Environment** | Docker |
| **Execution** | Jenkins Declarative Pipeline |

---

💡 **Tip:** For best maintainability, keep this pipeline as a template within your QA framework so other teams can easily extend it for their own test suites.

---

**Author:** Erick Felix Flores
