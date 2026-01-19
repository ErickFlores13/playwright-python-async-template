"""Authentication strategies."""

from .api_key import APIKeyAuth
from .basic import BasicAuth
from .bearer_token import BearerTokenAuth
from .composite import CompositeAuth
from .custom_header import CustomHeaderAuth
from .oauth2 import OAuth2ClientCredentialsAuth
from .refreshable_token import RefreshableTokenAuth

__all__ = [
    "BearerTokenAuth",
    "APIKeyAuth",
    "BasicAuth",
    "OAuth2ClientCredentialsAuth",
    "CustomHeaderAuth",
    "CompositeAuth",
    "RefreshableTokenAuth",
]
