###### Formats
from typing import List, Dict, Any, Callable, Tuple

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer

###############
### Intersect Operator


def intersect_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Find records that exist in all input data sources.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) to intersect, requires at least 2 data sources.
        attributes: Dictionary containing intersection parameters including match_option.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        List containing records that exist in all data sources.
    """
    # Extract attributes
    match_option = attributes.get('match_option', 'key_match')

    # Validate input
    if not input_data or len(input_data) < 2:
        return []
    non_empty_data = [data for data in input_data if data]
    if len(non_empty_data) < 2:
        return []

    intersect_records = _find_intersect_records(non_empty_data, match_option)
    return [intersect_records]


def intersect_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate intersect operator attributes.

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


def intersect_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for intersect operator execution.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the operation.
    """
    return default_operator_explainer(output, input_data, attributes)


class IntersectOperator(Operator):
    """
    Intersect operator finds records that exist in all input data sources.
    Supports key-based matching and sequential matching strategies.

    Attributes:
    ----------
    | Name         | Type | Required | Default     | Description                                                                                                      |
    |--------------|------|----------|-------------|------------------------------------------------------------------------------------------------------------------|
    | `match_option` | str  |     | "key_match" | Matching strategy for record comparison: 'key_match' (exact field names and values) or 'seq_match' (position-based comparison regardless of field names) |

    """

    PROPERTIES = {}

    name = "intersect"
    description = "Given multiple input data sources, return only records that exist in all data sources"
    default_attributes = {
        "match_option": {
            "type": "str",
            "description": "Matching strategy for record comparison: 'key_match' (exact field names and values) or 'seq_match' (position-based comparison regardless of field names)",
            "required": False,
            "default": "key_match",
        },
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=intersect_operator_function,
            description=description or self.description,
            properties=properties,
            validator=intersect_operator_validator,
            explainer=intersect_operator_explainer,
        )

    def _initialize_properties(self):
        super()._initialize_properties()

        # attribute definitions
        self.properties["attributes"] = self.default_attributes


###############
### Helper Functions of Intersect Operator


def _find_intersect_records(data_sources: List[List[Dict[str, Any]]], match_option: str) -> List[Dict[str, Any]]:
    """Find records common to all data sources using hash-based matching."""
    if not data_sources:
        return []

    base_data = data_sources[0]
    if len(data_sources) == 1:
        return base_data

    other_signature_sets = []
    for data_source in data_sources[1:]:
        signature_set = set()
        for record in data_source:
            signature = _generate_record_signature(record, match_option)
            signature_set.add(signature)
        other_signature_sets.append(signature_set)

    intersect_records = []
    for record in base_data:
        signature = _generate_record_signature(record, match_option)
        if all(signature in signature_set for signature_set in other_signature_sets):
            intersect_records.append(record)

    return intersect_records


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
            {"job_id": 1, "name": "name A", "department": "department A", "salary": 80000},
        ],
        [
            {"job_id": 1, "name": "name A", "department": "department A", "salary": 80000},
            {"job_id": 5, "name": "name E", "department": "department D", "salary": 70000},
            {"job_id": 2, "name": "name B", "department": "department B", "salary": 95000},
        ],
    ]

    ## test key matching
    print("=== INTERSECT RESULT (key_match) ===")
    attributes = {"match_option": "key_match"}
    result = intersect_operator_function(input_data, attributes)
    print(f"Input records per source: {[len(data) for data in input_data]}")
    print(f"Output records: {len(result[0])}")
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
        [
            {"other_a": 1, "other_b": "name A", "other_c": 80000},
            {"other_a": 4, "other_b": "name D", "other_c": 65000},
        ],
    ]

    print("\n=== INTERSECT RESULT (seq_match) ===")
    attributes = {"match_option": "seq_match"}
    result = intersect_operator_function(input_data, attributes)
    print(f"Input records per source: {[len(data) for data in input_data]}")
    print(f"Output records: {len(result[0])}")
    print(result)
