import logging
from typing import Any, Dict, Optional, Type, TypeVar, Union, List
from pydantic import BaseModel, ValidationError as PydanticValidationError
from core.api.models import ValidationError, APIResponseWrapper

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class ValidationService:
    """
    Service for validating API responses.
    
    Provides methods for:
    - Schema validation using Pydantic models
    - Status code assertions
    - JSON path assertions
    - Required field checks
    
    Example:
        >>> from pydantic import BaseModel
        >>> 
        >>> class User(BaseModel):
        ...     id: int
        ...     name: str
        ...     email: str
        >>> 
        >>> validator = ValidationService()
        >>> user = validator.validate_schema(response.data, User)
        >>> print(user.name)
    """
    
    def __init__(self):
        pass
    
    def validate_schema(
        self,
        data: Any,
        model: Type[T]
    ) -> T:
        """
        Validate data against Pydantic schema.
        
        Args:
            data: Data to validate (usually dict)
            model: Pydantic model class
        
        Returns:
            Validated and typed model instance
        
        Raises:
            ValidationError: If validation fails
        
        Example:
            >>> class CreateUserResponse(BaseModel):
            ...     id: int
            ...     name: str
            ...     email: str
            ...     created_at: str
            >>> 
            >>> user = validator.validate_schema(response.data, CreateUserResponse)
            >>> assert isinstance(user, CreateUserResponse)
            >>> print(user.id)  # Type-safe access
        """
        try:
            validated = model(**data) if isinstance(data, dict) else model.parse_obj(data)
            logger.debug(f"Schema validation successful for {model.__name__}")
            return validated
            
        except PydanticValidationError as e:
            error_msg = f"Schema validation failed for {model.__name__}: {str(e)}"
            logger.error(error_msg)
            raise ValidationError(
                message=error_msg,
                response_body=data
            ) from e
    
    def validate_status_code(
        self,
        response: APIResponseWrapper,
        expected: Union[int, List[int]]
    ) -> None:
        """
        Validate response status code.
        
        Args:
            response: API response wrapper
            expected: Expected status code(s)
        
        Raises:
            ValidationError: If status code doesn't match
        
        Example:
            >>> validator.validate_status_code(response, 200)
            >>> # or multiple acceptable codes
            >>> validator.validate_status_code(response, [200, 201])
        """
        expected_codes = [expected] if isinstance(expected, int) else expected
        
        if response.status_code not in expected_codes:
            error_msg = (
                f"Expected status code {expected_codes} but got {response.status_code}"
            )
            logger.error(error_msg)
            raise ValidationError(
                message=error_msg,
                status_code=response.status_code,
                response_body=response.data
            )
        
        logger.debug(f"Status code validation successful: {response.status_code}")
    
    def validate_required_fields(
        self,
        data: Dict[str, Any],
        required_fields: List[str]
    ) -> None:
        """
        Validate that required fields exist in response data.
        
        Args:
            data: Response data (dict)
            required_fields: List of required field names
        
        Raises:
            ValidationError: If any required field is missing
        
        Example:
            >>> validator.validate_required_fields(
            ...     response.data,
            ...     ['id', 'name', 'email']
            ... )
        """
        missing_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            logger.error(error_msg)
            raise ValidationError(
                message=error_msg,
                response_body=data
            )
        
        logger.debug(f"Required fields validation successful: {required_fields}")
    
    def validate_json_path(
        self,
        data: Any,
        path: str,
        expected_value: Optional[Any] = None
    ) -> Any:
        """
        Validate value at JSON path.
        
        Args:
            data: Response data
            path: Dot-notation path (e.g., 'user.address.city')
            expected_value: Optional expected value
        
        Returns:
            Value at path
        
        Raises:
            ValidationError: If path doesn't exist or value doesn't match
        
        Example:
            >>> # Check if path exists
            >>> city = validator.validate_json_path(response.data, 'user.address.city')
            >>> 
            >>> # Check specific value
            >>> validator.validate_json_path(
            ...     response.data,
            ...     'user.status',
            ...     expected_value='active'
            ... )
        """
        try:
            # Navigate path
            keys = path.split('.')
            value = data
            
            for key in keys:
                if isinstance(value, dict):
                    value = value[key]
                elif isinstance(value, list):
                    # Handle array index like 'items[0]'
                    if '[' in key and ']' in key:
                        field = key[:key.index('[')]
                        index = int(key[key.index('[') + 1:key.index(']')])
                        value = value[index] if field == '' else value[field][index]
                    else:
                        raise KeyError(f"Cannot access {key} on list")
                else:
                    raise KeyError(f"Cannot access {key} on {type(value)}")
            
            # Validate expected value if provided
            if expected_value is not None and value != expected_value:
                error_msg = (
                    f"Value at path '{path}' is '{value}' but expected '{expected_value}'"
                )
                logger.error(error_msg)
                raise ValidationError(
                    message=error_msg,
                    response_body=data
                )
            
            logger.debug(f"JSON path validation successful: {path} = {value}")
            return value
            
        except (KeyError, IndexError, TypeError) as e:
            error_msg = f"Invalid JSON path '{path}': {str(e)}"
            logger.error(error_msg)
            raise ValidationError(
                message=error_msg,
                response_body=data
            ) from e
    
    def validate_response_type(
        self,
        data: Any,
        expected_type: type
    ) -> None:
        """
        Validate response data type.
        
        Args:
            data: Response data
            expected_type: Expected Python type
        
        Raises:
            ValidationError: If type doesn't match
        
        Example:
            >>> # Expect list response
            >>> validator.validate_response_type(response.data, list)
            >>> 
            >>> # Expect dict response
            >>> validator.validate_response_type(response.data, dict)
        """
        if not isinstance(data, expected_type):
            error_msg = (
                f"Expected response type {expected_type.__name__} "
                f"but got {type(data).__name__}"
            )
            logger.error(error_msg)
            raise ValidationError(
                message=error_msg,
                response_body=data
            )
        
        logger.debug(f"Response type validation successful: {expected_type.__name__}")
    
    def validate_list_length(
        self,
        data: List[Any],
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        exact_length: Optional[int] = None
    ) -> None:
        """
        Validate list length constraints.
        
        Args:
            data: List data
            min_length: Minimum acceptable length
            max_length: Maximum acceptable length
            exact_length: Exact required length
        
        Raises:
            ValidationError: If length constraints not met
        
        Example:
            >>> # At least 1 item
            >>> validator.validate_list_length(response.data, min_length=1)
            >>> 
            >>> # Between 1 and 10 items
            >>> validator.validate_list_length(response.data, min_length=1, max_length=10)
            >>> 
            >>> # Exactly 5 items
            >>> validator.validate_list_length(response.data, exact_length=5)
        """
        if not isinstance(data, list):
            error_msg = f"Expected list but got {type(data).__name__}"
            logger.error(error_msg)
            raise ValidationError(message=error_msg, response_body=data)
        
        length = len(data)
        
        if exact_length is not None:
            if length != exact_length:
                error_msg = f"Expected list length {exact_length} but got {length}"
                logger.error(error_msg)
                raise ValidationError(message=error_msg, response_body=data)
        else:
            if min_length is not None and length < min_length:
                error_msg = f"List length {length} is less than minimum {min_length}"
                logger.error(error_msg)
                raise ValidationError(message=error_msg, response_body=data)
            
            if max_length is not None and length > max_length:
                error_msg = f"List length {length} exceeds maximum {max_length}"
                logger.error(error_msg)
                raise ValidationError(message=error_msg, response_body=data)
        
        logger.debug(f"List length validation successful: {length}")
