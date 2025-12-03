import logging
from dataclasses import dataclass, field
from typing import Callable, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """
    Retry behavior configuration with idempotency-aware policy.

    Safe methods (GET, PUT, DELETE) retry on transient failures.
    Unsafe methods (POST, PATCH) only retry if idempotency key present in headers.
    4xx errors (except 429) never retry to prevent misconfiguration.

    Attributes:
        max_attempts: Maximum retry attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        exponential_base: Exponential backoff base (default: 2)
        jitter: Add random jitter to delays (default: True)
        retry_on_status_codes: Status codes that trigger retry (default: [429, 503])
        safe_methods: Idempotent HTTP methods (default: ['GET', 'HEAD', 'OPTIONS', 'PUT', 'DELETE'])
        idempotency_key_headers: Headers to check for idempotency keys
            (default: ['idempotency-key', 'x-idempotency-key', 'paypal-request-id', 'x-amz-sdk-invocation-id'])
    """

    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: int = 2
    jitter: bool = True
    retry_on_status_codes: List[int] = field(default_factory=lambda: [429, 503])
    safe_methods: List[str] = field(
        default_factory=lambda: ["GET", "HEAD", "OPTIONS", "PUT", "DELETE"]
    )
    idempotency_key_headers: List[str] = field(
        default_factory=lambda: [
            "idempotency-key",
            "x-idempotency-key",
            "paypal-request-id",
            "x-amz-sdk-invocation-id",
        ]
    )

    def __post_init__(self):
        """Validate configuration values."""
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if self.initial_delay <= 0:
            raise ValueError("initial_delay must be positive")
        if self.max_delay < self.initial_delay:
            raise ValueError("max_delay must be >= initial_delay")
        if self.exponential_base < 1:
            raise ValueError("exponential_base must be >= 1")


@dataclass
class TimeoutConfig:
    """
    Request timeout configuration.

    Attributes:
        request_timeout: Maximum request time in seconds (default: 30.0)
        connect_timeout: Maximum connection time in seconds (default: 10.0)
    """

    request_timeout: float = 30.0
    connect_timeout: float = 10.0

    def __post_init__(self):
        """Validate configuration values."""
        if self.request_timeout <= 0:
            raise ValueError("request_timeout must be positive")
        if self.connect_timeout <= 0:
            raise ValueError("connect_timeout must be positive")
        if self.connect_timeout > self.request_timeout:
            raise ValueError("connect_timeout must be <= request_timeout")


@dataclass
class InterceptorConfig:
    """
    Request/response interceptor configuration.

    Attributes:
        enable_logging: Enable request/response logging (default: True)
        enable_metrics: Enable metrics collection (default: False)
        enable_tracing: Enable distributed tracing (default: False)
        add_correlation_header: Add X-Correlation-ID header (default: True)
        custom_request_interceptors: Custom request interceptor functions (default: [])
        custom_response_interceptors: Custom response interceptor functions (default: [])
    """

    enable_logging: bool = True
    enable_metrics: bool = False
    enable_tracing: bool = False
    add_correlation_header: bool = True
    custom_request_interceptors: List[Callable] = field(default_factory=list)
    custom_response_interceptors: List[Callable] = field(default_factory=list)


@dataclass
class HTTPConfig:
    """
    Complete HTTP client configuration.

    Attributes:
        retry: Retry configuration
        timeout: Timeout configuration
        interceptor: Interceptor configuration
        base_headers: Default headers for all requests (default: {})
        verify_ssl: Verify SSL certificates (default: True)
    """

    retry: RetryConfig = field(default_factory=RetryConfig)
    timeout: TimeoutConfig = field(default_factory=TimeoutConfig)
    interceptor: InterceptorConfig = field(default_factory=InterceptorConfig)
    base_headers: dict = field(default_factory=dict)
    verify_ssl: bool = True

    @classmethod
    def from_env(cls) -> "HTTPConfig":
        """
        Load configuration based on HTTP_CONFIG_MODE environment variable.

        Supported modes: standard, external_api, local_api, testing

        Returns:
            HTTPConfig preset based on environment variable
        """
        from utils.config import Config

        mode = Config.get_http_config_mode()

        config_map = {
            "standard": cls.standard,
            "default": cls.standard,
            "external": cls.external_api,
            "external_api": cls.external_api,
            "local": cls.local_api,
            "local_api": cls.local_api,
            "testing": cls.testing,
            "fast": cls.testing,
        }

        config_func = config_map.get(mode)

        if config_func:
            logger.info(f"Loading HTTP config from environment: {mode}")
            return config_func()
        else:
            logger.warning(f"Unknown HTTP_CONFIG_MODE '{mode}', using 'standard'")
            return cls.standard()

    @classmethod
    def standard(cls) -> "HTTPConfig":
        """
        Standard configuration for typical API testing.

        Settings: 3 retries, 30s timeout, balanced settings

        Returns:
            HTTPConfig with standard settings
        """
        return cls()

    @classmethod
    def external_api(cls) -> "HTTPConfig":
        """
        Configuration for external/third-party APIs with poor reliability.

        Settings: 5 retries, 60s timeout, aggressive retry on [429, 502, 503, 504]

        Returns:
            HTTPConfig optimized for unreliable APIs
        """
        return cls(
            retry=RetryConfig(
                max_attempts=5,
                initial_delay=2.0,
                max_delay=120.0,
                retry_on_status_codes=[429, 502, 503, 504],
            ),
            timeout=TimeoutConfig(request_timeout=60.0, connect_timeout=20.0),
        )

    @classmethod
    def local_api(cls) -> "HTTPConfig":
        """
        Configuration for local/internal APIs (localhost, Docker, same network).

        Settings: 1 retry (fail fast), 10s timeout, quick feedback

        Returns:
            HTTPConfig optimized for fast local APIs
        """
        return cls(
            retry=RetryConfig(max_attempts=1, initial_delay=0.5, max_delay=5.0),
            timeout=TimeoutConfig(request_timeout=10.0, connect_timeout=5.0),
        )

    @classmethod
    def testing(cls) -> "HTTPConfig":
        """
        Configuration for fast unit/integration tests.

        Settings: No retries, 5s timeout, minimal logging

        Returns:
            HTTPConfig optimized for test speed
        """
        return cls(
            retry=RetryConfig(max_attempts=1, initial_delay=0.1, max_delay=1.0),
            timeout=TimeoutConfig(request_timeout=5.0, connect_timeout=2.0),
            interceptor=InterceptorConfig(
                enable_logging=False, enable_metrics=False, enable_tracing=False
            ),
        )
