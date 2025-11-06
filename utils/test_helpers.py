"""
Utility functions for test data generation and common test operations.
"""

import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os


class TestDataGenerator:
    """Utility class for generating test data."""
    
    @staticmethod
    def random_string(length: int = 10) -> str:
        """Generate a random string of specified length."""
        return ''.join(random.choices(string.ascii_letters, k=length))
    
    @staticmethod
    def random_email() -> str:
        """Generate a random email address."""
        username = TestDataGenerator.random_string(8).lower()
        domain = random.choice(['gmail.com', 'yahoo.com', 'hotmail.com', 'test.com'])
        return f"{username}@{domain}"
    
    @staticmethod
    def random_phone() -> str:
        """Generate a random phone number."""
        return ''.join(random.choices(string.digits, k=10))
    
    @staticmethod
    def random_date(days_from_now: int = 0) -> str:
        """Generate a random date, optionally offset from today."""
        base_date = datetime.now() + timedelta(days=days_from_now)
        random_days = random.randint(-365, 365)
        random_date = base_date + timedelta(days=random_days)
        return random_date.strftime('%Y-%m-%d')
    
    @staticmethod
    def random_number(min_val: int = 1, max_val: int = 1000) -> int:
        """Generate a random number within specified range."""
        return random.randint(min_val, max_val)
    
    @staticmethod
    def create_user_data() -> Dict[str, Any]:
        """Create a complete user data dictionary."""
        return {
            'username': TestDataGenerator.random_string(8),
            'email': TestDataGenerator.random_email(),
            'first_name': TestDataGenerator.random_string(6).title(),
            'last_name': TestDataGenerator.random_string(8).title(),
            'phone': TestDataGenerator.random_phone(),
            'age': TestDataGenerator.random_number(18, 80),
            'birth_date': TestDataGenerator.random_date(-7300)  # About 20 years ago
        }


class TestHelpers:
    """Common helper functions for tests."""
    
    @staticmethod
    def get_test_file_path(filename: str) -> str:
        """Get the full path to a test file."""
        test_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(test_dir, 'test_files', filename)
    
    @staticmethod
    def create_temp_file(content: str, filename: str = None) -> str:
        """Create a temporary file with specified content."""
        if not filename:
            filename = f"temp_{TestDataGenerator.random_string(6)}.txt"
        
        temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    
    @staticmethod
    def cleanup_temp_files():
        """Clean up temporary files created during tests."""
        temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)


class FormDataBuilder:
    """Builder class for creating complex form data structures."""
    
    def __init__(self):
        self.data = {}
    
    def add_text_field(self, selector: str, value: str = None) -> 'FormDataBuilder':
        """Add a text field to the form data."""
        self.data[selector] = value or TestDataGenerator.random_string()
        return self
    
    def add_email_field(self, selector: str, value: str = None) -> 'FormDataBuilder':
        """Add an email field to the form data."""
        self.data[selector] = value or TestDataGenerator.random_email()
        return self
    
    def add_checkbox(self, selector: str, checked: bool = True) -> 'FormDataBuilder':
        """Add a checkbox field to the form data."""
        self.data[selector] = checked
        return self
    
    def add_select_option(self, selector: str, option: str) -> 'FormDataBuilder':
        """Add a select field to the form data."""
        self.data[selector] = option
        return self
    
    def add_file_upload(self, selector: str, file_path: str) -> 'FormDataBuilder':
        """Add a file upload field to the form data."""
        self.data[selector] = file_path
        return self
    
    def add_button_action(self, selector: str, actions: List[Dict]) -> 'FormDataBuilder':
        """Add button actions with nested data."""
        self.data[selector] = actions
        return self
    
    def add_select2_field(self, selector: str, options: List[str]) -> 'FormDataBuilder':
        """Add a Select2 field with multiple options."""
        self.data[selector] = options
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build and return the form data dictionary."""
        return self.data.copy()


class ValidationDataBuilder:
    """Builder class for creating validation data structures."""
    
    def __init__(self):
        self.validation_data = {}
    
    def expect_text_value(self, selector: str, expected_value: str) -> 'ValidationDataBuilder':
        """Add text value expectation."""
        self.validation_data[selector] = expected_value
        return self
    
    def expect_checkbox_state(self, selector: str, should_be_checked: bool) -> 'ValidationDataBuilder':
        """Add checkbox state expectation."""
        self.validation_data[selector] = should_be_checked
        return self
    
    def expect_select_option(self, selector: str, expected_option: str) -> 'ValidationDataBuilder':
        """Add select option expectation."""
        self.validation_data[selector] = expected_option
        return self
    
    def expect_multiple_values(self, selector: str, expected_values: List[str]) -> 'ValidationDataBuilder':
        """Add multiple values expectation."""
        self.validation_data[selector] = expected_values
        return self
    
    def expect_visible_options(self, selector: str, options: List[str]) -> 'ValidationDataBuilder':
        """Add visible options expectation (for Select2 or similar)."""
        self.validation_data[selector] = set(options)
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build and return the validation data dictionary."""
        return self.validation_data.copy()