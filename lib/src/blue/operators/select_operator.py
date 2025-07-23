###### Formats
from typing import List, Dict, Any, Callable, Union

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer

###############
### Select Operator (Filtering)


def select_operator_function(input_data: List[List[Dict[str, Any]]], params: Dict[str, Any]) -> List[List[Dict[str, Any]]]:
    """Filter records based on a single condition (record-wise filtering)."""
    # Extract parameters
    operand_key = params.get('operand_key')
    operand = params.get('operand')
    operand_val = params.get('operand_val')
    approximate_match = params.get('approximate_match', False)
    eps = params.get('eps', 1e-9)

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


def select_operator_validator(params: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate select operator parameters."""
    try:
        if not default_operator_validator(params, properties):
            return False
    except Exception:
        return False

    # Business logic validation (types already checked by default validator)
    operand = params.get('operand')
    if operand and operand not in ['=', '!=', '>', '>=', '<', '<=']:
        return False

    eps = params.get('eps', 1e-9)
    if eps < 0:
        return False

    return True


def select_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], params: Dict[str, Any]) -> Dict[str, Any]:
    return default_operator_explainer(output, input_data, params)


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
    """

    name = "select"
    description = "Given an input data, filter data elements based on a specified condition by type-aware comparison (record-wise)"
    default_parameters = {
        "operand_key": {"type": "str", "description": "The key to check in each record", "required": True},
        "operand": {"type": "str", "description": "Comparison operator: =, !=, >, >=, <, <=", "required": True},
        "operand_val": {"type": "Any", "description": "Value to compare with", "required": True},
        "approximate_match": {"type": "bool", "description": "Use epsilon tolerance for numeric comparison", "required": False, "default": False},
        "eps": {"type": "float", "description": "Epsilon tolerance for approximate numeric comparison", "required": False, "default": 1e-9},
    }

    def __init__(self, name: str = "select", description: str = None, properties: Dict[str, Any] = None, function: Callable = None, validator: Callable = None, explainer: Callable = None):
        if description is None:
            description = self.description

        if properties is None:
            properties = {}
        if "parameters" not in properties:
            properties["parameters"] = self.default_parameters
        if function is None:
            function = select_operator_function
        if validator is None:
            validator = select_operator_validator
        if explainer is None:
            explainer = select_operator_explainer

        super().__init__(
            name=name,
            description=description,
            properties=properties,
            function=function,
            validator=validator,
            explainer=explainer,
        )


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
    params = {"operand_key": "experience", "operand": ">=", "operand_val": 4}
    result = select_operator_function(input_data, params)
    print("=== SELECT RESULT (experience >= 4) ===")
    print(result)

    ## test salary filtering
    params = {"operand_key": "name", "operand": "!=", "operand_val": "name B"}
    result = select_operator_function(input_data, params)
    print("=== SELECT RESULT (name != name C) ===")
    print(result)
