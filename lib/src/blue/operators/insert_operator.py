###### Formats
from typing import List, Dict, Any, Callable, Union

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer

###############
### Insert Operator


def insert_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Insert records into the first data source at specified positions.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]), uses first data source as base and optionally second data source for records to insert.
        attributes: Dictionary containing insert parameters including insert_records and insert_idx.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        List containing the first data source with records inserted at specified positions.
    """
    insert_idx = attributes.get('insert_idx', -1)
    if not input_data or not input_data[0]:
        return []

    # Get insert_records from second data group or attributes
    if len(input_data) >= 2 and input_data[1]:
        insert_records = input_data[1]
    else:
        insert_records = attributes.get('insert_records', [])

    if not insert_records:
        return [input_data[0].copy()]

    base_data = input_data[0]
    base_len = len(base_data)

    # Handle single position
    if isinstance(insert_idx, int):
        pos = insert_idx
        if pos < 0 or pos > base_len:
            return [base_data + insert_records]
        else:
            return [base_data[:pos] + insert_records + base_data[pos:]]

    # Handle multiple positions
    else:
        insert_positions = insert_idx.copy()
        while len(insert_positions) < len(insert_records):
            insert_positions.append(-1)

        return [_build_result_with_multiple_inserts(base_data, insert_records, insert_positions)]


def insert_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate insert operator attributes.

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
    insert_idx = attributes.get('insert_idx', -1)

    # Validate insert_idx values are not less than -1
    if isinstance(insert_idx, int):
        if insert_idx < -1:
            return False
    elif isinstance(insert_idx, list):
        for idx in insert_idx:
            if idx < -1:
                return False

    return True


def insert_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for insert operator execution.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the operation.
    """
    return default_operator_explainer(output, input_data, attributes)


class InsertOperator(Operator):
    """
    Insert operator inserts records into the first data source at specified positions.
    Records come from attributes or second data group.

    Attributes:
    ----------
    | Name           | Type                 | Required | Default | Description                                                                                           |
    |----------------|--------------------|----------|---------|-------------------------------------------------------------------------------------------------------|
    | `insert_records` | list[dict]          |     | []      | List of records to insert into the first data source (optional if second data group provided)       |
    | `insert_idx`     | Union[int, list[int]] |     | -1      | Position(s) to insert records (-1 for append, 0+ for specific position). If list, each element corresponds to position for each record.                         |

    """

    PROPERTIES = {}

    name = "insert"
    description = "Given input data, insert records by position(s)"
    default_attributes = {
        "insert_records": {
            "type": "list[dict]",
            "description": "List of records to insert into the first data source (optional if second data group provided)",
            "required": False,
            "default": [],
        },
        "insert_idx": {
            "type": "Union[int, list[int]]",
            "description": "Position(s) to insert records (-1 for append, 0+ for specific position). If list, each element corresponds to position for each record",
            "required": False,
            "default": -1,
        },
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=insert_operator_function,
            description=description or self.description,
            properties=properties,
            validator=insert_operator_validator,
            explainer=insert_operator_explainer,
        )

    def _initialize_properties(self):
        super()._initialize_properties()

        # attribute definitions
        self.properties["attributes"] = self.default_attributes


###############
### Helper Functions of Insert Operator
def _build_result_with_multiple_inserts(base_data: List[Dict[str, Any]], insert_records: List[Dict[str, Any]], insert_positions: List[int]) -> List[Dict[str, Any]]:
    """Build result with multiple inserts efficiently."""
    base_len = len(base_data)

    # Group records by position
    position_to_records = {}
    append_records = []

    for record, pos in zip(insert_records, insert_positions):
        if pos < 0 or pos > base_len:
            append_records.append(record)
        else:
            if pos not in position_to_records:
                position_to_records[pos] = []
            position_to_records[pos].append(record)

    # Build result
    result = []

    for i in range(base_len):
        if i in position_to_records:
            result.extend(position_to_records[i])
        result.append(base_data[i])

    # Handle end position
    if base_len in position_to_records:
        result.extend(position_to_records[base_len])

    # Append invalid positions
    result.extend(append_records)

    return result


if __name__ == "__main__":
    ## calling example

    ## Example 1: insert_idx is -1, insert_records from input_data[1]
    print("=== Example 1: insert_idx = -1, records from second data group ===")
    input_data = [
        [
            {"job_id": 1, "name": "name A", "salary": 80000},
            {"job_id": 2, "name": "name B", "salary": 95000},
        ],
        [
            {"job_id": 3, "name": "name C", "salary": 75000},
            {"job_id": 4, "name": "name D", "salary": 88000},
        ],
    ]
    attributes = {"insert_idx": -1}
    result = insert_operator_function(input_data, attributes)
    print(result)

    ## Example 2: insert_idx is [2, -1, 0, 2] for input_data[0] of length 3
    print("=== Example 2: insert_idx = [2, -1, 0, 2] for data of length 3 ===")
    input_data = [
        [
            {"id": 1, "name": "A"},
            {"id": 2, "name": "B"},
            {"id": 3, "name": "C"},
        ]
    ]
    attributes = {
        "insert_records": [
            {"id": 10, "name": "X"},
            {"id": 11, "name": "Y"},
            {"id": 12, "name": "Z"},
            {"id": 13, "name": "W"},
        ],
        "insert_idx": [2, -1, 0, 2],
    }
    result = insert_operator_function(input_data, attributes)
    print(result)
