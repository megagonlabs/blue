###### Formats
from typing import List, Dict, Any, Callable, Optional

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer

###############
### Min Operator
#

def min_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Find the minimum value for a specified key across all records.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]). Uses the first data source.
        attributes: Dictionary containing operator attributes.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        List containing a single record with the min result.
    """
    min_key = attributes.get('min_key')
    output_key = attributes.get('output_key', 'min')

    if not input_data or not input_data[0]:
        return [[{output_key: None}]]

    data = input_data[0]
    
    min_val = None
    
    for record in data:
        value = record.get(min_key)
        if value is not None:
            val_to_compare = None
            
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
                if min_val is None or val_to_compare < min_val:
                    min_val = val_to_compare

    return [[{output_key: min_val}]]


def min_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate min operator attributes.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) to validate.
        attributes: Dictionary containing operator attributes to validate.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        True if attributes are valid, False otherwise.
    """
    if not default_operator_validator(input_data, attributes, properties):
        return False
        
    min_key = attributes.get('min_key')
    if not min_key:
        return False
        
    return True


def min_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for min operator execution.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the operation.
    """
    return default_operator_explainer(output, input_data, attributes)


class MinOperator(Operator):
    """
    Min operator finds the minimum value for a specified key across all records.

    Attributes:
    ----------
    | Name        | Type | Required | Default | Description                                |
    |------------|------|---------|--------|--------------------------------------------|
    | `min_key`    | str  | :fontawesome-solid-circle-check: {.green-check}    | -      | The key to find the min value for          |
    | `output_key` | str  |         | 'min'  | The key name for the result min value      |
    """

    PROPERTIES = {}

    name = "min"
    description = "Given an input data, find the minimum value for a specified key across all records."
    default_attributes = {
        "min_key": {"type": "str", "description": "The key to find the minimum value for", "required": True},
        "output_key": {"type": "str", "description": "The key name for the result min value", "required": False, "default": "min"},
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=min_operator_function,
            description=description or self.description,
            properties=properties,
            validator=min_operator_validator,
            explainer=min_operator_explainer,
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
            {"job_id": 3, "dept": "engineering", "salary": 75000.5},
            {"job_id": 4, "dept": "sales", "salary": 88000},
            {"job_id": 5, "dept": "engineering", "salary": None},
            {"job_id": 6, "dept": "hr", "salary": "70000"},
            {"job_id": 7, "dept": "hr", "salary": "N/A"},
        ]
    ]

    print("=== Input Data ===")
    print(input_data)

    ## Example 1: Basic min
    attributes = {"min_key": "salary"}
    result = min_operator_function(input_data, attributes)
    print("\n=== MIN RESULT (basic) ===")
    print(result)

    ## Example 2: Min with custom output key
    attributes = {"min_key": "salary", "output_key": "min_salary"}
    result = min_operator_function(input_data, attributes)
    print("\n=== MIN RESULT (custom output key) ===")
    print(result)
