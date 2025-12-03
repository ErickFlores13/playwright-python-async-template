from abc import ABC, abstractmethod
from typing import Dict


class AuthStrategy(ABC):
    """
    Base class for authentication strategies.

    All authentication methods must implement this interface.

    Example:
        >>> class CustomAuth(AuthStrategy):
        ...     async def get_auth_headers(self):
        ...         return {'X-Custom-Auth': 'value'}
    """

    @abstractmethod
    async def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers to add to requests.

        Returns:
            Dict of headers to add to request
        """
        pass
