###### Formats
from typing import List, Dict, Any, Callable, Optional

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer

###############
### Average Operator
#

def avg_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Calculate the average (arithmetic mean) of values for a specified key across all records.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]). Uses the first data source.
        attributes: Dictionary containing operator attributes.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        List containing a single record with the average result.
    """
    avg_key = attributes.get('avg_key')
    output_key = attributes.get('output_key', 'avg')

    if not input_data or not input_data[0]:
        return [[{output_key: 0}]]

    data = input_data[0]
    
    total_sum = 0
    count = 0
    
    for record in data:
        value = record.get(avg_key)
        if value is not None:
            if isinstance(value, (int, float)):
                 val_to_add = value
                 total_sum += val_to_add
                 count += 1
            else:
                try:
                    val_to_add = int(value)
                    total_sum += val_to_add
                    count += 1
                except (ValueError, TypeError):
                    try:
                        val_to_add = float(value)
                        total_sum += val_to_add
                        count += 1
                    except (ValueError, TypeError):
                        # ignore non-numeric values
                        pass
                
    average = total_sum / count if count > 0 else 0
    return [[{output_key: average}]]


def avg_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate average operator attributes.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) to validate.
        attributes: Dictionary containing operator attributes to validate.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        True if attributes are valid, False otherwise.
    """
    if not default_operator_validator(input_data, attributes, properties):
        return False
        
    avg_key = attributes.get('avg_key')
    if not avg_key:
        return False
        
    return True


def avg_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for average operator execution.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the operation.
    """
    return default_operator_explainer(output, input_data, attributes)


class AvgOperator(Operator):
    """
    Average operator calculates the average (arithmetic mean) of values for a specified key across all records.

    Attributes:
    ----------
    | Name        | Type | Required | Default | Description                                |
    |------------|------|---------|--------|--------------------------------------------|
    | `avg_key`    | str  | :fontawesome-solid-circle-check: {.green-check}    | -      | The key to average the values for          |
    | `output_key` | str  |         | 'avg'  | The key name for the result average        |
    """

    PROPERTIES = {}

    name = "avg"
    description = "Given an input data, calculate the average (arithmetic mean) of values for a specified key across all records."
    default_attributes = {
        "avg_key": {"type": "str", "description": "The key to average the values for", "required": True},
        "output_key": {"type": "str", "description": "The key name for the result average", "required": False, "default": "avg"},
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=avg_operator_function,
            description=description or self.description,
            properties=properties,
            validator=avg_operator_validator,
            explainer=avg_operator_explainer,
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
        ]
    ]

    print("=== Input Data ===")
    print(input_data)

    ## Example 1: Basic average
    attributes = {"avg_key": "salary"}
    result = avg_operator_function(input_data, attributes)
    print("\n=== AVG RESULT (basic) ===")
    print(result)

    ## Example 2: Average with custom output key
    attributes = {"avg_key": "salary", "output_key": "mean_salary"}
    result = avg_operator_function(input_data, attributes)
    print("\n=== AVG RESULT (custom output key) ===")
    print(result)
