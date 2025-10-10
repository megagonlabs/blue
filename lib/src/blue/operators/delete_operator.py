###### Formats
from typing import List, Dict, Any, Callable, Union

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer

###############
### Delete Operator


def delete_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Delete records from the first data source at specified positions.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]), uses the first data source for deletion.
        attributes: Dictionary containing deletion parameters including delete_idx.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        List containing the first data source with records deleted at specified positions.
    """
    # Extract attributes
    delete_idx = attributes.get('delete_idx', [])

    # Validate input
    if not input_data or not input_data[0]:
        return []

    if delete_idx == [] or delete_idx is None:
        return [input_data[0].copy()]

    base_data = input_data[0]
    base_len = len(base_data)

    if base_len == 0:
        return [base_data]

    # Handle single position
    if isinstance(delete_idx, int):
        pos = _normalize_index(delete_idx, base_len)
        if pos is None:
            return [base_data]
        return [base_data[:pos] + base_data[pos + 1 :]]

    # Handle multiple positions
    else:
        return [_delete_multiple_positions(base_data, delete_idx)]


def delete_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate delete operator attributes.

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

    # Business logic validation
    delete_idx = attributes.get('delete_idx', [])

    # delete_idx should be an integer or list of integers
    if isinstance(delete_idx, int):
        pass  # Any integer is valid (including negatives)
    elif isinstance(delete_idx, list):
        for idx in delete_idx:
            if not isinstance(idx, int):
                return False
    else:
        # delete_idx should be int or list, but allow empty list as default
        if delete_idx != [] and delete_idx is not None:
            return False

    return True


def delete_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for delete operator execution.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the operation.
    """
    return default_operator_explainer(output, input_data, attributes)


class DeleteOperator(Operator):
    """
    Delete operator removes records from the first data source at specified positions.
    Supports negative indexing like Python lists (-1 = last, -2 = second to last, etc.).

    Attributes:
    ----------
    | Name       | Type               | Required | Default | Description                                                                                  |
    |------------|------------------|----------|---------|----------------------------------------------------------------------------------------------|
    | `delete_idx` | Union[int, list[int]] |     | []      | Position(s) to delete records. Supports negative indexing (-1 = last, -2 = second to last, etc.) |
    """

    PROPERTIES = {}

    name = "delete"
    description = "Given input data, delete records from the first data source at specified positions"
    default_attributes = {
        "delete_idx": {
            "type": "Union[int, list[int]]",
            "description": "Position(s) to delete records. Supports negative indexing (-1 = last, -2 = second to last, etc.)",
            "required": False,
            "default": [],
        },
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=delete_operator_function,
            description=description or self.description,
            properties=properties,
            validator=delete_operator_validator,
            explainer=default_operator_explainer,
        )

    def _initialize_properties(self):
        super()._initialize_properties()

        # attribute definitions
        self.properties["attributes"] = self.default_attributes


###############
### Helper Functions of Delete Operator


def _normalize_index(idx: int, length: int) -> int:
    """Convert negative index to positive, return None if out of bounds."""
    if idx < 0:
        idx = length + idx
    if idx < 0 or idx >= length:
        return None
    return idx


def _delete_multiple_positions(base_data: List[Dict[str, Any]], delete_indices: List[int]) -> List[Dict[str, Any]]:
    """Delete multiple positions efficiently."""
    base_len = len(base_data)

    # Normalize indices and filter valid ones
    valid_indices = set()
    for idx in delete_indices:
        normalized = _normalize_index(idx, base_len)
        if normalized is not None:
            valid_indices.add(normalized)

    # Build result by skipping deleted positions
    result = []
    for i, record in enumerate(base_data):
        if i not in valid_indices:
            result.append(record)

    return result


if __name__ == "__main__":
    ## calling example

    ## Example 1: delete_idx = -1 (delete last record)
    print("=== Example 1: delete_idx = -1 (delete last) ===")
    input_data = [
        [
            {"id": 1, "name": "A"},
            {"id": 2, "name": "B"},
            {"id": 3, "name": "C"},
        ]
    ]
    attributes = {"delete_idx": -1}
    result = delete_operator_function(input_data, attributes)
    print(result)

    ## Example 2: delete_idx = [1, -1, 0] for data of length 3
    print("=== Example 2: delete_idx = [1, -1, 0] for data of length 3 ===")
    input_data = [
        [
            {"id": 1, "name": "A"},
            {"id": 2, "name": "B"},
            {"id": 3, "name": "C"},
        ]
    ]
    attributes = {"delete_idx": [1, -1, 0]}  # Delete positions 1, 2 (last), and 0 -> delete all
    result = delete_operator_function(input_data, attributes)
    print(result)
