###### Formats
from typing import List, Dict, Any, Callable, Tuple, Set, NamedTuple

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer

###############
### Join Operator


def join_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Perform N-way join on multiple JSON array data sources.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) to join, requires at least 2 data sources.
        attributes: Dictionary containing join parameters including join_on, join_type, join_suffix, and keep_keys.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        List containing the joined records from all data sources.
    """
    join_on = attributes.get('join_on', [])
    join_type = attributes.get('join_type', 'inner')
    join_suffix = attributes.get('join_suffix', [])
    keep_keys = attributes.get('keep_keys', 'left')

    # validation check regarding input data and attributes
    if not input_data or len(input_data) < 2:
        return []
    if len(join_on) != len(input_data):
        return []
    # default suffix is _ds{i} for each data source, in future we can add prefix if needed
    if not join_suffix:
        join_suffix = [f"_ds{i}" for i in range(len(input_data))]
    if len(join_suffix) != len(input_data):
        return []
    if len(join_suffix) != len(set(join_suffix)):  # suffix must be unique
        return []

    # perform n-way join with metadata tracking
    result, schema_info = _perform_n_way_join_with_metadata(input_data, join_on, join_type, join_suffix, keep_keys)

    return [result]


def join_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate join operator attributes.

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

    join_on = attributes.get('join_on', [])
    join_suffix = attributes.get('join_suffix', [])
    keep_keys = attributes.get('keep_keys', 'left')

    if not isinstance(join_on, list) or len(join_on) < 2:
        return False

    for field_list in join_on:
        if not isinstance(field_list, list) or not field_list:
            return False
        for field in field_list:
            if not isinstance(field, str):
                return False

    if join_suffix:
        if not isinstance(join_suffix, list):
            return False
        if len(join_suffix) != len(join_on):
            return False

    if keep_keys not in ['left', 'both']:
        return False

    join_type = attributes.get('join_type', 'inner')
    if join_type not in ['inner', 'left', 'right', 'outer']:
        return False
    return True


def join_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for join operator execution.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the operation.
    """
    return default_operator_explainer(output, input_data, attributes)


class JoinOperator(Operator):
    """
    Join operator performs N-way join on JSON array datas.

    Attributes:
    ----------
    | Name        | Type           | Required | Default | Description                                      |
    |------------|----------------|----------|---------|--------------------------------------------------|
    | `join_on`    | list[list[str]] | :fontawesome-solid-circle-check: {.green-check}     | -       | List of join key lists for each data source     |
    | `join_type`  | str             |     | "inner" | Type of join: 'inner', 'left', 'right', 'outer'|
    | `join_suffix`| list[str]       |     | []      | Suffixes for non-key fields                      |
    | `keep_keys`  | str             |     | "left"  | 'left' to keep left keys only, 'both' to keep both |
    """

    PROPERTIES = {}

    name = "join"
    description = "Joins multiple JSON array data sources using N-way join operations"
    default_attributes = {
        "join_on": {"type": "list[list[str]]", "description": "List of join key lists for each data source", "required": True},
        "join_type": {"type": "str", "description": "Type of join: 'inner', 'left', 'right', 'outer'", "required": False, "default": "inner"},
        "join_suffix": {"type": "list[str]", "description": "Suffixes for non-key fields", "required": False, "default": []},
        "keep_keys": {"type": "str", "description": "'left' to keep left keys only, 'both' to keep both", "required": False, "default": "left"},
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=join_operator_function,
            description=description or self.description,
            properties=properties,
            validator=join_operator_validator,
            explainer=join_operator_explainer,
        )

    def _initialize_properties(self):
        super()._initialize_properties()

        # attribute definitions
        self.properties["attributes"] = self.default_attributes


###############
### Helper Functions of Join Operator
class FieldMetadata(NamedTuple):
    """Metadata for tracking field provenance"""

    original_name: str
    data_source: int
    suffix: str
    is_join_key: bool
    join_key_index: int = -1
    is_original: bool = True


def _perform_n_way_join_with_metadata(data_sources, join_fields, join_type, suffixes, keep_keys):
    """Perform N-way join with metadata tracking using uniform format"""
    if len(data_sources) < 2:
        return [], {}

    if len(data_sources) == 2:
        return _perform_2_way_join_with_metadata(data_sources[0], data_sources[1], join_fields[0], join_fields[1], join_type, suffixes[0], suffixes[1], keep_keys)

    # Perform first 2-way join
    intermediate_result, intermediate_schema = _perform_2_way_join_with_metadata(
        data_sources[0], data_sources[1], join_fields[0], join_fields[1], join_type, suffixes[0], suffixes[1], keep_keys
    )

    if not intermediate_result:
        return [], {}

    # Convert intermediate result to uniform format
    intermediate_uniform = (intermediate_result, intermediate_schema)

    # Prepare for next recursion
    remaining_data_sources = [intermediate_uniform] + data_sources[2:]
    remaining_join_fields = [intermediate_schema.get('join_keys', [])] + join_fields[2:]
    # For intermediate results, we don't need to assign a new suffix since it already has provenance. We'll use a placeholder that will be ignored in the 2-way join
    remaining_suffixes = ['_intermediate'] + suffixes[2:]

    return _perform_n_way_join_with_metadata(remaining_data_sources, remaining_join_fields, join_type, remaining_suffixes, keep_keys)


def _perform_2_way_join_with_metadata(left_data, right_data, left_fields, right_fields, join_type, left_suffix, right_suffix, keep_keys):
    """
    Perform 2-way join with metadata tracking using uniform format
    """
    # Handle uniform format for left data
    if isinstance(left_data, tuple) and len(left_data) == 2:
        left_records, left_schema = left_data
        left_suffix = left_schema.get('suffixes', [left_suffix])[0]
        left_provenance = left_schema.get('field_provenance', {})
    else:
        left_records = left_data
        left_schema = None
        left_provenance = {}

    # Handle uniform format for right data
    if isinstance(right_data, tuple) and len(right_data) == 2:
        right_records, right_schema = right_data
        right_suffix = right_schema.get('suffixes', [right_suffix])[0]
        right_provenance = right_schema.get('field_provenance', {})
    else:
        right_records = right_data
        right_schema = None
        right_provenance = {}

    # First, determine the output schema
    schema_info = _determine_output_schema_with_provenance(left_records, right_records, left_fields, right_fields, left_suffix, right_suffix, keep_keys, left_provenance, right_provenance)

    # Build right index for joining
    right_index = {}
    for record in right_records:
        key = _get_join_key(record, right_fields)
        right_index.setdefault(key, []).append(record)

    if join_type == 'inner':
        result = _inner_join_with_schema(left_records, right_records, left_fields, right_fields, right_index, schema_info, keep_keys)
    elif join_type == 'left':
        result = _left_join_with_schema(left_records, right_records, left_fields, right_fields, right_index, schema_info, keep_keys)
    elif join_type == 'right':
        result = _right_join_with_schema(left_records, right_records, left_fields, right_fields, right_index, schema_info, keep_keys)
    elif join_type == 'outer':
        result = _outer_join_with_schema(left_records, right_records, left_fields, right_fields, right_index, schema_info, keep_keys)
    else:
        result = []

    # Determine the join keys for the merged data based on the actual output schema
    join_keys = _determine_join_keys_from_schema(schema_info, left_fields, keep_keys)

    # Update schema info with join keys
    schema_info['join_keys'] = join_keys
    schema_info['suffixes'] = [left_suffix, right_suffix]

    return result, schema_info


def _determine_output_schema_with_provenance(left_data, right_data, left_fields, right_fields, left_suffix, right_suffix, keep_keys, left_provenance, right_provenance):
    """
    Determine the output schema with proper field mapping and suffixing using existing provenance
    Core logic:
    1. Each field gets suffix ONLY if it appears more than once in final schema
    2. keep_keys='both': all fields kept
    3. keep_keys='left': right join keys dropped
    """
    left_all_fields = set()
    right_all_fields = set()
    for record in left_data:
        left_all_fields.update(record.keys())
    for record in right_data:
        right_all_fields.update(record.keys())

    # Step 1: Collect all fields that will be in final schema
    final_fields = set()
    # Add all left fields
    for field in left_all_fields:
        final_fields.add(field)
    # Add right fields based on keep_keys
    if keep_keys == 'both':
        for field in right_all_fields:
            final_fields.add(field)
    else:
        for field in right_all_fields:
            if field not in right_fields:
                final_fields.add(field)

    # Step 2: Determine which fields need suffixes
    field_conflicts = set()
    if keep_keys == 'both':
        # For keep_keys='both', suffix fields that appear in both input sources
        field_conflicts.update(left_all_fields.intersection(right_all_fields))
    else:  # keep_keys == 'left'
        field_conflicts.update(left_all_fields.intersection(right_all_fields).difference(right_fields))

    # Step 3: Build output schema
    output_fields = {}
    field_provenance = {}
    join_key_map = []

    # Handle left fields
    for field in left_all_fields:
        if field in left_fields:
            # Join key from left
            if field in field_conflicts:
                # Use original data source suffix for field naming
                if field in left_provenance:
                    field_name = f"{field}{left_provenance[field]}"
                else:
                    field_name = f"{field}{left_suffix}"
                is_original = False
            else:
                field_name = field
                is_original = True
            output_fields[field_name] = FieldMetadata(original_name=field, data_source=0, suffix=left_suffix, is_join_key=True, join_key_index=left_fields.index(field), is_original=is_original)
            # Use existing provenance if available, otherwise use left_suffix
            if field in left_provenance:
                field_provenance[field_name] = left_provenance[field]
            else:
                field_provenance[field_name] = left_suffix
            join_key_map.append(field_name)
        else:
            # Non-join field from left
            if field in field_conflicts:
                # Use original data source suffix for field naming
                if field in left_provenance:
                    field_name = f"{field}{left_provenance[field]}"
                else:
                    field_name = f"{field}{left_suffix}"
                is_original = False
            else:
                field_name = field
                is_original = True
            output_fields[field_name] = FieldMetadata(original_name=field, data_source=0, suffix=left_suffix, is_join_key=False, is_original=is_original)
            # Use existing provenance if available, otherwise use left_suffix
            if field in left_provenance:
                field_provenance[field_name] = left_provenance[field]
            else:
                field_provenance[field_name] = left_suffix

    # Handle right fields
    for field in right_all_fields:
        if field in right_fields:
            # Join key from right
            if keep_keys == 'both':
                if field in field_conflicts:
                    # Use original data source suffix for field naming
                    if field in right_provenance:
                        field_name = f"{field}{right_provenance[field]}"
                    else:
                        field_name = f"{field}{right_suffix}"
                    is_original = False
                else:
                    field_name = field
                    is_original = True
                output_fields[field_name] = FieldMetadata(
                    original_name=field, data_source=1, suffix=right_suffix, is_join_key=True, join_key_index=right_fields.index(field), is_original=is_original
                )
                # Use existing provenance if available, otherwise use right_suffix
                if field in right_provenance:
                    field_provenance[field_name] = right_provenance[field]
                else:
                    field_provenance[field_name] = right_suffix
            # For keep_keys='left', right join keys are dropped
        else:
            # Non-join field from right
            if field in field_conflicts:
                # Use original data source suffix for field naming
                if field in right_provenance:
                    field_name = f"{field}{right_provenance[field]}"
                else:
                    field_name = f"{field}{right_suffix}"
                is_original = False
            else:
                field_name = field
                is_original = True
            output_fields[field_name] = FieldMetadata(original_name=field, data_source=1, suffix=right_suffix, is_join_key=False, is_original=is_original)
            # Use existing provenance if available, otherwise use right_suffix
            if field in right_provenance:
                field_provenance[field_name] = right_provenance[field]
            else:
                field_provenance[field_name] = right_suffix

    return {'output_fields': output_fields, 'field_provenance': field_provenance, 'left_suffix': left_suffix, 'right_suffix': right_suffix, 'join_keys': join_key_map}


def _get_join_key(record, fields):
    return tuple(record.get(field) for field in fields)


def _merge_records_with_schema(left, right, schema_info, keep_keys):
    """
    Merge records according to the determined schema
    """
    merged = {}
    output_fields = schema_info['output_fields']

    for output_field, metadata in output_fields.items():
        if metadata.data_source == 0:  # Left dataset
            value = left.get(metadata.original_name)
        else:  # Right dataset
            value = right.get(metadata.original_name)

        merged[output_field] = value

    return merged


def _inner_join_with_schema(left_data, right_data, left_on, right_on, right_index, schema_info, keep_keys):
    result = []
    for left_record in left_data:
        key = _get_join_key(left_record, left_on)
        if key in right_index:
            for right_record in right_index[key]:
                result.append(_merge_records_with_schema(left_record, right_record, schema_info, keep_keys))
    return result


def _left_join_with_schema(left_data, right_data, left_on, right_on, right_index, schema_info, keep_keys):
    result = []
    for left_record in left_data:
        key = _get_join_key(left_record, left_on)
        if key in right_index:
            for right_record in right_index[key]:
                result.append(_merge_records_with_schema(left_record, right_record, schema_info, keep_keys))
        else:
            result.append(_merge_records_with_schema(left_record, {}, schema_info, keep_keys))
    return result


def _right_join_with_schema(left_data, right_data, left_on, right_on, right_index, schema_info, keep_keys):
    result = []
    matched = set()
    for left_record in left_data:
        key = _get_join_key(left_record, left_on)
        if key in right_index:
            matched.add(key)
            for right_record in right_index[key]:
                result.append(_merge_records_with_schema(left_record, right_record, schema_info, keep_keys))

    for right_record in right_data:
        key = _get_join_key(right_record, right_on)
        if key not in matched:
            result.append(_merge_records_with_schema({}, right_record, schema_info, keep_keys))
    return result


def _outer_join_with_schema(left_data, right_data, left_on, right_on, right_index, schema_info, keep_keys):
    result = []
    matched_left = set()
    matched_right = set()

    for left_record in left_data:
        key = _get_join_key(left_record, left_on)
        if key in right_index:
            matched_left.add(key)
            matched_right.add(key)
            for right_record in right_index[key]:
                result.append(_merge_records_with_schema(left_record, right_record, schema_info, keep_keys))

    for left_record in left_data:
        key = _get_join_key(left_record, left_on)
        if key not in matched_left:
            result.append(_merge_records_with_schema(left_record, {}, schema_info, keep_keys))

    for right_record in right_data:
        key = _get_join_key(right_record, right_on)
        if key not in matched_right:
            result.append(_merge_records_with_schema({}, right_record, schema_info, keep_keys))

    return result


def _determine_join_keys_from_schema(schema_info, left_fields, keep_keys):
    """Determine join keys based on the actual output schema"""
    output_fields = schema_info['output_fields']
    join_keys = []

    for left_key in left_fields:
        # Find the corresponding output field name for this join key
        found = False
        for output_field, metadata in output_fields.items():
            if metadata.original_name == left_key and metadata.is_join_key:  # Any join key from any data source
                join_keys.append(output_field)
                found = True
                break

        # If not found in output fields, use the original name
        if not found:
            join_keys.append(left_key)

    return join_keys


if __name__ == "__main__":
    ## calling example

    input_data = [
        [{"job_id": 1, "name": "name A", "salary": 100000}, {"job_id": 2, "name": "name B", "location": "state B", "salary": 200000}],
        [{"job_id": 2, "location": "city B"}, {"job_id": 3, "location": "city C"}],
        [{"id": 1, "title": "title A"}, {"id": 4, "title": "title D"}, {"id": 2, "title": "title B"}],
    ]

    ## test keep_keys = "left"
    attributes = {"join_on": [["job_id"], ["job_id"], ["id"]], "join_type": "inner", "join_suffix": ["_employee", "_geometry", "_job_content"], "keep_keys": "left"}
    result = join_operator_function(input_data, attributes)
    print("=== JOIN RESULT ===")
    print(result)

    ## test keep_keys = "both"
    attributes = {"join_on": [["job_id"], ["job_id"], ["id"]], "join_type": "inner", "join_suffix": ["_employee", "_geometry", "_job_content"], "keep_keys": "both"}
    result = join_operator_function(input_data, attributes)
    print("=== JOIN RESULT ===")
    print(result)
