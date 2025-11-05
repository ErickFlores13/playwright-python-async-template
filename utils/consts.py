from enum import Enum

class FilterType(Enum):
    """Enumeration for different filter types used in filtering."""
    INVALID = "invalid"
    EMPTY = "empty"
    CLEAR = "clear"

class ValidationType(Enum):
    """Enumeration for different edit types used in editing operations."""
    REQUIRED = "required"
    PATTERN = "pattern"
    MAX_LENGTH = "max_length"
    MIN_LENGTH = "min_length"
    DATA_TYPE = "data_type"
    MAX = "max"
    MIN = "min"
    NEGATIVE = "negative"
    CUSTOM = "custom"
    DISABLED = "disabled"

class ButtonOperations(Enum):
    """Enumeration for different cancel/back button operations"""
    CANCEL_CREATE = "cancel_create"
    CANCEL_EDIT = "cancel_edit" 
    CANCEL_DELETE = "cancel_delete"
    CANCEL_ENABLE = "cancel_enable"
    BACK_CREATE = "back_create"
    BACK_EDIT = "back_edit"
    BACK_DETAIL = "back_detail"
    BACK_DISABLED = "back_disabled"
    BACK_DETAIL_DISABLED = "back_detail_disabled"
    BACK_COPY = "back_copy"
    CANCEL_COPY = "back_copy"