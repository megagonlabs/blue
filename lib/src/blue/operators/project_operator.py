###### Formats
from typing import List, Dict, Any, Callable, Set

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer

###############
### Project Operator (Projection)


def project_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Project records to keep only specified keys and optionally rename them (key-wise projection).

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]), uses the first data source for projection.
        attributes: Dictionary containing projection parameters including kept_keys and key_mapping.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        List containing projected records with only the specified keys.
    """
    # Extract attributes
    kept_keys = attributes.get('kept_keys', [])
    key_mapping = attributes.get('key_mapping', {})

    # Validate input
    if not input_data or not input_data[0]:
        return []

    if not kept_keys:
        return []

    data = input_data[0]  # Use first data source

    # Project records
    result = []
    for record in data:
        projected_record = {}
        for key in kept_keys:
            if key in record:
                # Apply key mapping if specified
                output_key = key_mapping.get(key, key)
                projected_record[output_key] = record[key]
        result.append(projected_record)
    return [result]


def project_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate project operator attributes.

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

    # Business logic validation (types already checked by default validator)
    kept_keys = attributes.get('kept_keys', [])
    key_mapping = attributes.get('key_mapping', {})

    # Validate that all keys in key_mapping are in kept_keys
    for mapped_key in key_mapping.keys():
        if mapped_key not in kept_keys:
            return False

    try:
        # Validate key mapping conflicts
        _validate_key_mapping_conflicts(kept_keys, key_mapping)
    except ValueError:
        return False

    return True


def project_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for project operator execution.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the operation.
    """
    return default_operator_explainer(output, input_data, attributes)


def _validate_key_mapping_conflicts(kept_keys: List[str], key_mapping: Dict[str, str]) -> None:
    if not key_mapping:
        return
    # Get the final set of output keys after mapping
    output_keys: Set[str] = set()
    for key in kept_keys:
        if key in key_mapping:
            output_key = key_mapping[key]
        else:
            output_key = key
        if output_key in output_keys:
            raise ValueError(f"Key mapping conflict: output key '{output_key}' appears multiple times")
        output_keys.add(output_key)


class ProjectOperator(Operator):
    """
    Project operator keeps only specified keys and optionally renames them (key-wise projection).
    Supports key selection and renaming with conflict detection.

    Attributes:
    ----------
    | Name        | Type         | Required | Default | Description                                |
    |------------|-------------|---------|--------|--------------------------------------------|
    | `kept_keys`  | list[str]   | :fontawesome-solid-circle-check: {.green-check}    | -      | List of keys to keep in each record       |
    | `key_mapping`| dict[str, str]|    | {}     | Dictionary mapping old key names to new key names |
    """

    PROPERTIES = {}

    name = "project"
    description = "Given an input data, return only a set of attributes for each data element (key-wise)"
    default_attributes = {
        "kept_keys": {"type": "list[str]", "description": "List of keys to keep in each record", "required": True},
        "key_mapping": {"type": "dict[str, str]", "description": "Dictionary mapping old key names to new key names", "required": False, "default": {}},
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=project_operator_function,
            description=description or self.description,
            properties=properties,
            validator=project_operator_validator,
            explainer=project_operator_explainer,
        )

    def _initialize_properties(self):
        super()._initialize_properties()

        # attribute definitions
        self.properties["attributes"] = self.default_attributes


if __name__ == "__main__":
    ## calling example

    input_data = [
        [
            {"job_id": 1, "name": "name A", "title": "title A", "salary": 80000, "location": "location A"},
            {"job_id": 2, "name": "name B", "title": "title B", "salary": 95000, "location": "location B"},
            {"job_id": 3, "name": "name C", "title": "title C", "salary": 75000, "location": "location C"},
        ]
    ]

    ## test basic projection
    attributes = {"kept_keys": ["job_id", "name", "salary"]}
    result = project_operator_function(input_data, attributes)
    print("=== PROJECT RESULT (basic projection) ===")
    print(result)

    ## test projection with key mapping
    attributes = {"kept_keys": ["job_id", "name", "salary"], "key_mapping": {"name": "employee_name", "salary": "annual_salary"}}
    result = project_operator_function(input_data, attributes)
    print("=== PROJECT RESULT (with key mapping) ===")
    print(result)
