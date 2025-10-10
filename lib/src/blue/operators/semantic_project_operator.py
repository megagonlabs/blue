###### Formats
from typing import List, Dict, Any, Callable, Optional, Set

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer
from blue.utils.service_utils import ServiceClient
from blue.properties import PROPERTIES

###############
### Semantic Project Operator


def semantic_project_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Project records to select and rename columns using LLM-based mapping resolution.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) containing records to project.
        attributes: Dictionary containing projection parameters including projection_instructions.
        properties: Optional properties dictionary containing service configuration. Defaults to None.

    Returns:
        List containing projected records with selected and renamed columns.
    """
    projection_instructions = attributes.get('projection_instructions', '')

    if not input_data or not input_data[0]:
        return []

    if not projection_instructions:
        return []

    service_client = ServiceClient(name="semantic_project_operator_service_client", properties=properties)

    results = []
    for data_group in input_data:
        if not data_group:
            results.append([])
            continue

        # Generate column mapping using LLM
        schema = _extract_typed_schema(data_group)
        resolved_mapping = _resolve_column_mapping(schema, projection_instructions, service_client, properties)
        if not resolved_mapping:
            results.append([])
            continue

        # Apply projection with resolved mapping
        result = _apply_projection(data_group, resolved_mapping)
        results.append(result)

    return results


def semantic_project_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate semantic project operator attributes.

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

    projection_instructions = attributes.get('projection_instructions', '')
    if not isinstance(projection_instructions, str) or not projection_instructions.strip():
        return False

    return True


def semantic_project_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for semantic project operator execution.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the operation.
    """
    return default_operator_explainer(output, input_data, attributes)


def _extract_typed_schema(data_group: List[Dict[str, Any]]) -> Dict[str, str]:
    """Extract schema with aggregated data types from a data group. The schema is only used for this operator, not DataSchema."""
    type_mapping = {
        type(None): "null",
        bool: "boolean",
        int: "integer",
        float: "float",
        str: "string",
        list: "array",
        dict: "object",
    }

    schema: Dict[str, set] = {}
    for record in data_group:
        for key, value in record.items():
            schema.setdefault(key, set()).add(type_mapping.get(type(value), "unknown"))
    return {key: "|".join(sorted(types)) for key, types in schema.items()}


def _resolve_column_mapping(schema: Dict[str, str], projection_instructions: str, service_client: ServiceClient, properties: Dict[str, Any]) -> Dict[str, str]:
    """Use LLM to resolve column mapping based on projection instructions."""
    # Format schema for display
    schema_display = []
    for column_name, data_type in schema.items():
        schema_display.append(f"- {column_name} ({data_type})")

    additional_data = {'schema': '\n'.join(schema_display), 'projection_instructions': projection_instructions}

    result = service_client.execute_api_call({}, properties=properties, additional_data=additional_data)

    if isinstance(result, dict):
        return result
    else:
        return {}


def _apply_projection(data_group: List[Dict[str, Any]], resolved_mapping: Dict[str, str]) -> List[Dict[str, Any]]:
    """Apply projection using resolved mapping."""
    if not resolved_mapping:
        return []

    projected_records = []
    for record in data_group:
        projected_record = {}
        for old_key, new_key in resolved_mapping.items():
            if old_key in record:
                projected_record[new_key] = record[old_key]
        projected_records.append(projected_record)

    return projected_records


class SemanticProjectOperator(Operator, ServiceClient):
    """
    Semantic Project Operator projects records to select and rename columns using LLM-based mapping resolution.
    Uses natural language instructions to determine which columns to keep and how to rename them.

    Attributes:
    ----------
    | Name                   | Type | Required | Default | Description                                                                 |
    |------------------------|------|----------|---------|-----------------------------------------------------------------------------|
    | `projection_instructions` | str  | :fontawesome-solid-circle-check: {.green-check}     | None    | Natural language description of which columns to keep and how to rename them |

    """

    MAPPING_PROMPT = """## Task
You are given a database schema with data types and natural language projection instructions. Your job is to generate a JSON mapping that specifies which columns to keep and how to rename them.

## Available Schema (with data types)
${schema}

## Projection Instructions
${projection_instructions}

## Output Requirements
- Return a **single JSON object** as the output
- The JSON object must contain key-value pairs where:
  - **Keys**: original column names from the schema (exact matches)
  - **Values**: new column names for the output
- **Column Selection Rules**:
  - Only include columns that should be kept in the output
  - If a column should be dropped, do not include it in the mapping
  - If a column should be renamed, map the old name to the new name
  - If a column should keep its original name, map it to itself
- **Validation Rules**:
  - All keys must exist in the provided schema
  - All values must be unique (no duplicate output column names)
  - All values must be valid column names (no special characters, extra spaces, etc.)
- **Examples**:
  - Keep and rename: `{"fname": "full_name", "lname": "last_name"}`
  - Keep without rename: `{"skills": "skills", "experience": "experience"}`
  - Drop column: simply don't include it in the mapping

## Additional Notes
- Interpret the natural language requirements carefully
- Be precise about which columns to keep vs drop
- Follow standard naming conventions for column names
- Return only the JSON object, no explanations or additional text

---

### Output JSON Object
"""

    PROPERTIES = {
        # openai related properties
        "openai.api": "ChatCompletion",
        "openai.model": "gpt-4o",
        "openai.stream": False,
        "openai.max_tokens": 1024,
        "openai.temperature": 0,
        # io related properties
        "input_json": "[{\"role\": \"user\"}]",
        "input_context": "$[0]",
        "input_context_field": "content",
        "input_field": "messages",
        "input_template": MAPPING_PROMPT,
        "output_path": "$.choices[0].message.content",
        # service related properties
        "service_prefix": "openai",
        # output transformations
        "output_transformations": [{"transformation": "replace", "from": "```", "to": ""}, {"transformation": "replace", "from": "json", "to": ""}],
        "output_strip": True,
        "output_cast": "json",
    }

    name = "semantic_project"
    description = "Projects records to select and rename columns using LLM-based mapping resolution"
    default_attributes = {
        "projection_instructions": {"type": "str", "description": "Natural language description of which columns to keep and how to rename them", "required": True},
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=semantic_project_operator_function,
            description=description or self.description,
            properties=properties,
            validator=semantic_project_operator_validator,
            explainer=semantic_project_operator_explainer,
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
                "first_name": "first_name_A",
                "last_name": "last_name_A",
                "current_title": "Senior Software Engineer",
                "skills": ["Python", "React", "SQL", "Docker", "AWS"],
                "years_experience": 5,
                "degree": "Bachelor of Computer Science",
                "certifications": ["AWS Certified Developer", "Google Cloud Professional"],
            },
            {
                "first_name": "first_name_B",
                "last_name": "last_name_B",
                "current_title": "Data Scientist",
                "skills": ["Python", "R", "Machine Learning", "TensorFlow", "Pandas"],
                "years_experience": 3,
                "degree": "Master of Data Science",
                "certifications": ["AWS Certified Machine Learning", "Microsoft Azure Data Scientist"],
            },
        ]
    ]

    print("=== Original Data ===")
    print(input_data[0])

    # Initialize operator
    semantic_project_operator = SemanticProjectOperator()
    properties = semantic_project_operator.properties
    properties['service_url'] = 'ws://localhost:8001'  # update this to your service url

    # Example 1: Just select (keep only specific columns, no renaming)
    print("\n=== Example 1: Just select ===")
    attributes = {"projection_instructions": "Keep columns about name and skills."}

    print(f"Projection Instructions: {attributes['projection_instructions']}")
    result = semantic_project_operator_function(input_data, attributes, properties)
    print("=== Semantic Project RESULT (Example 1) ===")
    print(result)

    # Example 2: Mixture of select and rename
    print("\n=== Example 2: Mixture of select and rename ===")
    attributes = {"projection_instructions": "Help me process the data to get the surname as key \"Name\" and applicants skill-related fields."}

    print(f"Projection Instructions: {attributes['projection_instructions']}")
    result = semantic_project_operator_function(input_data, attributes, properties)
    print("=== Semantic Project RESULT (Example 2) ===")
    print(result)

    # Example 3: Drop only (keep most columns, drop specific ones)
    print("\n=== Example 3: Drop only ===")
    attributes = {"projection_instructions": "Drop all columns about experiences."}

    print(f"Projection Instructions: {attributes['projection_instructions']}")
    result = semantic_project_operator_function(input_data, attributes, properties)
    print("=== Semantic Project RESULT (Example 3) ===")
    print(result)
