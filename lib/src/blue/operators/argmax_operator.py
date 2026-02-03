###### Formats
from typing import List, Dict, Any, Callable, Optional

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer

###############
### Argmax Operator
#

def argmax_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Find the record(s) that contain the maximum value for a specified key.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]). Uses the first data source.
        attributes: Dictionary containing operator attributes.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        List of record(s) with the max value (or single record with indices list if return_index is True).
    """
    argmax_key = attributes.get('argmax_key')
    return_index = attributes.get('return_index', False)

    if not input_data or not input_data[0]:
        if return_index:
            return [[{'indices': []}]]
        return [[]]

    data = input_data[0]
    
    max_val = None
    max_records_indices = []

    for i, record in enumerate(data):
        value = record.get(argmax_key)
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
                if max_val is None or val_to_compare > max_val:
                    max_val = val_to_compare
                    max_records_indices = [(i, record)]
                elif val_to_compare == max_val:
                    max_records_indices.append((i, record))

    if return_index:
        indices = [idx for idx, _ in max_records_indices]
        return [[{'indices': indices}]]
    else:
        records = [rec for _, rec in max_records_indices]
        return [records]


def argmax_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate argmax operator attributes.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) to validate.
        attributes: Dictionary containing operator attributes to validate.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        True if attributes are valid, False otherwise.
    """
    if not default_operator_validator(input_data, attributes, properties):
        return False
        
    argmax_key = attributes.get('argmax_key')
    if not argmax_key:
        return False
        
    return True


def argmax_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for argmax operator execution.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the operation.
    """
    return default_operator_explainer(output, input_data, attributes)


class ArgmaxOperator(Operator):
    """
    Argmax operator finds the record(s) that contain the maximum value for a specified key.

    Attributes:
    ----------
    | Name        | Type | Required | Default | Description                                |
    |------------|------|---------|--------|--------------------------------------------|
    | `argmax_key` | str  | :fontawesome-solid-circle-check: {.green-check}    | -      | The key to find the max value for          |
    | `return_index`| bool |         | False  | If True, returns indices (0-based) instead of records, otherwise returns records|
    """

    PROPERTIES = {}

    name = "argmax"
    description = "Given an input data, find the record(s) that contain the maximum value for a specified key."
    default_attributes = {
        "argmax_key": {"type": "str", "description": "The key to find the maximum value for", "required": True},
        "return_index": {"type": "bool", "description": "If True, returns indices (0-based) instead of records, otherwise returns records", "required": False, "default": False},
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=argmax_operator_function,
            description=description or self.description,
            properties=properties,
            validator=argmax_operator_validator,
            explainer=argmax_operator_explainer,
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
            {"job_id": 4, "dept": "sales", "salary": "95000.0"},
            {"job_id": 5, "dept": "engineering", "salary": None},
            {"job_id": 6, "dept": "hr", "salary": "70000"},
            {"job_id": 7, "dept": "hr", "salary": "N/A"},
        ]
    ]

    print("=== Input Data ===")
    print(input_data)

    ## Example 1: Basic argmax (Records)
    attributes = {"argmax_key": "salary"}
    result = argmax_operator_function(input_data, attributes)
    print("\n=== ARGMAX RESULT (records) ===")
    print(result)

    ## Example 2: Return Indices
    attributes = {"argmax_key": "salary", "return_index": True}
    result = argmax_operator_function(input_data, attributes)
    print("\n=== ARGMAX RESULT (indices) ===")
    print(result)
    
