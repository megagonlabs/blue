###### Formats
from typing import List, Dict, Any, Callable, Optional

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer

###############
### Max Operator
#

def max_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Find the maximum value for a specified key across all records.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]). Uses the first data source.
        attributes: Dictionary containing operator attributes.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        List containing a single record with the max result.
    """
    max_key = attributes.get('max_key')
    output_key = attributes.get('output_key', 'max')

    if not input_data or not input_data[0]:
        return [[{output_key: None}]]

    data = input_data[0]
    
    max_val = None
    
    for record in data:
        value = record.get(max_key)
        if value is not None:
            if isinstance(value, (int, float)):
                val_to_compare = value
            else:
                try:
                    val_to_compare = int(value)
                except (ValueError, TypeError):
                    try:
                        val_to_compare = float(value)
                    except (ValueError, TypeError):
                        # ignore non-numeric values
                        pass
            
            if val_to_compare is not None:
                if max_val is None or val_to_compare > max_val:
                    max_val = val_to_compare

    return [[{output_key: max_val}]]


def max_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate max operator attributes.

    Parameters:
        input_data: List of JSON arrays.
        attributes: Dictionary containing operator attributes.
        properties: Optional properties dictionary.

    Returns:
        True if attributes are valid.
    """
    if not default_operator_validator(input_data, attributes, properties):
        return False
        
    max_key = attributes.get('max_key')
    if not max_key:
        return False
        
    return True


def max_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for max operator."""
    return default_operator_explainer(output, input_data, attributes)


class MaxOperator(Operator):
    """
    Max operator finds the maximum value for a specified key across all records.

    Attributes:
    ----------
    | Name        | Type | Required | Default | Description                                |
    |------------|------|---------|--------|--------------------------------------------|
    | `max_key`    | str  | :fontawesome-solid-circle-check: {.green-check}    | -      | The key to find the max value for          |
    | `output_key` | str  |         | 'max'  | The key name for the result max value      |
    """

    PROPERTIES = {}

    name = "max"
    description = "Given an input data, find the maximum value for a specified key across all records."
    default_attributes = {
        "max_key": {"type": "str", "description": "The key to find the maximum value for", "required": True},
        "output_key": {"type": "str", "description": "The key name for the result max value", "required": False, "default": "max"},
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=max_operator_function,
            description=description or self.description,
            properties=properties,
            validator=max_operator_validator,
            explainer=max_operator_explainer,
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
            {"job_id": 4, "dept": "sales", "salary": 88000},
            {"job_id": 5, "dept": "engineering", "salary": None},
            {"job_id": 6, "dept": "hr", "salary": "70000"},
            {"job_id": 7, "dept": "hr", "salary": "N/A"},
            {"job_id": 8, "dept": "exec", "salary": "120000.5"},
        ]
    ]

    print("=== Input Data ===")
    print(input_data)

    ## Example 1: Basic max
    attributes = {"max_key": "salary"}
    result = max_operator_function(input_data, attributes)
    print("\n=== MAX RESULT (basic) ===")
    print(result)

    ## Example 2: Max with custom output key
    attributes = {"max_key": "salary", "output_key": "max_salary"}
    result = max_operator_function(input_data, attributes)
    print("\n=== MAX RESULT (custom output key) ===")
    print(result)
