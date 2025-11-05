FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps chromium

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p reports/allure-results screenshots

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTEST_CURRENT_TEST=""

# Default command
CMD ["pytest", "--alluredir=reports/allure-results", "-v"]