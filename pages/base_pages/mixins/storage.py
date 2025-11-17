import logging
from playwright.async_api import Page
from utils.exceptions import (
    ValidationError,
    ConfigurationError,
)

logger = logging.getLogger(__name__)

class StorageMixin:
    """
    Generic base page with overridable playwright methods that allow a custom-made test automation.
    """

    def __init__(self, page: Page) -> None:
        if not page:
            raise ConfigurationError(
                config_key="page",
                message="Page instance cannot be None or empty"
            )
            
        self.page = page
    
    async def set_cookie(
            self, 
            name: str, 
            value: str, 
            domain: str = None, 
            path: str = '/') -> None:
        """
        Sets a cookie in the browser context.
        
        Args:
            name (str): Cookie name.
            value (str): Cookie value.
            domain (str, optional): Cookie domain (defaults to current domain).
            path (str): Cookie path (default: '/').
            
        Example:
            await self.set_cookie('session_id', 'abc123')
        """
        if domain is None:
            domain = await self.page.evaluate('() => window.location.hostname')
        
        await self.page.context.add_cookies([{
            'name': name,
            'value': value,
            'domain': domain,
            'path': path
        }])
        logger.info(f"Cookie set: {name}={value}")

    async def get_cookie(self, name: str) -> dict:
        """
        Retrieves a specific cookie by name.
        
        Args:
            name (str): Cookie name.
            
        Returns:
            dict: Cookie object with name, value, domain, path, etc.
            
        Raises:
            ValidationError: if cookie not found.
        """
        cookies = await self.page.context.cookies()
        
        for cookie in cookies:
            if cookie['name'] == name:
                return cookie
        
        raise ValidationError(
            field=name,
            message=f"Cookie '{name}' not found"
        )

    async def get_all_cookies(self) -> list:
        """
        Retrieves all cookies for the current context.
        
        Returns:
            list: List of cookie dictionaries.
        """
        return await self.page.context.cookies()

    async def delete_cookie(self, name: str) -> None:
        """
        Deletes a specific cookie by name.
        
        Args:
            name (str): Cookie name to delete.
        """
        cookies = await self.page.context.cookies()
        filtered_cookies = [c for c in cookies if c['name'] != name]
        
        await self.page.context.clear_cookies()
        await self.page.context.add_cookies(filtered_cookies)
        logger.info(f"Cookie deleted: {name}")

    async def clear_all_cookies(self) -> None:
        """
        Clears all cookies from the browser context.
        """
        await self.page.context.clear_cookies()
        logger.info("All cookies cleared")

    async def set_local_storage(self, key: str, value: str) -> None:
        """
        Sets a value in localStorage.
        
        Args:
            key (str): localStorage key.
            value (str): Value to store (will be converted to string).
            
        Example:
            await self.set_local_storage('user_preference', 'dark_mode')
        """
        await self.page.evaluate(
            f"() => window.localStorage.setItem('{key}', '{value}')"
        )
        logger.info(f"localStorage set: {key}={value}")

    async def get_local_storage(self, key: str) -> str:
        """
        Retrieves a value from localStorage.
        
        Args:
            key (str): localStorage key.
            
        Returns:
            str: Value from localStorage (or None if not found).
        """
        value = await self.page.evaluate(
            f"() => window.localStorage.getItem('{key}')"
        )
        return value

    async def get_all_local_storage(self) -> dict:
        """
        Retrieves all localStorage items.
        
        Returns:
            dict: Dictionary of all localStorage key-value pairs.
        """
        return await self.page.evaluate(
            """() => {
                let items = {};
                for (let i = 0; i < localStorage.length; i++) {
                    let key = localStorage.key(i);
                    items[key] = localStorage.getItem(key);
                }
                return items;
            }"""
        )

    async def remove_local_storage(self, key: str) -> None:
        """
        Removes a specific item from localStorage.
        
        Args:
            key (str): localStorage key to remove.
        """
        await self.page.evaluate(
            f"() => window.localStorage.removeItem('{key}')"
        )
        logger.info(f"localStorage removed: {key}")

    async def clear_local_storage(self) -> None:
        """
        Clears all localStorage items.
        """
        await self.page.evaluate("() => window.localStorage.clear()")
        logger.info("localStorage cleared")

    async def set_session_storage(self, key: str, value: str) -> None:
        """
        Sets a value in sessionStorage.
        
        Args:
            key (str): sessionStorage key.
            value (str): Value to store.
        """
        await self.page.evaluate(
            f"() => window.sessionStorage.setItem('{key}', '{value}')"
        )
        logger.info(f"sessionStorage set: {key}={value}")

    async def get_session_storage(self, key: str) -> str:
        """
        Retrieves a value from sessionStorage.
        
        Args:
            key (str): sessionStorage key.
            
        Returns:
            str: Value from sessionStorage (or None if not found).
        """
        value = await self.page.evaluate(
            f"() => window.sessionStorage.getItem('{key}')"
        )
        return value

    async def clear_session_storage(self) -> None:
        """
        Clears all sessionStorage items.
        """
        await self.page.evaluate("() => window.sessionStorage.clear()")
        logger.info("sessionStorage cleared")

    async def clear_all_storage(self) -> None:
        """
        Clears cookies, localStorage, and sessionStorage.
        Useful for resetting browser state between tests.
        """
        await self.clear_all_cookies()
        await self.clear_local_storage()
        await self.clear_session_storage()
        logger.info("All storage cleared (cookies, localStorage, sessionStorage)")