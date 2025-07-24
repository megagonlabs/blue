###### Formats
from typing import List, Dict, Any, Callable, Set

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer

###############
### Project Operator (Projection)


def project_operator_function(input_data: List[List[Dict[str, Any]]], params: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Project records to keep only specified keys and optionally rename them (key-wise projection)."""
    # Extract parameters
    kept_keys = params.get('kept_keys', [])
    key_mapping = params.get('key_mapping', {})

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


def project_operator_validator(params: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate project operator parameters."""
    try:
        if not default_operator_validator(params, properties):
            return False
    except Exception:
        return False

    # Business logic validation (types already checked by default validator)
    kept_keys = params.get('kept_keys', [])
    key_mapping = params.get('key_mapping', {})

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


def project_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], params: Dict[str, Any]) -> Dict[str, Any]:
    return default_operator_explainer(output, input_data, params)


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
    """

    name = "project"
    description = "Given an input data, return only a set of attributes for each data element (key-wise)"
    default_parameters = {
        "kept_keys": {"type": "list[str]", "description": "List of keys to keep in each record", "required": True},
        "key_mapping": {"type": "dict[str, str]", "description": "Dictionary mapping old key names to new key names", "required": False, "default": {}},
    }

    def __init__(self, name: str = "project", description: str = None, properties: Dict[str, Any] = None, function: Callable = None, validator: Callable = None, explainer: Callable = None):
        if description is None:
            description = self.description

        if properties is None:
            properties = {}
        if "parameters" not in properties:
            properties["parameters"] = self.default_parameters
        if function is None:
            function = project_operator_function
        if validator is None:
            validator = project_operator_validator
        if explainer is None:
            explainer = project_operator_explainer

        super().__init__(
            name=name,
            description=description,
            properties=properties,
            function=function,
            validator=validator,
            explainer=explainer,
        )


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
    params = {"kept_keys": ["job_id", "name", "salary"]}
    result = project_operator_function(input_data, params)
    print("=== PROJECT RESULT (basic projection) ===")
    print(result)

    ## test projection with key mapping
    params = {"kept_keys": ["job_id", "name", "salary"], "key_mapping": {"name": "employee_name", "salary": "annual_salary"}}
    result = project_operator_function(input_data, params)
    print("=== PROJECT RESULT (with key mapping) ===")
    print(result)
