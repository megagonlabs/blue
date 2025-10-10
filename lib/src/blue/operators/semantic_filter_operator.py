###### Formats
from typing import List, Dict, Any, Callable, Optional

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer
from blue.utils.service_utils import ServiceClient
from blue.properties import PROPERTIES

###############
### Semantic Filter Operator


def semantic_filter_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Filter records based on natural language conditions using LLM models.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) containing records to filter.
        attributes: Dictionary containing filtering parameters including filter_conditions, context, demonstrations, and return_idx.
        properties: Optional properties dictionary containing service configuration. Defaults to None.

    Returns:
        List containing filtered records or indices based on return_idx setting.
    """
    filter_conditions = attributes.get('filter_conditions', {})
    context = attributes.get('context', '')
    demonstrations = attributes.get('demonstrations', '')
    return_idx = attributes.get('return_idx', False)

    if not input_data or not input_data[0] or not filter_conditions:
        return []

    service_client = ServiceClient(name="semantic_filter_operator_service_client", properties=properties)

    results = []
    for data_group in input_data:
        if not data_group:
            results.append([])
            continue

        result = _filter_records_with_conditions(data_group, filter_conditions, context, demonstrations, return_idx, service_client, properties)
        results.append(result)

    return results


def semantic_filter_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate semantic filter operator attributes.

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

    filter_conditions = attributes.get('filter_conditions', {})

    if not isinstance(filter_conditions, dict):
        return False

    if len(filter_conditions) == 0:
        return False

    for key, value in filter_conditions.items():
        if not isinstance(key, str) or not isinstance(value, str):
            return False
        if not key.strip() or not value.strip():
            return False

    return True


def semantic_filter_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for semantic filter operator execution.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the operation.
    """
    return default_operator_explainer(output, input_data, attributes)


def _filter_records_with_conditions(
    data_group: List[Dict[str, Any]], filter_conditions: Dict[str, str], context: str, demonstrations: str, return_idx: bool, service_client: ServiceClient, properties: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Filter records using LLM-based semantic filtering"""
    filtered_records = []
    filtered_indices = []

    for idx, record in enumerate(data_group):
        conditions_text = []
        for i, (field, condition) in enumerate(filter_conditions.items(), 1):
            if field in record:
                field_value = record[field]
                conditions_text.append(f"{i}. Field '{field}' (value: {field_value}) should satisfy: {condition}")
            else:
                conditions_text.append(f"{i}. Field '{field}' (not present in record) should satisfy: {condition}")

        additional_data = {'record': record, 'conditions': '\n'.join(conditions_text), 'context': context, 'demonstrations': demonstrations}

        result = service_client.execute_api_call({}, properties=properties, additional_data=additional_data)

        # Convert string results to proper boolean
        if isinstance(result, str):
            result = result.lower().strip() in ['true', 'yes', '1', 'include']
        elif not isinstance(result, bool):
            result = bool(result)

        if result:
            filtered_records.append(record)
            filtered_indices.append(idx)

    if return_idx:
        return [{'indices': filtered_indices}]
    else:
        return filtered_records


class SemanticFilterOperator(Operator, ServiceClient):
    """
    Semantic filter operator filters records based on natural language conditions using LLM models.
    It evaluates each record against the provided conditions and returns those that satisfy all conditions.

    Attributes:
    ----------
    | Name               | Type            | Required | Default | Description                                                                 |
    |-------------------|----------------|----------|---------|-----------------------------------------------------------------------------|
    | `filter_conditions`  | dict[str, str]  | :fontawesome-solid-circle-check: {.green-check}     | -       | Dictionary mapping field names to natural language filter conditions       |
    | `context`            | str             |     | ""      | Optional context to provide domain knowledge or additional instructions    |
    | `demonstrations`     | str             |     | ""      | Optional demonstrations to help in-context learning                        |
    | `return_idx`         | boolean         |     | False   | If true, return indices of records that satisfy all conditions, else return filtered records |

    """

    FILTER_PROMPT = """## Task
You are given a data record and natural language filter conditions. Your job is to determine if the record should be included in the filtered results.

## Record to Evaluate
${record}

## Filter Conditions
${conditions}

## Context
${context}

## Demonstrations
${demonstrations}

## Output Requirements
- Return **only a boolean value**: true or false
- Return **true** if the record satisfies ALL the filter conditions
- Return **false** if the record does NOT satisfy any of the filter conditions
- Be precise in your evaluation based on the natural language conditions
- Consider the semantic meaning of the conditions, not just exact text matching

## Additional Notes
- If a field is not present in the record, evaluate the condition as if the field has no value
- Use your understanding of natural language to interpret conditions.
- Return only the boolean result, no explanations or additional text

---

### Output
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
        "input_template": FILTER_PROMPT,
        "output_path": "$.choices[0].message.content",
        # service related properties
        "service_prefix": "openai",
        # output transformations
        "output_transformations": [{"transformation": "replace", "from": "```", "to": ""}, {"transformation": "replace", "from": "json", "to": ""}],
        "output_strip": True,
        "output_cast": "bool",
    }

    name = "semantic_filter"
    description = "Filters records based on natural language conditions using LLM models"
    default_attributes = {
        "filter_conditions": {"type": "dict[str, str]", "description": "Dictionary mapping field names to natural language filter conditions", "required": True},
        "context": {"type": "str", "description": "Optional context to provide domain knowledge or additional instructions", "required": False, "default": ""},
        "demonstrations": {"type": "str", "description": "Optional demonstrations to help in-context learning", "required": False, "default": ""},
        "return_idx": {"type": "boolean", "description": "If true, return indices of records that satisfy all conditions, else return filtered records", "required": False, "default": False},
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=semantic_filter_operator_function,
            description=description or self.description,
            properties=properties,
            validator=semantic_filter_operator_validator,
            explainer=semantic_filter_operator_explainer,
        )

    def _initialize_properties(self):
        super()._initialize_properties()
        self.properties["attributes"] = self.default_attributes

        # service_url, set as default
        self.properties["service_url"] = PROPERTIES["services.openai.service_url"]


if __name__ == "__main__":
    ## calling example

    # Test data - applicant records
    input_data = [
        [
            {"name": "Applicant A", "skills": ["Spring Framework", "Gradle", "SQL"], "experience_years": 5, "current_title": "Frontend Developer"},
            {"name": "Applicant B", "skills": ["Java", "React"], "experience_years": 2, "current_title": "Junior Software Engineer"},
            {"name": "Applicant C", "skills": ["Java", "Spring", "Docker"], "experience_years": 7},
            {"name": "Applicant D", "skills": ["Python", "Java systems", "SQL"], "experience_years": 8, "current_title": "Senior Software Engineer"},
            {"name": "Applicant E", "skills": ["JUnit", "JVM"], "experience_years": 5, "current_title": "Coder"},
        ]
    ]

    print(f"=== Semantic Filter attributes ===")

    # just used to get the default properties
    semantic_filter_operator = SemanticFilterOperator()
    properties = semantic_filter_operator.properties
    print(f"=== Semantic Filter PROPERTIES ===")
    print(properties)
    properties['service_url'] = 'ws://localhost:8001'  # update this to your service url

    # call the function
    # Example 1: return filtered records
    filter_conditions = {"skills": "contains relevant skill(s) about Java", "experience_years": "at least 5", "current_title": "not empty"}
    print(filter_conditions)
    attributes = {
        "filter_conditions": filter_conditions,
        "context": "The **relevant skills**  in the conditions are skills that have high correlation with the target skill.",
        "return_idx": False,
    }
    print(attributes)
    result = semantic_filter_operator_function(input_data, attributes, properties)
    print("=== Semantic Filter RESULT (return_idx=False)===")
    print(result)

    # Example 2: return indices of filtered records
    attributes['return_idx'] = True
    attributes['context'] = "The **relevant skills**  in the conditions are defined as those if knowledge of it, there is a high probability that the target skill is also known."
    print(attributes)
    result = semantic_filter_operator.function(input_data, attributes, properties)
    print("=== Semantic Filter RESULT (return_idx=True)===")
    print(result)
