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
    def random_alphanumeric(length: int = 10) -> str:
        """Generate a random alphanumeric string."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def random_digits(length: int = 10) -> str:
        """Generate a random string of digits."""
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def random_email(domain: str = None) -> str:
        """Generate a random email address."""
        username = TestDataGenerator.random_string(8).lower()
        domain = domain or random.choice(['gmail.com', 'yahoo.com', 'hotmail.com', 'test.com'])
        return f"{username}@{domain}"
    
    @staticmethod
    def random_phone(format_type: str = 'us') -> str:
        """
        Generate a random phone number.
        
        Args:
            format_type: 'us' for (XXX) XXX-XXXX, 'international' for +1XXXXXXXXXX, 'simple' for XXXXXXXXXX
        """
        digits = TestDataGenerator.random_digits(10)
        if format_type == 'us':
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif format_type == 'international':
            return f"+1{digits}"
        else:  # simple
            return digits
    
    @staticmethod
    def random_date(days_from_now: int = 0, date_format: str = '%Y-%m-%d') -> str:
        """
        Generate a random date, optionally offset from today.
        
        Args:
            days_from_now: Base offset from today
            date_format: strftime format string (default: YYYY-MM-DD)
        """
        base_date = datetime.now() + timedelta(days=days_from_now)
        random_days = random.randint(-365, 365)
        random_date = base_date + timedelta(days=random_days)
        return random_date.strftime(date_format)
    
    @staticmethod
    def random_future_date(max_days: int = 365, date_format: str = '%Y-%m-%d') -> str:
        """Generate a random date in the future."""
        random_days = random.randint(1, max_days)
        future_date = datetime.now() + timedelta(days=random_days)
        return future_date.strftime(date_format)
    
    @staticmethod
    def random_past_date(max_days: int = 365, date_format: str = '%Y-%m-%d') -> str:
        """Generate a random date in the past."""
        random_days = random.randint(1, max_days)
        past_date = datetime.now() - timedelta(days=random_days)
        return past_date.strftime(date_format)
    
    @staticmethod
    def random_number(min_val: int = 1, max_val: int = 1000) -> int:
        """Generate a random number within specified range."""
        return random.randint(min_val, max_val)
    
    @staticmethod
    def random_decimal(min_val: float = 0.0, max_val: float = 1000.0, decimals: int = 2) -> float:
        """Generate a random decimal number."""
        value = random.uniform(min_val, max_val)
        return round(value, decimals)
    
    @staticmethod
    def random_price(min_val: float = 1.0, max_val: float = 10000.0) -> str:
        """Generate a random price formatted as string with 2 decimals."""
        price = random.uniform(min_val, max_val)
        return f"{price:.2f}"
    
    @staticmethod
    def random_url(protocol: str = 'https', domain: str = None) -> str:
        """Generate a random URL."""
        domain = domain or f"{TestDataGenerator.random_string(8).lower()}.com"
        path = TestDataGenerator.random_string(6).lower()
        return f"{protocol}://{domain}/{path}"
    
    @staticmethod
    def random_username(length: int = 8) -> str:
        """Generate a random username (lowercase alphanumeric)."""
        return TestDataGenerator.random_alphanumeric(length).lower()
    
    @staticmethod
    def random_password(
        length: int = 12, 
        include_special: bool = True,
        include_numbers: bool = True,
        include_uppercase: bool = True
    ) -> str:
        """
        Generate a random password with specified complexity.
        
        Args:
            length: Password length
            include_special: Include special characters (!@#$%^&*)
            include_numbers: Include numbers
            include_uppercase: Include uppercase letters
        """
        chars = string.ascii_lowercase
        if include_uppercase:
            chars += string.ascii_uppercase
        if include_numbers:
            chars += string.digits
        if include_special:
            chars += '!@#$%^&*'
        
        return ''.join(random.choices(chars, k=length))
    
    @staticmethod
    def random_address() -> Dict[str, str]:
        """Generate a random address."""
        return {
            'street': f"{TestDataGenerator.random_number(1, 9999)} {TestDataGenerator.random_string(8).title()} St",
            'city': TestDataGenerator.random_string(8).title(),
            'state': random.choice(['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH']),
            'zip_code': TestDataGenerator.random_digits(5),
            'country': 'USA'
        }
    
    @staticmethod
    def random_name(name_type: str = 'full') -> str:
        """
        Generate a random name.
        
        Args:
            name_type: 'first', 'last', or 'full'
        """
        first_names = ['John', 'Jane', 'Michael', 'Emily', 'David', 'Sarah', 'James', 'Emma', 'Robert', 'Olivia']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
        
        if name_type == 'first':
            return random.choice(first_names)
        elif name_type == 'last':
            return random.choice(last_names)
        else:  # full
            return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    @staticmethod
    def random_company_name() -> str:
        """Generate a random company name."""
        prefixes = ['Tech', 'Global', 'Digital', 'Smart', 'Innovative', 'Advanced', 'Dynamic']
        suffixes = ['Solutions', 'Systems', 'Corp', 'Inc', 'Technologies', 'Enterprises', 'Group']
        return f"{random.choice(prefixes)} {random.choice(suffixes)}"
    
    @staticmethod
    def random_boolean() -> bool:
        """Generate a random boolean value."""
        return random.choice([True, False])
    
    @staticmethod
    def random_choice(options: List[Any]) -> Any:
        """Return a random choice from a list of options."""
        return random.choice(options)
    
    @staticmethod
    def random_ip_address() -> str:
        """Generate a random IP address."""
        return '.'.join(str(random.randint(0, 255)) for _ in range(4))
    
    @staticmethod
    def random_uuid() -> str:
        """Generate a random UUID-like string."""
        import uuid
        return str(uuid.uuid4())
    
    @staticmethod
    def random_color_hex() -> str:
        """Generate a random color in hex format."""
        return f"#{random.randint(0, 0xFFFFFF):06x}"


class TestHelpers:
    """Common helper functions for tests."""
    
    @staticmethod
    def get_test_file_path(filename: str) -> str:
        """Get the full path to a test file."""
        test_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(test_dir, 'test_files', filename)
    
    @staticmethod
    def create_temp_file(content: str, filename: str = None, extension: str = '.txt') -> str:
        """
        Create a temporary file with specified content.
        
        Args:
            content: Content to write to the file
            filename: Optional filename (will be auto-generated if not provided)
            extension: File extension (default: .txt)
        """
        if not filename:
            filename = f"temp_{TestDataGenerator.random_string(6)}{extension}"
        elif not filename.endswith(extension):
            filename = f"{filename}{extension}"
        
        temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    
    @staticmethod
    def create_temp_csv(data: List[List[str]], filename: str = None) -> str:
        """
        Create a temporary CSV file.
        
        Args:
            data: List of rows, where each row is a list of strings
            filename: Optional filename
        """
        import csv
        
        if not filename:
            filename = f"temp_{TestDataGenerator.random_string(6)}.csv"
        
        temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(data)
        
        return file_path
    
    @staticmethod
    def create_temp_json(data: Dict[str, Any], filename: str = None) -> str:
        """
        Create a temporary JSON file.
        
        Args:
            data: Dictionary to save as JSON
            filename: Optional filename
        """
        import json
        
        if not filename:
            filename = f"temp_{TestDataGenerator.random_string(6)}.json"
        
        temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return file_path
    
    @staticmethod
    def read_file(file_path: str) -> str:
        """Read and return the contents of a file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def read_json_file(file_path: str) -> Dict[str, Any]:
        """Read and parse a JSON file."""
        import json
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def read_csv_file(file_path: str) -> List[List[str]]:
        """Read and parse a CSV file."""
        import csv
        with open(file_path, 'r', encoding='utf-8') as f:
            return list(csv.reader(f))
    
    @staticmethod
    def file_exists(file_path: str) -> bool:
        """Check if a file exists."""
        return os.path.exists(file_path) and os.path.isfile(file_path)
    
    @staticmethod
    def directory_exists(dir_path: str) -> bool:
        """Check if a directory exists."""
        return os.path.exists(dir_path) and os.path.isdir(dir_path)
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Get file size in bytes."""
        return os.path.getsize(file_path) if TestHelpers.file_exists(file_path) else 0
    
    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """Get the file extension."""
        return os.path.splitext(file_path)[1]
    
    @staticmethod
    def ensure_directory(dir_path: str) -> str:
        """
        Ensure a directory exists, create it if it doesn't.
        
        Returns:
            The absolute path to the directory
        """
        os.makedirs(dir_path, exist_ok=True)
        return os.path.abspath(dir_path)
    
    @staticmethod
    def wait_for_condition(condition_func, timeout: int = 10, interval: float = 0.5) -> bool:
        """
        Wait for a condition to become true.
        
        Args:
            condition_func: Function that returns True when condition is met
            timeout: Maximum time to wait in seconds
            interval: Time between checks in seconds
            
        Returns:
            True if condition was met, False if timeout occurred
        """
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if condition_func():
                return True
            time.sleep(interval)
        
        return False
    
    @staticmethod
    def retry_on_exception(func, max_retries: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
        """
        Retry a function if it raises an exception.
        
        Args:
            func: Function to execute
            max_retries: Maximum number of retry attempts
            delay: Delay between retries in seconds
            exceptions: Tuple of exceptions to catch
            
        Returns:
            Result of the function if successful
            
        Raises:
            The last exception if all retries fail
        """
        import time
        
        for attempt in range(max_retries):
            try:
                return func()
            except exceptions as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(delay)
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize a string to be used as a filename.
        
        Removes or replaces characters that are not allowed in filenames.
        """
        # Remove/replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')
        
        return filename or 'unnamed'
    
    @staticmethod
    def get_timestamp(format_str: str = '%Y%m%d_%H%M%S') -> str:
        """Get current timestamp as formatted string."""
        return datetime.now().strftime(format_str)
    
    @staticmethod
    def compare_dicts(dict1: Dict, dict2: Dict, ignore_keys: List[str] = None) -> tuple[bool, List[str]]:
        """
        Compare two dictionaries and return differences.
        
        Args:
            dict1: First dictionary
            dict2: Second dictionary
            ignore_keys: List of keys to ignore in comparison
            
        Returns:
            Tuple of (are_equal, list_of_differences)
        """
        ignore_keys = ignore_keys or []
        differences = []
        
        # Filter out ignored keys
        filtered_dict1 = {k: v for k, v in dict1.items() if k not in ignore_keys}
        filtered_dict2 = {k: v for k, v in dict2.items() if k not in ignore_keys}
        
        # Check for keys only in dict1
        for key in filtered_dict1:
            if key not in filtered_dict2:
                differences.append(f"Key '{key}' only in first dict")
            elif filtered_dict1[key] != filtered_dict2[key]:
                differences.append(f"Key '{key}': {filtered_dict1[key]} != {filtered_dict2[key]}")
        
        # Check for keys only in dict2
        for key in filtered_dict2:
            if key not in filtered_dict1:
                differences.append(f"Key '{key}' only in second dict")
        
        return len(differences) == 0, differences
    
    @staticmethod
    def merge_dicts(*dicts: Dict) -> Dict:
        """
        Merge multiple dictionaries into one.
        Later dictionaries override earlier ones.
        """
        result = {}
        for d in dicts:
            result.update(d)
        return result
    
    @staticmethod
    def cleanup_temp_files():
        """Clean up temporary files created during tests."""
        temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)
    
    @staticmethod
    def cleanup_directory(dir_path: str, ignore_errors: bool = True):
        """
        Remove a directory and all its contents.
        
        Args:
            dir_path: Path to directory to remove
            ignore_errors: If True, ignore errors during removal
        """
        if os.path.exists(dir_path):
            import shutil
            shutil.rmtree(dir_path, ignore_errors=ignore_errors)