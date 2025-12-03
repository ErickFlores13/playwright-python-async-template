import asyncio
import logging
import random
from typing import Callable, TypeVar, Optional, Dict
from core.api.config import RetryConfig
from core.api.models import RetryExhaustedError, APIError

logger = logging.getLogger(__name__)

T = TypeVar('T')

class RetryService:
    """
    Service for executing functions with retry logic.
    
    Implements exponential backoff with optional jitter to prevent
    thundering herd problem. Supports configurable retry conditions
    based on status codes and exception types.
    """
    
    def __init__(self, config: RetryConfig):
        """
        Initialize retry service.
        
        Args:
            config: Retry configuration
        """
        self.config = config
        self._attempt_count = 0
    
    async def execute(
        self,
        func: Callable[..., T],
        *args,
        **kwargs
    ) -> T:
        """
        Execute function with retry logic and exponential backoff.
        
        Args:
            func: Async function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
                method (str): HTTP method (GET, POST, PUT, PATCH, DELETE)
                headers (Dict[str, str]): Request headers
                params (Dict[str, Any]): Query parameters
                data (Any): Request body
                timeout (float): Request timeout
        
        Returns:
            Result from successful function execution
        
        Raises:
            RetryExhaustedError: When all retry attempts fail
        """
        last_exception: Optional[Exception] = None
        self._attempt_count = 0
        
        http_method = kwargs.get('method', 'GET').upper()
        headers = kwargs.get('headers', {})
        
        for attempt in range(1, self.config.max_attempts + 1):
            self._attempt_count = attempt
            
            try:
                logger.debug(f"Retry attempt {attempt}/{self.config.max_attempts}")
                result = await func(*args, **kwargs)
                
                if hasattr(result, 'status_code') and self._should_retry_status(result.status_code, http_method, headers):
                    logger.warning(f"Attempt {attempt} failed with status {result.status_code}, retrying...")
                    last_exception = APIError(f"Status {result.status_code}", status_code=result.status_code)
                else:
                    if attempt > 1:
                        logger.info(f"Request succeeded on attempt {attempt}")
                    return result
                    
            except Exception as e:
                last_exception = e
                
                if self._should_retry_exception(e):
                    logger.warning(f"Attempt {attempt} failed with {type(e).__name__}: {str(e)}, retrying...")
                else:
                    logger.error(f"Non-retryable exception: {type(e).__name__}: {str(e)}")
                    raise
            
            if attempt < self.config.max_attempts:
                delay = self._calculate_delay(attempt)
                logger.debug(f"Waiting {delay:.2f}s before next attempt")
                await asyncio.sleep(delay)
        
        error_msg = f"Request failed after {self.config.max_attempts} attempts. Last error: {type(last_exception).__name__}: {str(last_exception)}"
        logger.error(error_msg)
        
        raise RetryExhaustedError(
            message=error_msg,
            status_code=getattr(last_exception, 'status_code', None)
        )
    
    def _should_retry_status(
            self, 
            status_code: int, 
            method: str = 'GET', 
            headers: Optional[Dict[str, str]] = None
            ) -> bool:
        """
        Determine if status code should trigger retry based on method and idempotency.
        
        Implements idempotency-aware retry policy:
        - Safe methods (GET, PUT, DELETE): Retry on transient failures
        - Unsafe methods (POST, PATCH): Only retry if idempotency key present or 429
        - 4xx errors (except 429): Never retry to prevent misconfiguration
        
        For POST/PATCH without idempotency keys, only retry errors where server
        never processed the request (429 rate limit). With idempotency key present,
        can safely retry transient failures since key prevents duplicate processing.
        
        Args:
            status_code: HTTP status code
            method: HTTP method
            headers: Request headers to check for idempotency key
        
        Returns:
            True if should retry, False otherwise
        """
        if 400 <= status_code < 500 and status_code != 429:
            return False
        
        if status_code not in self.config.retry_on_status_codes:
            return False
        
        is_safe_method = method.upper() in self.config.safe_methods
        
        if is_safe_method:
            return True
        else:
            headers = headers or {}
            has_idempotency_key = any(
                key.lower() in [h.lower() for h in self.config.idempotency_key_headers]
                for key in headers.keys()
            )
            
            if has_idempotency_key:
                return True
            else:
                return status_code == 429
    
    def _should_retry_exception(self, exception: Exception) -> bool:
        """
        Check if exception should trigger retry.
        
        Only retries TimeoutError (transient network timeout).
        All other exceptions fail fast to avoid masking bugs.
        
        Args:
            exception: Exception instance
        
        Returns:
            True if should retry
        """
        from core.api.models import TimeoutError
        return isinstance(exception, TimeoutError)
    
    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay with optional jitter.
        
        Args:
            attempt: Current attempt number (1-based)
        
        Returns:
            Delay in seconds
        """
        delay = self.config.initial_delay * (self.config.exponential_base ** (attempt - 1))
        delay = min(delay, self.config.max_delay)
        
        if self.config.jitter:
            jitter = delay * random.uniform(0, 0.25)
            delay += jitter
        
        return delay
    
    @property
    def current_attempt(self) -> int:
        """Current attempt number."""
        return self._attempt_count
    
    def reset(self) -> None:
        """Reset attempt counter."""
        self._attempt_count = 0
