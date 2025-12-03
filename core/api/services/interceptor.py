import logging
import time
import uuid
import asyncio
from typing import Dict, Any, Optional, Callable
from core.api.config import InterceptorConfig
from core.api.models import APIResponseWrapper

logger = logging.getLogger(__name__)


class InterceptorService:
    """
    Service for intercepting and modifying requests/responses.
    
    Provides hooks for:
    - Request logging and modification
    - Response logging and transformation
    - Metrics collection
    - Distributed tracing
    - Custom interceptors
    """
    
    def __init__(self, config: InterceptorConfig):
        """
        Initialize interceptor service.
        
        Args:
            config: Interceptor configuration
        """
        self.config = config
        self._request_metrics: Dict[str, Dict[str, Any]] = {}
    
    async def before_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Intercept and modify request before sending.
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers (mutable)
            params: Query parameters
            data: Request body
        
        Returns:
            Request context dict with timing and correlation info
        
        Example:
            >>> context = await interceptor.before_request(
            ...     method='POST',
            ...     url='/users',
            ...     headers={'Content-Type': 'application/json'},
            ...     data={'name': 'John'}
            ... )
        """
        # Generate correlation ID for request tracking
        correlation_id = str(uuid.uuid4())
        
        # Create request context
        context = {
            'correlation_id': correlation_id,
            'method': method,
            'url': url,
            'start_time': time.time(),
            'headers': headers or {},
            'params': params,
            'data': data
        }
        
        # Add correlation ID to headers
        if self.config.add_correlation_header and headers is not None:
            headers['X-Correlation-ID'] = correlation_id
        
        # Logging interceptor
        if self.config.enable_logging:
            self._log_request(context)
        
        # Tracing interceptor
        if self.config.enable_tracing:
            self._add_tracing_headers(headers or {})
        
        # Custom request interceptors
        for interceptor in self.config.custom_request_interceptors:
            try:
                context = await self._run_interceptor(interceptor, context)
            except Exception as e:
                logger.warning(f"Custom request interceptor failed: {e}")
        
        # Store for metrics
        if self.config.enable_metrics:
            self._request_metrics[correlation_id] = context
        
        return context
    
    async def after_response(
        self,
        response: APIResponseWrapper,
        request_context: Dict[str, Any]
    ) -> APIResponseWrapper:
        """
        Intercept and process response after receiving.
        
        Args:
            response: API response wrapper
            request_context: Request context from before_request
        
        Returns:
            Processed response (potentially modified)
        
        Example:
            >>> response = await interceptor.after_response(response, request_context)
        """
        # Calculate elapsed time
        elapsed = time.time() - request_context['start_time']
        response.elapsed_ms = elapsed * 1000  # Convert to milliseconds
        
        # Logging interceptor
        if self.config.enable_logging:
            self._log_response(response, request_context)
        
        # Metrics interceptor
        if self.config.enable_metrics:
            self._record_metrics(response, request_context)
        
        # Custom response interceptors
        for interceptor in self.config.custom_response_interceptors:
            try:
                response = await self._run_interceptor(interceptor, response, request_context)
            except Exception as e:
                logger.warning(f"Custom response interceptor failed: {e}")
        
        # Clean up metrics storage
        correlation_id = request_context.get('correlation_id')
        if correlation_id in self._request_metrics:
            del self._request_metrics[correlation_id]
        
        return response
    
    def _log_request(self, context: Dict[str, Any]) -> None:
        """
        Log request details.
        
        Args:
            context: Request context
        """
        method = context['method']
        url = context['url']
        correlation_id = context['correlation_id']
        
        log_msg = f"[{correlation_id}] → {method} {url}"
        
        # Add query params if present
        if context.get('params'):
            log_msg += f" params={context['params']}"
        
        # Add body for POST/PUT/PATCH
        if context.get('data') and method in ['POST', 'PUT', 'PATCH']:
            # Truncate large bodies
            data_str = str(context['data'])
            if len(data_str) > 200:
                data_str = data_str[:200] + "..."
            log_msg += f" body={data_str}"
        
        logger.info(log_msg)
    
    def _log_response(
        self,
        response: APIResponseWrapper,
        context: Dict[str, Any]
    ) -> None:
        """
        Log response details.
        
        Args:
            response: API response
            context: Request context
        """
        correlation_id = context['correlation_id']
        method = context['method']
        url = context['url']
        
        log_msg = (
            f"[{correlation_id}] ← {method} {url} "
            f"status={response.status_code} "
            f"elapsed={response.elapsed_ms:.2f}ms"
        )
        
        # Use different log levels based on status
        if response.is_success:
            logger.info(log_msg)
        elif response.is_client_error:
            logger.warning(f"{log_msg} response={response.data}")
        else:
            logger.error(f"{log_msg} response={response.data}")
    
    def _add_tracing_headers(self, headers: Dict[str, str]) -> None:
        """
        Add distributed tracing headers.
        
        Args:
            headers: Request headers to modify
        """
        # Add trace ID and span ID (simplified OpenTelemetry style)
        if 'X-Trace-ID' not in headers:
            headers['X-Trace-ID'] = str(uuid.uuid4())
        if 'X-Span-ID' not in headers:
            headers['X-Span-ID'] = str(uuid.uuid4())
    
    def _record_metrics(
        self,
        response: APIResponseWrapper,
        context: Dict[str, Any]
    ) -> None:
        """
        Record metrics for request/response.
        
        Args:
            response: API response
            context: Request context
        """
        metrics = {
            'method': context['method'],
            'url': context['url'],
            'status_code': response.status_code,
            'elapsed_ms': response.elapsed_ms,
            'success': response.is_success,
            'timestamp': time.time()
        }
        
        logger.debug(f"Metrics: {metrics}")
    
    async def _run_interceptor(
        self,
        interceptor: Callable,
        *args
    ) -> Any:
        """
        Run custom interceptor function.
        
        Args:
            interceptor: Interceptor function
            *args: Arguments for interceptor
        
        Returns:
            Result from interceptor
        """
        if asyncio.iscoroutinefunction(interceptor):
            return await interceptor(*args)
        else:
            return interceptor(*args)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get summary of collected metrics.
        
        Returns:
            Dict with metrics summary
        
        Example:
            >>> summary = interceptor.get_metrics_summary()
            >>> print(summary['total_requests'])
        """
        return {
            'active_requests': len(self._request_metrics),
            'request_ids': list(self._request_metrics.keys())
        }