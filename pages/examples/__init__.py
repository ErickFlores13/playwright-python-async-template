"""
Example Page Objects demonstrating proper POM pattern.

These page objects show how to structure your page classes for different modules.
"""

from .authentication_page import AuthenticationPage
from .user_management_page import UserManagementPage
from .product_management_page import ProductManagementPage

__all__ = [
    'AuthenticationPage',
    'UserManagementPage',
    'ProductManagementPage',
]
