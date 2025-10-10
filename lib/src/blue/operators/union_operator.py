###### Formats
from typing import List, Dict, Any, Callable, Tuple

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer

###############
### Union Operator


def union_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Perform N-way union on multiple data sources with exact duplicate removal.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) to union, requires at least 1 data source.
        attributes: Dictionary containing union parameters including match_option.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        List containing all unique records from all data sources.
    """
    # Extract attributes
    match_option = attributes.get('match_option', 'key_match')

    # Validate input
    if not input_data or len(input_data) < 1:
        return []

    all_records = []
    for data_source in input_data:
        if data_source:
            all_records.extend(data_source)
    unique_records = _remove_duplicates(all_records, match_option)

    return [unique_records]


def union_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate union operator attributes.

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

    match_option = attributes.get('match_option', 'key_match')
    if match_option not in ['seq_match', 'key_match']:
        return False

    return True


def union_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for union operator execution.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the operation.
    """
    return default_operator_explainer(output, input_data, attributes)


class UnionOperator(Operator):
    """
    Union operator performs n-way union on multiple data sources with exact duplicate removal.
    Supports key-based matching and sequential matching strategies.

    Attributes:
    ----------
    | Name         | Type | Required | Default    | Description                                                                                   |
    |--------------|------|----------|------------|-----------------------------------------------------------------------------------------------|
    | `match_option` | str  |     | "key_match" | Matching strategy for duplicate detection: 'key_match' (exact field names and values) or 'seq_match' (position-based comparison regardless of field names) |

    """

    PROPERTIES = {}

    name = "union"
    description = "Given multiple input data sources, combine all records and remove exact duplicates"
    default_attributes = {
        "match_option": {
            "type": "str",
            "description": "Matching strategy for duplicate detection: 'key_match' (exact field names and values) or 'seq_match' (position-based comparison regardless of field names)",
            "required": False,
            "default": "key_match",
        },
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=union_operator_function,
            description=description or self.description,
            properties=properties,
            validator=union_operator_validator,
            explainer=union_operator_explainer,
        )

    def _initialize_properties(self):
        super()._initialize_properties()

        # attribute definitions
        self.properties["attributes"] = self.default_attributes


###############
### Helper Functions of Union Operator


def _remove_duplicates(records: List[Dict[str, Any]], match_option: str) -> List[Dict[str, Any]]:

    if not records:
        return []

    seen_signatures = set()
    unique_records = []

    for record in records:
        signature = _generate_record_signature(record, match_option)
        if signature not in seen_signatures:
            seen_signatures.add(signature)
            unique_records.append(record)

    return unique_records


def _generate_record_signature(record: Dict[str, Any], match_option: str) -> Tuple:
    """Generate hashable signature for record comparison."""

    def make_hashable(value):
        """Convert value to hashable equivalent."""
        try:
            if isinstance(value, (int, float, bool)):
                normalized_value = float(value)
                if normalized_value != normalized_value:  # NaN check
                    return ('__NaN__',)
                return normalized_value
            elif isinstance(value, dict):
                return tuple(sorted((k, make_hashable(v)) for k, v in value.items()))
            elif isinstance(value, list):
                return tuple(make_hashable(item) for item in value)
            elif isinstance(value, set):
                return tuple(sorted(make_hashable(item) for item in value))
            elif hasattr(value, '__hash__') and value.__hash__ is not None:
                hash(value)
                return value
            else:
                return str(value)
        except (TypeError, RecursionError):
            return str(value)

    if match_option == 'key_match':
        return tuple(sorted((k, make_hashable(v)) for k, v in record.items()))
    elif match_option == 'seq_match':
        return tuple(make_hashable(record[key]) for key in record.keys())
    else:
        raise ValueError(f"Invalid match_option: {match_option}")


if __name__ == "__main__":
    ## calling example

    input_data = [
        [
            {"job_id": 1, "name": "name A", "department": "department A", "salary": 80000},
            {"job_id": 2, "name": "name B", "department": "department B", "salary": 95000},
            {"job_id": 3, "name": "name C", "department": "department A", "salary": 75000},
        ],
        [
            {"job_id": 2, "name": "name B", "department": "department B", "salary": 95000},
            {"job_id": 4, "name": "name D", "department": "department C", "salary": 85000},
            {"job_id": 5, "name": "name E", "department": "department A", "salary": 90000},
        ],
        [
            {"job_id": 1, "name": "name A", "department": "department A", "salary": 80000},
            {"job_id": 6, "name": "name F", "department": "department D", "salary": 70000},
        ],
    ]

    ## test key matching
    print("=== UNION RESULT (key_match) ===")
    attributes = {"match_option": "key_match"}
    result = union_operator_function(input_data, attributes)
    print(f"Input records: {sum(len(data) for data in input_data)}")
    print(f"Output records: {len(result[0])}")
    print(f"Duplicates removed: {sum(len(data) for data in input_data) - len(result[0])}")
    print(result)

    ## test sequential matching
    input_data = [
        [
            {"field_a": 1, "field_b": "name A", "field_c": 80000},
            {"field_a": 2, "field_b": "name B", "field_c": 95000},
        ],
        [
            {"field_x": 1, "field_y": "name A", "field_z": 80000},
            {"field_x": 3, "field_y": "name C", "field_z": 75000},
        ],
    ]

    print("\n=== UNION RESULT (seq_match) ===")
    attributes = {"match_option": "seq_match"}
    result = union_operator_function(input_data, attributes)
    print(f"Input records: {sum(len(data) for data in input_data)}")
    print(f"Output records: {len(result[0])}")
    print(f"Duplicates removed: {sum(len(data) for data in input_data) - len(result[0])}")
    print(result)
