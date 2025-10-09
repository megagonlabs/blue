"""
This utils to used to convert string type representation to actual Python type for Pydantic.
The current implementation depends on manual mapping of string type representation to actual Python type.
"""

from typing import Any, List, Dict, Union, Optional, Type
from collections import deque
from pydantic import BaseModel, ValidationError, create_model
import logging


def string_to_python_type(type_str: str) -> Any:
    """Convert string type representation to actual Python type for Pydantic.

    Parameters:
        type_str: String representation of a Python type (e.g., "List[str]", "Dict[str, int]").

    Returns:
        Actual Python type object that can be used with Pydantic validation.
    """
    if not type_str:
        return Any

    # Normalize type string for Python 3.9+ compatibility
    type_str = (
        type_str.strip().replace('List[', 'list[').replace('Dict[', 'dict[').replace('Tuple[', 'tuple[').replace('Set[', 'set[').replace('FrozenSet[', 'frozenset[').replace('Deque[', 'deque[')
    )
    type_str = type_str.lower()

    # Handle complex types with type hints first
    if type_str.startswith("list["):
        inner_type_str = type_str[5:-1].strip()
        inner_type = string_to_python_type(inner_type_str)
        return List[inner_type]
    elif type_str.startswith("dict["):
        # Parse key and value types: dict[key_type, value_type]
        inner = type_str[5:-1].strip()
        if ',' in inner:
            key_type_str, value_type_str = [s.strip() for s in inner.split(',', 1)]
            key_type = string_to_python_type(key_type_str)
            value_type = string_to_python_type(value_type_str)
            return Dict[key_type, value_type]
        else:
            # Default to Dict[str, Any] if not specified
            return Dict[str, Any]
    elif type_str.startswith("tuple["):
        inner_type_str = type_str[6:-1].strip()
        inner_type = string_to_python_type(inner_type_str)
        return tuple[inner_type]
    elif type_str.startswith("set["):
        inner_type_str = type_str[4:-1].strip()
        inner_type = string_to_python_type(inner_type_str)
        return set[inner_type]
    elif type_str.startswith("frozenset["):
        inner_type_str = type_str[10:-1].strip()
        inner_type = string_to_python_type(inner_type_str)
        return frozenset[inner_type]
    elif type_str.startswith("deque["):
        inner_type_str = type_str[6:-1].strip()
        inner_type = string_to_python_type(inner_type_str)
        return deque[inner_type]
    elif type_str.startswith("union[") or "|" in type_str:
        if type_str.startswith("union["):
            inner_types_str = type_str[6:-1]
            # Parse comma-separated types, respecting nested brackets
            type_names = []
            current = ""
            bracket_count = 0

            for char in inner_types_str:
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                elif char == ',' and bracket_count == 0:
                    type_names.append(current.strip())
                    current = ""
                    continue
                current += char

            if current.strip():
                type_names.append(current.strip())
        else:
            type_names = [t.strip() for t in type_str.split("|")]

        types = [string_to_python_type(t) for t in type_names]
        if type(None) in types:
            non_none_types = [t for t in types if t is not type(None)]
            if len(non_none_types) == 1:
                return Optional[non_none_types[0]]
            else:
                return Union[tuple(non_none_types + [type(None)])]
        return Union[tuple(types)]
    elif type_str.startswith("optional["):
        inner_type_str = type_str[9:-1].strip()
        inner_type = string_to_python_type(inner_type_str)
        return Optional[inner_type]

    # Basic types - only use lowercase/built-in
    type_mapping = {
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "dict": dict,
        "list": list,
        "tuple": tuple,
        "set": set,
        "none": type(None),
        "any": Any,
    }

    # Check simple types
    if type_str in type_mapping:
        return type_mapping[type_str]

    return Any


def create_pydantic_model(parameters: Dict[str, Any]) -> Type[BaseModel]:
    """Create a Pydantic model dynamically from parameter definitions using Pydantic v2.

    Parameters:
        parameters: Dictionary mapping parameter names to their definitions containing 'type' and 'required' keys.

    Returns:
        Dynamically created Pydantic model class for parameter validation.
    """
    fields = {}
    for param_name, param_def in parameters.items():
        param_type = param_def.get("type")
        required = param_def.get("required", False)
        if param_type:
            python_type = string_to_python_type(param_type)
        else:
            python_type = Any

        if required:
            fields[param_name] = (python_type, ...)  # ... means required
        else:
            fields[param_name] = (python_type, None)  # None means optional

    model_class = create_model('ParameterModel', **fields)
    return model_class


def validate_parameter_type(value: Any, expected_type: str) -> bool:
    """Validate that a parameter value matches the expected type using Pydantic v2.

    Parameters:
        value: The value to validate against the expected type.
        expected_type: String representation of the expected Python type.

    Returns:
        True if the value matches the expected type, False otherwise.
    """
    if expected_type is None:
        return True
    try:
        python_type = string_to_python_type(expected_type)
        SingleFieldModel = create_model('SingleFieldModel', value=(python_type, ...))
        SingleFieldModel(value=value)
        return True
    except ValidationError:
        # Validation failure: value doesn't match expected type
        return False
    except (TypeError, ValueError, AttributeError) as e:
        # Validation failure: invalid type specification or conversion issue
        logging.warning(f"Invalid type specification '{expected_type}': {e}")
        return False
    except Exception as e:
        # System failure: something is wrong with the validation system itself, how to handle this depends on the use case
        logging.error(f"System error during parameter type validation: {e}")
        raise RuntimeError(f"Parameter type validation system error: {e}") from e
