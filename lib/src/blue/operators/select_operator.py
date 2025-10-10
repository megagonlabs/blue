###### Formats
from typing import List, Dict, Any, Callable, Union

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer

###############
### Select Operator (Filtering)


def select_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Filter records based on a single condition (record-wise filtering).

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]), uses the first data source for filtering.
        attributes: Dictionary containing filtering parameters including operand_key, operand, operand_val, approximate_match, and eps.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        List containing filtered records from the first data source.
    """
    # Extract attributes
    operand_key = attributes.get('operand_key')
    operand = attributes.get('operand')
    operand_val = attributes.get('operand_val')
    approximate_match = attributes.get('approximate_match', False)
    eps = attributes.get('eps', 1e-9)

    # Validate input
    if not input_data or not input_data[0]:
        return []

    data = input_data[0]  # Use first data source

    # Filter records based on condition
    result = []
    for record in data:
        if operand_key not in record:
            continue
        record_value = record[operand_key]
        if _evaluate_condition(record_value, operand, operand_val, approximate_match, eps):
            result.append(record)
    return [result]


def select_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate select operator attributes.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) to validate.
        attributes: Dictionary containing operator attributes to validate.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        True if attributes are valid, False otherwise.
    """
    try:
        if not default_operator_validator(input_data, attributes, properties):
            return False
    except Exception:
        return False

    # Business logic validation (types already checked by default validator)
    operand = attributes.get('operand')
    if operand and operand not in ['=', '!=', '>', '>=', '<', '<=']:
        return False

    eps = attributes.get('eps', 1e-9)
    if eps < 0:
        return False

    return True


def select_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for select operator execution.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the operation.
    """
    return default_operator_explainer(output, input_data, attributes)


def _evaluate_condition(record_value: Any, operand: str, operand_val: Any, approximate_match: bool, eps: float) -> bool:
    """Evaluate a single condition based on type-aware comparison rules."""
    # Type-aware comparison logic
    record_is_numeric = isinstance(record_value, (int, float))
    operand_is_numeric = isinstance(operand_val, (int, float))

    # If both are numeric, convert to float and compare
    if record_is_numeric and operand_is_numeric:
        record_float = float(record_value)
        operand_float = float(operand_val)

        if operand == '=':
            if approximate_match:
                return abs(record_float - operand_float) <= eps
            else:
                return record_float == operand_float
        elif operand == '!=':
            if approximate_match:
                return abs(record_float - operand_float) > eps
            else:
                return record_float != operand_float
        elif operand == '>':
            return record_float > operand_float
        elif operand == '>=':
            return record_float >= operand_float
        elif operand == '<':
            return record_float < operand_float
        elif operand == '<=':
            return record_float <= operand_float

    # If one is numeric and one is string, doesn't match (except for != which should return True)
    elif record_is_numeric != operand_is_numeric:
        return operand == '!='

    # If both are strings, compare as strings
    elif isinstance(record_value, str) and isinstance(operand_val, str):
        if operand == '=':
            return record_value == operand_val
        elif operand == '!=':
            return record_value != operand_val
        elif operand == '>':
            return record_value > operand_val
        elif operand == '>=':
            return record_value >= operand_val
        elif operand == '<':
            return record_value < operand_val
        elif operand == '<=':
            return record_value <= operand_val

    # For other types, only support equality checks
    else:
        if operand == '=':
            return record_value == operand_val
        elif operand == '!=':
            return record_value != operand_val
        else:
            # Cannot perform ordering operations on non-numeric, non-string types
            return False

    return False


class SelectOperator(Operator):
    """
    Select operator filters records based on a single condition (record-wise filtering).
    Supports basic comparison operators with type-aware comparison logic.

    Attributes:
    ----------
    | Name               | Type  | Required | Default | Description                                           |
    |-------------------|-------|---------|--------|-------------------------------------------------------|
    | `operand_key`        | str   | :fontawesome-solid-circle-check: {.green-check}    | -      | The key to check in each record                       |
    | `operand`            | str   | :fontawesome-solid-circle-check: {.green-check}    | -      | Comparison operator: =, !=, >, >=, <, <=             |
    | `operand_val`        | Any   | :fontawesome-solid-circle-check: {.green-check}    | -      | Value to compare with                                  |
    | `approximate_match`  | bool  |    | False  | Use epsilon tolerance for numeric comparison          |
    | `eps`                | float |    | 1e-9   | Epsilon tolerance for approximate numeric comparison  |

    """

    PROPERTIES = {}

    name = "select"
    description = "Given an input data, filter data elements based on a specified condition by type-aware comparison (record-wise)"
    default_attributes = {
        "operand_key": {"type": "str", "description": "The key to check in each record", "required": True},
        "operand": {"type": "str", "description": "Comparison operator: =, !=, >, >=, <, <=", "required": True},
        "operand_val": {"type": "Any", "description": "Value to compare with", "required": True},
        "approximate_match": {"type": "bool", "description": "Use epsilon tolerance for numeric comparison", "required": False, "default": False},
        "eps": {"type": "float", "description": "Epsilon tolerance for approximate numeric comparison", "required": False, "default": 1e-9},
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=select_operator_function,
            description=description or self.description,
            properties=properties,
            validator=select_operator_validator,
            explainer=select_operator_explainer,
        )

    def _initialize_properties(self):
        super()._initialize_properties()

        # attribute definitions
        self.properties["attributes"] = self.default_attributes


if __name__ == "__main__":
    ## calling example

    input_data = [
        [
            {"job_id": 1, "name": "name A", "salary": 80000, "experience": 3},
            {"job_id": 2, "name": "name B", "salary": 95000, "experience": 5},
            {"job_id": 3, "name": "name C", "salary": 75000, "experience": 4},
        ]
    ]

    ## test numeric filtering
    attributes = {"operand_key": "experience", "operand": ">=", "operand_val": 4}
    result = select_operator_function(input_data, attributes)
    print("=== SELECT RESULT (experience >= 4) ===")
    print(result)

    ## test salary filtering
    attributes = {"operand_key": "name", "operand": "!=", "operand_val": "name B"}
    result = select_operator_function(input_data, attributes)
    print("=== SELECT RESULT (name != name C) ===")
    print(result)
