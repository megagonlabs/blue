###### Formats
from typing import List, Dict, Any, Callable, Optional
import json

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer
from blue.utils.service_utils import ServiceClient
from blue.properties import PROPERTIES

###############
### Semantic Transform Operator


def semantic_transform_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Transform data into target fields and values using LLM-based transformations.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) containing records to transform.
        attributes: Dictionary containing transformation parameters including input_meta, output_desc, and strategy.
        properties: Optional properties dictionary containing service configuration. Defaults to None.

    Returns:
        List containing transformed records with target fields and values.
    """
    input_meta = attributes.get('input_meta', {})
    output_desc = attributes.get('output_desc', {})

    if not input_data or not input_data[0] or not output_desc:
        return []

    service_client = ServiceClient(name="semantic_transform_operator_service_client", properties=properties)

    results = []
    for data_group in input_data:
        if not data_group:
            results.append([])
            continue

        # Generate transformation plan and merge into output_desc
        enhanced_output_desc = _generate_transformation_plan(data_group, input_meta, output_desc, service_client, properties)
        print(f"Enhanced output desc: {enhanced_output_desc}")

        # Select transformation execution strategy
        specified_strategy = attributes.get('strategy', 'auto')
        if specified_strategy == 'auto':
            strategy_info = _select_execution_strategy(enhanced_output_desc, data_group)
        else:
            strategy_info = _force_strategy(enhanced_output_desc, data_group, specified_strategy)

        print(f"Strategy info: {strategy_info}")

        # Execute transformation based on strategy
        strategy = strategy_info["strategy"]
        simple_fields = strategy_info["simple_fields"]
        complex_fields = strategy_info["complex_fields"]

        print(f"Selected strategy: {strategy}")
        print(f"Simple fields: {simple_fields}")
        print(f"Complex fields: {complex_fields}")

        if strategy == "simple_rename":
            result = _execute_simple_rename(data_group, enhanced_output_desc, simple_fields)
        elif strategy == "per_record":
            result = _execute_per_record(data_group, enhanced_output_desc, simple_fields, complex_fields, service_client, properties)
        elif strategy == "distinct_required_values":
            result = _execute_distinct_required_values(data_group, enhanced_output_desc, simple_fields, complex_fields, service_client, properties)
        elif strategy == "distinct_required_values_with_merged_fields":
            result = _execute_distinct_required_values_with_merged_fields(data_group, enhanced_output_desc, simple_fields, complex_fields, strategy_info, service_client, properties)
        else:  # fallback to per_record
            result = _execute_per_record(data_group, enhanced_output_desc, simple_fields, complex_fields, service_client, properties)

        results.append(result)

    return results


def semantic_transform_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate semantic transform operator attributes.

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

    output_desc = attributes.get('output_desc', {})
    if not output_desc or not isinstance(output_desc, dict):
        return False

    for field_name, field_info in output_desc.items():
        if not isinstance(field_name, str) or not isinstance(field_info, dict):
            return False
        if 'description' not in field_info or not isinstance(field_info['description'], str):
            return False

    return True


def semantic_transform_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for semantic transform operator execution.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the operation.
    """
    return default_operator_explainer(output, input_data, attributes)


def _extract_typed_schema(data_group: List[Dict[str, Any]]) -> str:
    """Extract schema with aggregated data types from a data group. The schema is only used for this operator, not DataSchema."""
    type_mapping = {
        type(None): "null",
        bool: "boolean",
        int: "integer",
        float: "float",
        str: "str",
        list: "array",
        dict: "object",
    }

    schema: Dict[str, set] = {}
    for record in data_group:
        for key, value in record.items():
            schema.setdefault(key, set()).add(type_mapping.get(type(value), "unknown"))

    # Format schema for display
    schema_display = []
    for column_name, data_types in schema.items():
        data_type_str = "|".join(sorted(data_types))
        schema_display.append(f"- {column_name} ({data_type_str})")

    return "Available input fields:\n" + "\n".join(schema_display)


def _generate_transformation_plan(
    data_group: List[Dict[str, Any]], input_meta: Dict[str, Dict[str, Any]], output_desc: Dict[str, Dict[str, Any]], service_client: ServiceClient, properties: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate transformation plan using LLM and merge into output_desc."""
    # Generate schema from input_meta or auto-generate from data
    if input_meta:
        schema_text = "Available input fields:\n"
        for field in data_group[0].keys():
            if field in input_meta:
                meta_info = input_meta[field]
                schema_text += f"- {field}: {meta_info.get('description', 'No description')}"
                if 'type' in meta_info:
                    schema_text += f" (type: {meta_info['type']})"
                schema_text += "\n"
            else:
                schema_text += f"- {field}\n"
    else:
        schema_text = _extract_typed_schema(data_group)

    # Format input metadata for the prompt
    input_metadata_text = ""
    if input_meta:
        input_metadata_text = "Input field metadata:\n"
        for field, meta_info in input_meta.items():
            input_metadata_text += f"- {field}: {meta_info.get('description', 'No description')}"
            if 'type' in meta_info:
                input_metadata_text += f" (type: {meta_info['type']})"
            if 'hints' in meta_info:
                input_metadata_text += f" (hints: {meta_info['hints']})"
            input_metadata_text += "\n"

    # Build output requirements
    output_text = "Required output fields:\n"
    for field_name, field_info in output_desc.items():
        description = field_info.get('description', '')
        field_type = field_info.get('type', '')
        required = field_info.get('required', '')
        hints = field_info.get('hints', '')
        output_text += f"- {field_name}: {description}"
        if field_type:
            output_text += f" (type: {field_type})"
        if required != '':
            output_text += f" (required: {required})"
        if hints:
            output_text += f" (hints: {hints})"
        output_text += "\n"

    # Prepare sample data (first 5 records)
    sample_data_text = ""
    if data_group:
        sample_records = data_group[:5]  # First 5 records
        sample_data_text = "Sample data records:\n"
        for i, record in enumerate(sample_records):
            sample_data_text += f"Record {i+1}: {record}\n"

    additional_data = {'schema': schema_text, 'input_metadata': input_metadata_text, 'sample_data': sample_data_text, 'output_requirements': output_text}

    # Use plan-specific properties for plan generation
    plan_properties = properties.copy() if properties else {}
    plan_properties['input_template'] = SemanticTransformOperator.PLAN_RESOLUTION_PROMPT

    result = service_client.execute_api_call({}, properties=plan_properties, additional_data=additional_data)

    # Parse the plan result
    if isinstance(result, dict):
        plan = result
    elif isinstance(result, str):
        try:
            plan = json.loads(result)
            if not isinstance(plan, dict):
                plan = {}
        except (json.JSONDecodeError, ValueError):
            plan = {}
    else:
        plan = {}

    # Merge plan into output_desc
    enhanced_output_desc = output_desc.copy()
    for target_field, plan_info in plan.items():
        if target_field in enhanced_output_desc:
            enhanced_output_desc[target_field].update(plan_info)

    return enhanced_output_desc


def _select_execution_strategy(enhanced_output_desc: Dict[str, Any], data_group: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Strategy selection with three optimization approaches."""
    if not enhanced_output_desc:
        return {"strategy": "per_record", "simple_fields": [], "complex_fields": []}

    # Separate simple renames from complex transformations
    simple_fields = []
    complex_fields = []
    for field_name, field_info in enhanced_output_desc.items():
        transformation_type = field_info.get('transformation_type', 'field_mapping_with_value_change')

        if transformation_type == 'field_mapping_without_value_change':
            simple_fields.append(field_name)
        elif transformation_type == 'field_mapping_with_value_change':
            complex_fields.append(field_name)

    # If no complex fields, use simple rename strategy (most efficient)
    if not complex_fields:
        return {"strategy": "simple_rename", "simple_fields": simple_fields, "complex_fields": []}

    # Analyze complex fields and their source field dependencies
    field_dependencies = {}
    for field_name, field_info in enhanced_output_desc.items():
        if field_name in complex_fields:
            source_fields = field_info.get('source_fields', [])
            field_dependencies[field_name] = set(source_fields)

    # Calculate costs for different strategies
    num_records = len(data_group)
    per_record_cost = num_records
    distinct_required_values_cost = _calculate_distinct_required_values_cost(field_dependencies, data_group)
    distinct_required_values_with_merged_fields_cost = _calculate_distinct_required_values_with_merged_fields_cost(field_dependencies, data_group)

    # Select the best strategy
    costs = {
        'per_record': per_record_cost,
        'distinct_required_values': distinct_required_values_cost,
        'distinct_required_values_with_merged_fields': distinct_required_values_with_merged_fields_cost,
    }
    best_strategy = min(costs.keys(), key=lambda k: costs[k])

    return {'strategy': best_strategy, 'simple_fields': simple_fields, 'complex_fields': complex_fields, 'costs': costs, 'field_dependencies': field_dependencies}


def _calculate_distinct_required_values_cost(field_dependencies: Dict[str, set], data_group: List[Dict[str, Any]]) -> int:
    """Calculate cost for distinct required values strategy: one prompt per distinct values tuple per target field."""
    total_cost = 0

    for field_name, source_fields in field_dependencies.items():
        # Get distinct value combinations for this field's source fields
        distinct_combinations = set()
        for record in data_group:
            combination = tuple(record.get(field, '') for field in source_fields)
            distinct_combinations.add(combination)

        total_cost += len(distinct_combinations)

    return total_cost


def _calculate_distinct_required_values_with_merged_fields_cost(field_dependencies: Dict[str, set], data_group: List[Dict[str, Any]]) -> int:
    """Calculate cost for merged distinct optimization strategy: groups fields with shared source dependencies."""
    # Use the same optimal merging algorithm as the execution function
    field_groups = _get_merged_field_groups(field_dependencies)

    # Calculate cost for each merged group
    total_cost = 0
    for group in field_groups:
        source_fields = group['source_fields']

        # Get distinct value combinations for these source fields
        distinct_combinations = set()
        for record in data_group:
            combination = tuple(record.get(field, '') for field in source_fields)
            distinct_combinations.add(combination)

        total_cost += len(distinct_combinations)

    return total_cost


def _get_merged_field_groups(field_dependencies: Dict[str, set]) -> List[Dict[str, Any]]:
    """Get merged field groups using optimal merging algorithm for shared source dependencies."""
    # Create initial groups by exact source field combinations
    source_combinations = {}
    for field_name, source_fields in field_dependencies.items():
        key = tuple(sorted(source_fields))
        if key not in source_combinations:
            source_combinations[key] = []
        source_combinations[key].append(field_name)

    # Merge groups that can be processed together
    # A group can be merged with another if all its source fields are a subset of the other's source fields
    merged_groups = []
    processed_combinations = set()

    # Sort combinations by size (largest first) to ensure we process supersets first
    sorted_combinations = sorted(source_combinations.items(), key=lambda x: len(x[0]), reverse=True)

    for source_fields, field_names in sorted_combinations:
        if source_fields in processed_combinations:
            continue

        # Find all combinations that can be merged with this one
        mergeable_combinations = [source_fields]
        mergeable_fields = field_names.copy()

        for other_source_fields, other_field_names in source_combinations.items():
            if other_source_fields in processed_combinations:
                continue
            if other_source_fields == source_fields:
                continue

            # Check if other_source_fields is a subset of source_fields
            if set(other_source_fields).issubset(set(source_fields)):
                mergeable_combinations.append(other_source_fields)
                mergeable_fields.extend(other_field_names)
                processed_combinations.add(other_source_fields)

        # Create merged group
        merged_groups.append({'source_fields': list(source_fields), 'target_fields': mergeable_fields})
        processed_combinations.add(source_fields)

    return merged_groups


def _force_strategy(enhanced_output_desc: Dict[str, Any], data_group: List[Dict[str, Any]], specified_strategy: str) -> Dict[str, Any]:
    """Force a specific strategy as requested by the caller."""
    if not enhanced_output_desc:
        return {"strategy": specified_strategy, "simple_fields": [], "complex_fields": []}

    # Separate simple renames from complex transformations
    simple_fields = []
    complex_fields = []

    for field_name, field_info in enhanced_output_desc.items():
        transformation_type = field_info.get('transformation_type', 'field_mapping_with_value_change')

        if transformation_type == 'field_mapping_without_value_change':
            simple_fields.append(field_name)
        elif transformation_type == 'field_mapping_with_value_change':
            complex_fields.append(field_name)

    # Validate caller strategy (simple_rename is internal only)
    valid_strategies = ['per_record', 'distinct_required_values', 'distinct_required_values_with_merged_fields']
    if specified_strategy not in valid_strategies:
        print(f"Warning: Invalid strategy '{specified_strategy}', falling back to 'per_record'")
        specified_strategy = 'per_record'

    # If no complex fields, use per_record (which will handle simple fields efficiently)
    if not complex_fields:
        return {"strategy": "per_record", "simple_fields": simple_fields, "complex_fields": []}

    # For other strategies, include field dependencies if needed
    field_dependencies = {}
    if specified_strategy in ['distinct_required_values', 'distinct_required_values_with_merged_fields']:
        for field_name, field_info in enhanced_output_desc.items():
            if field_name in complex_fields:
                source_fields = field_info.get('source_fields', [])
                field_dependencies[field_name] = set(source_fields)

    return {"strategy": specified_strategy, "simple_fields": simple_fields, "complex_fields": complex_fields, "field_dependencies": field_dependencies}


def _execute_simple_rename(data_group: List[Dict[str, Any]], enhanced_output_desc: Dict[str, Any], simple_fields: List[str]) -> List[Dict[str, Any]]:
    """Execute simple rename strategy: direct field renames without any LLM calls."""
    results = []
    for record in data_group:
        transformed_record = {}
        for field_name in simple_fields:
            field_info = enhanced_output_desc.get(field_name, {})
            source_fields = field_info.get('source_fields', [])
            if source_fields and source_fields[0] in record:
                transformed_record[field_name] = record[source_fields[0]]
        results.append(transformed_record)
    return results


def _execute_per_record(
    data_group: List[Dict[str, Any]], enhanced_output_desc: Dict[str, Any], simple_fields: List[str], complex_fields: List[str], service_client: ServiceClient, properties: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Execute per-record transformation strategy with automatic handling of simple fields."""
    results = []
    print(f"Executing per_record strategy with {len(data_group)} records")

    for record in data_group:
        transformed_record = {}

        # Handle simple fields with direct renaming (no LLM calls)
        for field_name in simple_fields:
            field_info = enhanced_output_desc.get(field_name, {})
            source_fields = field_info.get('source_fields', [])
            if source_fields and source_fields[0] in record:
                transformed_record[field_name] = record[source_fields[0]]

        # Handle complex fields with LLM if any exist
        if complex_fields:
            # Build schema description from the record
            schema_text = "Available input fields:\n"
            for field, value in record.items():
                value_type = type(value).__name__
                schema_text += f"- {field} ({value_type})\n"

            # Build output requirements from enhanced_output_desc (only complex fields)
            output_text = "Required output fields:\n"
            for target_field in complex_fields:
                if target_field in enhanced_output_desc:
                    field_info = enhanced_output_desc[target_field]
                    source_fields = field_info.get('source_fields', [])
                    description = field_info.get('description', '')
                    transformation_type = field_info.get('transformation_type', 'field_mapping_with_value_change')

                    # Only include required field if explicitly specified
                    required_info = ""
                    if 'required' in field_info:
                        required_info = f", required: {field_info['required']}"

                    # Include hints if available
                    hints_info = ""
                    if 'hints' in field_info:
                        hints_info = f", hints: {field_info['hints']}"

                    output_text += f"- {target_field}: {description} (from {', '.join(source_fields)}, {transformation_type}{required_info}{hints_info})\n"

            additional_data = {'schema': schema_text, 'output_requirements': output_text, 'input_data': record}

            result = service_client.execute_api_call({}, properties=properties, additional_data=additional_data)

            if isinstance(result, dict):
                transformed_record.update(result)
            elif isinstance(result, str):
                try:
                    parsed_result = json.loads(result)
                    if isinstance(parsed_result, dict):
                        transformed_record.update(parsed_result)
                except (json.JSONDecodeError, ValueError):
                    pass  # Keep simple fields even if complex transformation fails

        # Handle optional fields that are not in complex_fields (set to None)
        for field_name, field_info in enhanced_output_desc.items():
            if field_name not in simple_fields and field_name not in complex_fields:
                transformed_record[field_name] = None

        results.append(transformed_record)

    print(f"Per_record strategy completed: {len(data_group)} LLM calls")
    return results


def _execute_distinct_required_values(
    data_group: List[Dict[str, Any]], enhanced_output_desc: Dict[str, Any], simple_fields: List[str], complex_fields: List[str], service_client: ServiceClient, properties: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Execute distinct required values strategy with automatic handling of simple fields."""
    results = []
    print(f"Executing distinct_required_values strategy with {len(complex_fields)} complex fields")

    # Handle simple fields with direct renaming (no LLM calls)
    simple_results = []
    for record in data_group:
        transformed_record = {}
        for field_name in simple_fields:
            field_info = enhanced_output_desc.get(field_name, {})
            source_fields = field_info.get('source_fields', [])
            if source_fields and source_fields[0] in record:
                transformed_record[field_name] = record[source_fields[0]]
        simple_results.append(transformed_record)

    # Handle complex fields with distinct value deduplication
    if not complex_fields:
        return simple_results

    # Build field dependencies for complex fields
    field_dependencies = {}
    for field_name in complex_fields:
        field_info = enhanced_output_desc.get(field_name, {})
        source_fields = field_info.get('source_fields', [])
        field_dependencies[field_name] = set(source_fields)

    # Create distinct value mappings for each target field
    value_mappings = {}
    for field_name in complex_fields:
        source_fields = field_dependencies[field_name]

        # Handle fields with no source dependencies (required fields that need default values)
        if len(source_fields) == 0:
            source_fields = []

        # Get distinct combinations of source field values
        distinct_combinations = set()
        for record in data_group:
            combination = tuple(record.get(field, '') for field in source_fields)
            distinct_combinations.add(combination)

        # Transform each distinct combination
        for combination in distinct_combinations:
            # Create a sample record with this combination
            sample_record = {}
            for i, field in enumerate(source_fields):
                sample_record[field] = combination[i]

            # Build schema and requirements for this field
            schema_text = "Available input fields:\n"
            for field, value in sample_record.items():
                value_type = type(value).__name__
                schema_text += f"- {field} ({value_type})\n"

            field_info = enhanced_output_desc.get(field_name, {})
            description = field_info.get('description', '')
            transformation_type = field_info.get('transformation_type', 'field_mapping_with_value_change')

            # Only include required field if explicitly specified
            required_info = ""
            if 'required' in field_info:
                required_info = f", required: {field_info['required']}"

            # Include hints if available
            hints_info = ""
            if 'hints' in field_info:
                hints_info = f", hints: {field_info['hints']}"

            output_text = f"Required output fields:\n- {field_name}: {description} (from {', '.join(source_fields)}, {transformation_type}{required_info}{hints_info})\n"

            additional_data = {'schema': schema_text, 'output_requirements': output_text, 'input_data': sample_record}

            result = service_client.execute_api_call({}, properties=properties, additional_data=additional_data)

            if isinstance(result, dict) and field_name in result:
                value_mappings[combination] = result[field_name]
            elif isinstance(result, str):
                try:
                    parsed_result = json.loads(result)
                    if isinstance(parsed_result, dict) and field_name in parsed_result:
                        value_mappings[combination] = parsed_result[field_name]
                except (json.JSONDecodeError, ValueError):
                    pass

    # Apply transformations to all records
    for i, record in enumerate(data_group):
        transformed_record = simple_results[i].copy()

        for field_name in complex_fields:
            source_fields = field_dependencies[field_name]

            # If no source fields, use empty tuple as combination key
            if len(source_fields) == 0:
                combination = ()
            else:
                combination = tuple(record.get(field, '') for field in source_fields)

            if combination in value_mappings:
                transformed_record[field_name] = value_mappings[combination]

        # Handle optional fields that are not in complex_fields (set to None)
        for field_name, field_info in enhanced_output_desc.items():
            if field_name not in simple_fields and field_name not in complex_fields:
                transformed_record[field_name] = None

        results.append(transformed_record)

    total_calls = sum(
        len(set(tuple(record.get(field, '') for field in field_dependencies[field_name]) for record in data_group)) for field_name in complex_fields if len(field_dependencies[field_name]) > 0
    )
    print(f"Distinct_required_values strategy completed: {total_calls} LLM calls")
    return results


def _execute_distinct_required_values_with_merged_fields(
    data_group: List[Dict[str, Any]],
    enhanced_output_desc: Dict[str, Any],
    simple_fields: List[str],
    complex_fields: List[str],
    strategy_info: Dict[str, Any],
    service_client: ServiceClient,
    properties: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Execute merged distinct optimization strategy with automatic handling of simple fields."""
    results = []
    print(f"Executing merged distinct optimization strategy with {len(complex_fields)} complex fields")

    # Handle simple fields with direct renaming (no LLM calls)
    simple_results = []
    for record in data_group:
        transformed_record = {}
        for field_name in simple_fields:
            field_info = enhanced_output_desc.get(field_name, {})
            source_fields = field_info.get('source_fields', [])
            if source_fields and source_fields[0] in record:
                transformed_record[field_name] = record[source_fields[0]]
        simple_results.append(transformed_record)

    # Get merged field groups
    field_dependencies = strategy_info.get('field_dependencies', {})

    field_groups = _get_merged_field_groups(field_dependencies)
    print(f"Field dependencies: {field_dependencies}")
    print(f"Merged field groups: {field_groups}")

    # Process each field group
    complex_results = []
    for group in field_groups:
        source_fields = group['source_fields']
        target_fields = group['target_fields']

        # Get distinct value combinations for this group
        distinct_combinations = set()
        combination_to_records = {}

        for i, record in enumerate(data_group):
            combination = tuple(record.get(field, '') for field in source_fields)
            distinct_combinations.add(combination)
            if combination not in combination_to_records:
                combination_to_records[combination] = []
            combination_to_records[combination].append(i)

        # Process each distinct combination
        combination_results = {}
        for combination in distinct_combinations:
            # Use the first record with this combination as representative
            representative_record = data_group[combination_to_records[combination][0]]

            # Build schema for this combination
            if source_fields:
                schema_text = "Available input fields:\n"
                for field in source_fields:
                    value = representative_record.get(field, '')
                    value_type = type(value).__name__
                    schema_text += f"- {field} ({value_type})\n"
            else:
                schema_text = "No specific input fields available for this transformation.\n"

            # Build output requirements for this group
            output_text = "Required output fields:\n"
            for target_field in target_fields:
                if target_field in enhanced_output_desc:
                    field_info = enhanced_output_desc[target_field]
                    source_fields = field_info.get('source_fields', [])
                    description = field_info.get('description', '')
                    transformation_type = field_info.get('transformation_type', 'field_mapping_with_value_change')

                    # Only include required field if explicitly specified
                    required_info = ""
                    if 'required' in field_info:
                        required_info = f", required: {field_info['required']}"

                    # Include hints if available
                    hints_info = ""
                    if 'hints' in field_info:
                        hints_info = f", hints: {field_info['hints']}"

                    if source_fields:
                        output_text += f"- {target_field}: {description} (from {', '.join(source_fields)}, {transformation_type}{required_info}{hints_info})\n"
                    else:
                        output_text += f"- {target_field}: {description} (no source fields available,  {transformation_type}{required_info}{hints_info}), \n"

            additional_data = {'schema': schema_text, 'output_requirements': output_text, 'input_data': representative_record}

            result = service_client.execute_api_call({}, properties=properties, additional_data=additional_data)

            if isinstance(result, dict):
                combination_results[combination] = result
            elif isinstance(result, str):
                try:
                    parsed_result = json.loads(result)
                    if isinstance(parsed_result, dict):
                        combination_results[combination] = parsed_result
                    else:
                        combination_results[combination] = {}
                except (json.JSONDecodeError, ValueError):
                    combination_results[combination] = {}
            else:
                combination_results[combination] = {}

        # Apply results to all records with matching combinations
        for i, record in enumerate(data_group):
            combination = tuple(record.get(field, '') for field in source_fields)
            if combination in combination_results:
                if i >= len(complex_results):
                    complex_results.extend([{}] * (i + 1 - len(complex_results)))
                complex_results[i].update(combination_results[combination])

    # Merge simple and complex results
    for i in range(len(data_group)):
        result = simple_results[i] if i < len(simple_results) else {}
        if i < len(complex_results):
            result.update(complex_results[i])

        # Handle optional fields that are not in complex_fields (set to None)
        for field_name, field_info in enhanced_output_desc.items():
            if field_name not in simple_fields and field_name not in complex_fields:
                # This is an optional field with value changes that we're not processing
                result[field_name] = None

        results.append(result)

    total_calls = sum(len(set(tuple(record.get(field, '') for field in group['source_fields']) for record in data_group)) for group in field_groups)
    print(f"Merged distinct optimization strategy completed: {total_calls} LLM calls")
    return results


class SemanticTransformOperator(Operator, ServiceClient):
    """
    Operator that transforms data into target fields and values using LLM-based transformations.

    Attributes:
    ----------
    | Name     | Type | Required | Default | Description |
    |----------|------|----------|---------|-------------|
    | `input_meta` | dict |  | {} | Optional metadata about input fields |
    | `output_desc` | dict | :fontawesome-solid-circle-check: {.green-check} | N/A | Required description of target fields to create |
    | `strategy` | str |  | "auto" | Execution strategy: 'auto' (automatic cost-based selection), 'per_record' (one LLM call per record), 'distinct_required_values' (deduplicate by distinct values), 'distinct_required_values_with_merged_fields' (merged distinct optimization) |


    """

    PLAN_RESOLUTION_PROMPT = """## Task
You are a data transformation planner. Analyze the input schema and output requirements to create a transformation plan.

## Input Schema
${schema}

## Input Metadata (if provided)
${input_metadata}

## Sample Data (first 5 records)
${sample_data}

## Output Requirements
${output_requirements}

## Instructions
Create a transformation plan that maps each target field to its source fields and transformation type.

For each target field, determine:
1. **source_fields**: List of input fields needed to create this target field
2. **transformation_type**: Either "field_mapping_without_value_change" or "field_mapping_with_value_change"
   - Use "field_mapping_without_value_change" when you can simply rename/copy a field without any value modification
   - Use "field_mapping_with_value_change" when you need to modify, combine, derive, or transform values

## Output Format
Return a JSON object where each key is a target field name and the value is:
{
  "source_fields": ["field1", "field2", ...],
  "transformation_type": "field_mapping_without_value_change" | "field_mapping_with_value_change"
}

## Examples
- Simple rename: `{"full_name": {"source_fields": ["name"], "transformation_type": "field_mapping_without_value_change"}}`
- Value transformation: `{"age_group": {"source_fields": ["age"], "transformation_type": "field_mapping_with_value_change"}}`
- Field combination: `{"full_address": {"source_fields": ["street", "city", "state"], "transformation_type": "field_mapping_with_value_change"}}`

Return only the JSON object, no additional text.
"""

    TRANSFORM_PROMPT = """## Task
You are a data transformation expert. Transform the input data to match the required output schema.

## Available Input Fields
${schema}

## Target Output Fields
${output_requirements}

## Input Data Record
${input_data}

## Instructions
1. Transform the input data record to create the target output fields
2. Use the field descriptions, optional types, optional required flags, and optional hints to guide your transformations.
3. Ensure output values match the specified data types (str, integer, boolean, etc.) if specified.
4. **Field Inclusion Rules**:
   - If a field is marked as "required: True", it MUST be present in the output with an appropriate value
   - If a field is marked as "required: False", it can be omitted if you cannot reasonably infer its value from the input data
   - If no "required" information is provided, only include fields that you confidently infer or derive from the available input data
5. **Required Field Generation**: If a required field cannot be created from available data, use a null value (None) that satisfies the field type.ck

6. **Conservative Approach**: When in doubt about whether to include a field, err on the side of omitting it rather than generating speculative values
7. **Do NOT generate fake or speculative values** for fields that cannot be reasonably inferred from the input data
8. Return the transformed data as a JSON object

Return only the transformed JSON object, no additional text.
"""

    PROPERTIES = {
        # openai related properties
        "openai.api": "ChatCompletion",
        "openai.model": "gpt-4o",
        "openai.stream": False,
        "openai.max_tokens": 1024,
        "openai.temperature": 0.0,
        # io related properties
        "input_json": "[{\"role\": \"user\"}]",
        "input_context": "$[0]",
        "input_context_field": "content",
        "input_field": "messages",
        "input_template": TRANSFORM_PROMPT,
        "output_path": "$.choices[0].message.content",
        # service related properties
        "service_prefix": "openai",
        # output transformations
        "output_transformations": [{"transformation": "replace", "from": "```", "to": ""}, {"transformation": "replace", "from": "json", "to": ""}],
        "output_strip": True,
        "output_cast": "json",
    }

    name = "semantic_transform"
    description = "Transforms data into target fields and values using LLM-based transformations"
    default_attributes = {
        "input_meta": {"type": "dict", "description": "Optional metadata about input fields", "required": False, "default": {}},
        "output_desc": {"type": "dict", "description": "Required description of target fields to create", "required": True},
        "strategy": {
            "type": "str",
            "description": "Execution strategy: 'auto' (automatic cost-based selection), 'per_record' (one LLM call per record), 'distinct_required_values' (deduplicate by distinct values), 'distinct_required_values_with_merged_fields' (merged distinct optimization).",
            "required": False,
            "default": "auto",
        },
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=semantic_transform_operator_function,
            description=description or self.description,
            properties=properties,
            validator=semantic_transform_operator_validator,
            explainer=semantic_transform_operator_explainer,
        )

    def _initialize_properties(self):
        super()._initialize_properties()
        self.properties["attributes"] = self.default_attributes

        # service_url, set as default
        self.properties["service_url"] = PROPERTIES["services.openai.service_url"]


if __name__ == "__main__":
    ## calling example

    # Test data
    input_data = [
        [
            {
                'full_name': 'AAA BBBB',
                'email': 'aaa.bbb@email.com',
                'phone': '111-111-1111',
                'birth_date': '1900-05-15',
                'street': '123 XXX St',
                'city': 'New York',
                'state': 'NY',
                'zip_code': '10001',
            },
            {
                'full_name': 'CCCC DD EEE',
                'email': 'xxxyyy@email.com',
                'phone': '222-222-2222',
                'birth_date': '1905-12-03',
                'street': '456 YYY Ave',
                'city': 'San Francisco',
                'state': 'CA',
                'zip_code': '94111',
            },
        ]
    ]

    print(f"=== Semantic Transform attributes ===")

    # just used to get the default properties
    semantic_transform_operator = SemanticTransformOperator()
    properties = semantic_transform_operator.properties
    print(f"=== Semantic Transform PROPERTIES ===")
    print(properties)
    properties['service_url'] = 'ws://localhost:8001'  # update this to your service url

    # Example 1: Basic field transformation
    print("=== Example 1: semantic transformation without input metadata or hints===")
    attributes = {
        'output_desc': {
            'first_name': {'description': 'First name of the person'},
            'last_name': {'description': 'Last name of the person'},
            'name': {'description': 'Name of the person'},
            'age': {'description': 'Age of the person'},
            'formatted_phone': {'description': 'Phone number in appropriate format'},
            'full_address': {'description': 'The full address of the person'},
        }
    }
    print(attributes)
    result = semantic_transform_operator_function(input_data, attributes, properties)
    print("=== Semantic Transform RESULT (Example 1) ===")
    print(result)

    # Example 2: With input metadata
    print("=== Example 2: transform with input metadata and hints===")
    attributes = {
        'input_meta': {'full_name': {'description': 'Complete name of the person', 'type': 'str'}, 'birth_date': {'description': 'Date of birth in YYYY-MM-DD format', 'type': 'date'}},
        'output_desc': {
            'name': {'description': 'name of the person', 'type': 'str', 'hints': 'use first name as the name'},
            'age': {'description': 'Age of the person', 'type': 'integer', 'hints': 'Infer from birth_date'},
            'is_adult': {'description': 'Boolean indicating if person is 18 or older', 'type': 'boolean', 'hints': 'Derive from age/birthday'},
        },
    }
    print(attributes)
    result = semantic_transform_operator_function(input_data, attributes, properties)
    print("=== Semantic Transform RESULT (Example 2) ===")
    print(result)

    # Example 3: Transformation layer between NL2SQL and semantic_extract operators
    print("=== Example 3: NL2SQL to Semantic Extract Transformation ===")
    # Simulated NL2SQL operator output (database query results)
    # Disclaimer: all the data is fake and made up for demonstration purposes, don't use it for any other purpose.
    nl2sql_output = [
        [
            {
                'job_id': 1,
                'job_title': 'Senior Software Engineer',
                'job_description': 'We are looking for a senior software engineer with 5+ years of experience in Java, Spring Framework, and microservices. Must have experience with AWS, Docker, and CI/CD pipelines.',
                'company_name': 'Company A',
                'location': 'San Francisco, CA',
                'salary_min': 120000,
                'salary_max': 150000,
                'posted_date': '2025-01-15',
                'contact_email': 'hr@companya.com',
                'contact_phone': '333-333-3333',
                'experience_required': '5+ years',
                'education_level': 'Bachelor degree',
            },
            {
                'job_id': 2,
                'job_title': 'Data Scientist',
                'job_description': 'Seeking a data scientist with expertise in Python, machine learning, and statistical analysis. Experience with TensorFlow, PyTorch, and cloud platforms required.',
                'company_name': 'Company B',
                'location': 'New York, NY',
                'salary_min': 100000,
                'salary_max': 130000,
                'posted_date': '2025-09-01',
                'contact_email': 'careers@companyb.com',
                'contact_phone': '444 444 4444',
                'experience_required': 'at least 3 years',
                'education_level': 'Master degree',
            },
            {
                'job_id': 3,
                'job_title': 'Frontend Developer',
                'job_description': 'Looking for a frontend developer skilled in React, TypeScript, and modern web development. Experience with Redux, GraphQL, and responsive design preferred.',
                'company_name': 'Company C',
                'location': 'Austin, TX',
                'salary_min': 80000,
                'salary_max': 110000,
                'posted_date': '2024-01-18',
                'contact_email': 'jobs@companyc.com',
                'contact_phone': '+1 (555) 555-5555',
                'experience_required': '2+ years',
                'education_level': 'Bachelor',
            },
        ]
    ]

    attributes = {
        'input_meta': {
            'job_description': {'description': 'Job description text containing skills and requirements', 'type': 'str'},
            'job_title': {'description': 'Job title or position name', 'type': 'str'},
            'company_name': {'description': 'Name of the hiring company', 'type': 'str'},
            'location': {'description': 'Job location in format "City, State"', 'type': 'str'},
            'salary_min': {'description': 'Minimum salary amount', 'type': 'integer'},
            'salary_max': {'description': 'Maximum salary amount', 'type': 'integer'},
            'contact_email': {'description': 'Contact email address', 'type': 'str'},
            'contact_phone': {'description': 'Contact phone number', 'type': 'str'},
            'experience_required': {'description': 'Required years of experience', 'type': 'str'},
            'education_level': {'description': 'Required education level', 'type': 'str'},
        },
        'output_desc': {
            # Field rename
            'position': {'description': 'Job position title', 'type': 'str', 'hints': 'The position refers to job_title'},
            # Field unchanged
            'job_description': {'description': 'Full job description text', 'type': 'str'},
            # Value transformation
            'company': {'description': 'company name in lower case', 'type': 'str'},
            # Field split
            'city': {'description': 'City name extracted from location', 'type': 'str', 'hints': 'Get from location field'},
            'state': {'description': 'State abbreviation extracted from location', 'type': 'str'},
            # Fields merge
            'salary_range': {'description': 'Salary range combining min and max values', 'type': 'str'},
            # Fields merge
            'contact_info': {
                'description': 'Contact information combining email and phone',
                'type': 'str',
                'hints': 'Merge contact_email and contact_phone into format "email | phone", phone number should be in (XXX) XXX-XXXX format',
            },
            # Value transformation
            'education_degree': {'description': 'Single word education degree', 'type': 'str'},
            # Value transformation
            'description_summary': {'description': 'Summary of the job description, be concise and to the point.', 'type': 'str', 'hints': 'use all fields to generate a summary'},
        },
    }

    print(attributes)
    result = semantic_transform_operator_function(nl2sql_output, attributes, properties)
    print("=== Semantic Transform RESULT (Example 3) ===")
    print(result)

    # Example 4: Transform natural language queries to NL2SQL operator attributes (note, this is  just for example use, the actual predecessor of NL2SQL operator might be different, like data discovery operator)
    print("\n=== Example 4: Natural Language to NL2SQL Attributes Transformation (with required fields from the target NL2SQL operator) ===")

    # Input: Natural language queries that need to be transformed into NL2SQL operator attributes
    input_data = [
        [
            {'data': 'what jobs are available for software engineers in San Francisco?'},
            {'data': 'show me data scientist positions with salary above 100k'},
            {'data': 'find frontend developer jobs at tech companies'},
        ]
    ]

    attributes = {
        'input_meta': {'data': {'description': 'Natural language query about job search', 'type': 'str'}},
        'output_desc': {
            'source': {'description': 'Data source name', 'type': 'str', 'required': True},
            'question': {'description': 'Natural language question to translate to SQL', 'type': 'str', 'required': True},
            'protocol': {'description': 'Database protocol (postgres or mysql)', 'type': 'str', 'required': True},
            'database': {'description': 'Database name', 'type': 'str', 'required': True},
            'collection': {'description': 'Collection/schema name', 'type': 'str', 'required': True},
            'case_insensitive': {'description': 'Case insensitive str matching', 'type': 'boolean', 'required': False},
            'additional_requirements': {'description': 'Additional requirements for SQL generation', 'type': 'str', 'required': False, 'hints': 'Set to empty str as default'},
            'context': {
                'description': 'Optional context for domain knowledge',
                'type': 'str',
                'required': False,
                'hints': 'Set to "This is a job database with information about job postings, skills, companies, and salaries"',
            },
            'schema': {
                'description': 'JSON str of database schema (optional - will be fetched automatically if not provided)',
                'type': 'str',
                'required': False,
                'hints': 'Set to empty str as default - schema will be fetched automatically',
            },
        },
    }

    print(attributes)
    result = semantic_transform_operator_function(input_data, attributes, properties)
    print("=== Semantic Transform RESULT (Example 4) ===")
    print(result)

    # Example 5: Transform natural language queries with only question required (all others optional)
    print("\n=== Example 5: Natural Language to NL2SQL Attributes (Only Question Required) ===")
    input_data = [
        [
            {'data': 'what jobs are available for software engineers in San Francisco?'},
            {'data': 'show me data scientist positions with salary above 100k'},
            {'data': 'find frontend developer jobs at tech companies'},
        ]
    ]

    attributes = {
        'input_meta': {'data': {'description': 'Natural language query about job search', 'type': 'str'}},
        'output_desc': {
            'source': {'description': 'Data source name', 'type': 'str', 'required': False},
            'question': {'description': 'Natural language question to translate to SQL', 'type': 'str', 'required': True},
            'protocol': {'description': 'Database protocol (postgres or mysql)', 'type': 'str', 'required': False},
            'database': {'description': 'Database name', 'type': 'str', 'required': False},
            'collection': {'description': 'Collection/schema name', 'type': 'str', 'required': False},
            'case_insensitive': {'description': 'Case insensitive str matching', 'type': 'boolean', 'required': False},
            'additional_requirements': {'description': 'Additional requirements for SQL generation', 'type': 'str', 'required': False, 'hints': 'Set to empty str as default'},
            'context': {
                'description': 'Optional context for domain knowledge',
                'type': 'str',
                'required': False,
                'hints': 'Set to "This is a job database with information about job postings, skills, companies, and salaries"',
            },
        },
    }

    result = semantic_transform_operator_function(input_data, attributes, properties)
    print("=== Semantic Transform RESULT (Example 5) ===")
    print(result)

    # Example 6: Transform natural language queries with NO "required" keys at all
    print("\n=== Example 6: Natural Language to NL2SQL Attributes (No Required Keys) ===")
    input_data = [
        [
            {'data': 'what jobs are available for software engineers in San Francisco?'},
            {'data': 'show me data scientist positions with salary above 100k'},
            {'data': 'find frontend developer jobs at tech companies'},
        ]
    ]

    attributes = {
        'input_meta': {'data': {'description': 'Natural language query about job search', 'type': 'str'}},
        'output_desc': {
            'source': {'description': 'Data source name', 'type': 'str'},
            'question': {'description': 'Natural language question to translate to SQL', 'type': 'str'},
            'protocol': {'description': 'Database protocol (postgres or mysql)', 'type': 'str'},
            'database': {'description': 'Database name', 'type': 'str'},
            'collection': {'description': 'Collection/schema name', 'type': 'str'},
            'case_insensitive': {'description': 'Case insensitive str matching', 'type': 'boolean'},
            'additional_requirements': {'description': 'Additional requirements for SQL generation', 'type': 'str', 'hints': 'Set to empty str as default'},
            'context': {
                'description': 'Optional context for domain knowledge',
                'type': 'str',
                'hints': 'Set to "This is a job database with information about job postings, skills, companies, and salaries"',
            },
        },
    }

    result = semantic_transform_operator_function(input_data, attributes, properties)
    print("=== Semantic Transform RESULT (Example 6) ===")
    print(result)
