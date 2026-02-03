###### Formats
from typing import List, Dict, Any, Callable, Optional

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer

###############
### Sum Operator
#

def sum_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Calculate the sum of values for a specified key across all records.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]). Uses the first data source.
        attributes: Dictionary containing operator attributes.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        List containing a single record with the sum result.
    """
    sum_key = attributes.get('sum_key')
    output_key = attributes.get('output_key', 'sum')

    if not input_data or not input_data[0]:
        return [[{output_key: 0}]]

    data = input_data[0]
    
    # Calculate sum skipping None values
    total_sum = 0
    for record in data:
        value = record.get(sum_key)
        if value is not None:
            if isinstance(value, (int, float)):
                total_sum += value
            else:
                try:
                    total_sum += int(value)
                except (ValueError, TypeError):
                    try:
                        total_sum += float(value)
                    except (ValueError, TypeError):
                        # ignore non-numeric values
                        pass
                
    return [[{output_key: total_sum}]]


def sum_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate sum operator attributes.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) to validate.
        attributes: Dictionary containing operator attributes to validate.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        True if attributes are valid, False otherwise.
    """
    if not default_operator_validator(input_data, attributes, properties):
        return False
        
    sum_key = attributes.get('sum_key')
    if not sum_key:
        return False
        
    return True


def sum_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for sum operator execution.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the operation.
    """
    return default_operator_explainer(output, input_data, attributes)


class SumOperator(Operator):
    """
    Sum operator calculates the sum of values for a specified key across all records.

    Attributes:
    ----------
    | Name        | Type | Required | Default | Description                                |
    |------------|------|---------|--------|--------------------------------------------|
    | `sum_key`    | str  | :fontawesome-solid-circle-check: {.green-check}    | -      | The key to sum the values for              |
    | `output_key` | str  |         | 'sum'  | The key name for the result sum            |
    """

    PROPERTIES = {}

    name = "sum"
    description = "Given an input data, calculate the sum of values for a specified key across all records."
    default_attributes = {
        "sum_key": {"type": "str", "description": "The key to sum the values for", "required": True},
        "output_key": {"type": "str", "description": "The key name for the result sum", "required": False, "default": "sum"},
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=sum_operator_function,
            description=description or self.description,
            properties=properties,
            validator=sum_operator_validator,
            explainer=sum_operator_explainer,
        )

    def _initialize_properties(self):
        super()._initialize_properties()
        self.properties["attributes"] = self.default_attributes


if __name__ == "__main__":
    ## calling example
    input_data = [
        [
            {"job_id": 1, "dept": "engineering", "salary": 80000},
            {"job_id": 2, "dept": "sales", "salary": 95000},
            {"job_id": 3, "dept": "engineering", "salary": 75000},
            {"job_id": 4, "dept": "sales", "salary": "88000"},
            {"job_id": 5, "dept": "engineering", "salary": None},
        ]
    ]

    print("=== Input Data ===")
    print(input_data)

    ## Example 1: Basic sum
    attributes = {"sum_key": "salary"}
    result = sum_operator_function(input_data, attributes)
    print("\n=== SUM RESULT (basic) ===")
    print(result)

    ## Example 2: Sum with custom output key
    attributes = {"sum_key": "salary", "output_key": "total_salary"}
    result = sum_operator_function(input_data, attributes)
    print("\n=== SUM RESULT (custom output key) ===")
    print(result)
