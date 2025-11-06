"""
Custom exceptions for the Playwright Python Async Template.

This module defines custom exceptions used throughout the framework
for better error handling and debugging.

Author: Erick Guadalupe Félix Flores
License: MIT
"""


class ElementNotFoundError(Exception):
    """
    Raised when an expected element is not found on the page.
    
    This exception is used when waiting for elements that should be present
    but are not found within the specified timeout period.
    """
    
    def __init__(self, selector: str, timeout: int = None):
        self.selector = selector
        self.timeout = timeout
        
        if timeout:
            message = f"Element '{selector}' not found within {timeout}ms timeout"
        else:
            message = f"Element '{selector}' not found"
            
        super().__init__(message)


class ValidationError(Exception):
    """
    Raised when form validation fails or validation checks don't pass.
    
    This exception is used for form validation errors and data validation
    issues during test execution.
    """
    
    def __init__(self, field: str = None, message: str = None):
        self.field = field
        
        if field and message:
            error_message = f"Validation error for field '{field}': {message}"
        elif field:
            error_message = f"Validation error for field '{field}'"
        elif message:
            error_message = f"Validation error: {message}"
        else:
            error_message = "Validation error occurred"
            
        super().__init__(error_message)


class Select2Error(Exception):
    """
    Raised when Select2 component interactions fail.
    
    This exception is used specifically for Select2-related errors
    such as option not found, dropdown not opening, etc.
    """
    
    def __init__(self, selector: str, operation: str, message: str = None):
        self.selector = selector
        self.operation = operation
        
        if message:
            error_message = f"Select2 error on '{selector}' during '{operation}': {message}"
        else:
            error_message = f"Select2 error on '{selector}' during '{operation}'"
            
        super().__init__(error_message)


class ConfigurationError(Exception):
    """
    Raised when there are configuration-related issues.
    
    This exception is used for missing or invalid configuration values
    that prevent tests from running properly.
    """
    
    def __init__(self, config_key: str = None, message: str = None):
        self.config_key = config_key
        
        if config_key and message:
            error_message = f"Configuration error for '{config_key}': {message}"
        elif config_key:
            error_message = f"Configuration error: missing or invalid '{config_key}'"
        elif message:
            error_message = f"Configuration error: {message}"
        else:
            error_message = "Configuration error occurred"
            
        super().__init__(error_message)


class DatabaseError(Exception):
    """
    Raised when database operations fail.
    
    This exception is used for database connection issues,
    query failures, or data validation problems.
    """
    
    def __init__(self, operation: str = None, message: str = None):
        self.operation = operation
        
        if operation and message:
            error_message = f"Database error during '{operation}': {message}"
        elif operation:
            error_message = f"Database error during '{operation}'"
        elif message:
            error_message = f"Database error: {message}"
        else:
            error_message = "Database error occurred"
            
        super().__init__(error_message)


class RedisError(Exception):
    """
    Raised when Redis operations fail.
    
    This exception is used for Redis connection issues,
    cache operations failures, or data retrieval problems.
    """
    
    def __init__(self, operation: str = None, message: str = None):
        self.operation = operation
        
        if operation and message:
            error_message = f"Redis error during '{operation}': {message}"
        elif operation:
            error_message = f"Redis error during '{operation}'"
        elif message:
            error_message = f"Redis error: {message}"
        else:
            error_message = "Redis error occurred"
            
        super().__init__(error_message)