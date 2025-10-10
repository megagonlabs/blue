###### Formats
from typing import List, Dict, Any, Callable, Optional

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer
from blue.utils.service_utils import ServiceClient
from blue.properties import PROPERTIES

###############
### Semantic Extract Operator


def semantic_extract_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Extract entities from natural language text fields using LLM models.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) containing records with text fields to extract entities from.
        attributes: Dictionary containing extraction parameters including entities, context, demonstrations, and extract_with_single_prompt.
        properties: Optional properties dictionary containing service configuration. Defaults to None.

    Returns:
        List containing extracted entities for each record in the input data.
    """
    entities = attributes.get('entities', [])
    context = attributes.get('context', '')
    demonstrations = attributes.get('demonstrations', '')
    extract_with_single_prompt = attributes.get('extract_with_single_prompt', True)

    if not input_data or not input_data[0] or not entities:
        return []

    service_client = ServiceClient(name="semantic_extract_operator_service_client", properties=properties)

    results = []
    for data_group in input_data:
        if not data_group:
            results.append([])
            continue

        if extract_with_single_prompt:
            # Extract all entities in a single prompt
            result = _extract_all_entities_single_prompt(data_group, entities, context, demonstrations, service_client, properties)
        else:
            # Extract each entity with individual prompts
            result = _extract_entities_individual_prompts(data_group, entities, context, demonstrations, service_client, properties)

        results.append(result)

    return results


def semantic_extract_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate semantic extract operator attributes.

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

    entities = attributes.get('entities', [])

    if not isinstance(entities, list) or len(entities) == 0:
        return False

    for entity in entities:
        if not isinstance(entity, dict):
            return False
        if 'name' not in entity:
            return False
        if 'description' in entity and not isinstance(entity['description'], str):
            return False
        if 'type' in entity and not isinstance(entity['type'], str):
            return False
        if 'extract_on_fields' in entity:
            if not isinstance(entity['extract_on_fields'], list):
                return False
            if len(entity['extract_on_fields']) == 0:
                return False
    return True


def semantic_extract_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for semantic extract operator execution.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the operation.
    """
    return default_operator_explainer(output, input_data, attributes)


def _extract_all_entities_single_prompt(
    data_group: List[Dict[str, Any]], entities: List[Dict[str, Any]], context: str, demonstrations: str, service_client: ServiceClient, properties: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Extract all entities using a single prompt for each record."""
    results = []

    for record in data_group:
        entity_descriptions = []
        relevant_fields = set()

        for entity in entities:
            name = entity['name']
            description = entity.get('description', f'Extract {name} from the text')
            extract_on_fields = entity.get('extract_on_fields', [])
            entity_type = entity.get('type')

            if entity_type:
                type_info = f" ({entity_type})"
            else:
                type_info = ""

            if extract_on_fields:
                fields = ', '.join(extract_on_fields)
                entity_descriptions.append(f"- {name}{type_info}: {description} (from fields: {fields})")
                relevant_fields.update(extract_on_fields)
            else:
                entity_descriptions.append(f"- {name}{type_info}: {description} (from all fields)")
                relevant_fields.update(record.keys())

        # Create filtered record with only relevant fields
        filtered_record = {field: record[field] for field in relevant_fields if field in record}

        additional_data = {'entities': '\n'.join(entity_descriptions), 'context': context, 'demonstrations': demonstrations, 'data_record': filtered_record}

        result = service_client.execute_api_call({}, properties=properties, additional_data=additional_data)

        if isinstance(result, dict):
            results.append(result)
        else:
            empty_result = {entity['name']: [] for entity in entities}
            results.append(empty_result)

    return results


def _extract_entities_individual_prompts(
    data_group: List[Dict[str, Any]], entities: List[Dict[str, Any]], context: str, demonstrations: str, service_client: ServiceClient, properties: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Extract entities using individual prompts for each entity type."""
    results = []

    for record in data_group:
        extracted_record = {}

        for entity in entities:
            entity_name = entity['name']
            entity_description = entity.get('description', '')
            extract_on_fields = entity.get('extract_on_fields', [])
            entity_type = entity.get('type')

            # If no extract_on_fields specified, use all fields in the record
            if not extract_on_fields:
                extract_on_fields = list(record.keys())

            text_to_extract = []
            for field in extract_on_fields:
                if field in record and record[field]:
                    text_to_extract.append(f"{field}: {record[field]}")

            if not text_to_extract:
                extracted_record[entity_name] = []
                continue

            individual_properties = properties.copy()
            individual_properties['input_template'] = SemanticExtractOperator.INDIVIDUAL_EXTRACT_PROMPT

            if entity_type:
                entity_type_info = f" ({entity_type})"
                type_line = f"\n- **Type**: {entity_type}"
            else:
                entity_type_info = ""
                type_line = ""

            additional_data = {
                'entity_name': entity_name,
                'entity_description': entity_description,
                'entity_type_info': entity_type_info,
                'type_line': type_line,
                'extract_fields': ', '.join(extract_on_fields) if extract_on_fields else 'all fields',
                'context': context,
                'demonstrations': demonstrations,
                'text_to_extract': '\n'.join(text_to_extract),
            }

            entity_result = service_client.execute_api_call({}, properties=individual_properties, additional_data=additional_data)

            if isinstance(entity_result, list):
                extracted_record[entity_name] = entity_result
            else:
                extracted_record[entity_name] = [entity_result] if entity_result else []

        results.append(extracted_record)

    return results


class SemanticExtractOperator(Operator, ServiceClient):
    """
    Semantic extract operator extracts entities from natural language text fields using LLM models.

    Attributes:
    ----------
    | Name                     | Type          | Required | Default | Description                                                                                                                   |
    |--------------------------|---------------|----------|---------|-------------------------------------------------------------------------------------------------------------------------------|
    | `entities`                 | list[dict]    | :fontawesome-solid-circle-check: {.green-check}     | N/A     | List of entities to extract. Each dict has 'name', 'description' (optional), 'extract_on_fields' (optional list of field names - if not provided, extracts from all fields), and 'type' (optional) |
    | `context`                  | str           |     | ""      | Additional context information that provides domain knowledge or additional instructions for the extraction                  |
    | `demonstrations`           | str           |     | ""      | Additional demonstrations to help in-context learning                                                                       |
    | `extract_with_single_prompt` | bool         |     | True    | If true, extract all entities in a single prompt, else extract each entity with individual prompt                             |
    """

    SINGLE_EXTRACT_PROMPT = """## Task
You are given one data record in JSON format. Your job is to extract specific entities from this record and return them in strict JSON format.

## Entities to Extract
${entities}

## Context
${context}

## Demonstrations
${demonstrations}

## Output Requirements
- Return a **single JSON object** as the output.
- The JSON object must contain:
  - Keys: exact entity names from the list above (preserve original case and formatting).
  - Values: arrays of extracted items (may be empty if nothing is found).
- Do not introduce extra keys or change entity names.
- **Deduplication rule (within the same entity key):**
  - Remove duplicates and near-duplicates (e.g., case/spacing/punctuation variants, obvious aliases, or versioned forms).
  - Keep **one canonical value** if there are multiple semantically equivalent values.
  - Example: `"skill": ["python", "python3.10", "Python "]` → `"skill": ["python"]`.
- Only extract entities from the specified fields for each entity name.
- Be precise and only return relevant entities.

## Additional Notes
- If no entities are found, still return an object with all keys mapped to empty arrays.
- Do not include explanations, comments, or text outside the JSON object.
- Validate that the final output is syntactically valid JSON.

---

### Data Record
${data_record}

---

### Output JSON Object
"""

    INDIVIDUAL_EXTRACT_PROMPT = """## Task
You are given text content and need to extract specific entities of type "${entity_name}" from it.

## Entity to Extract
- **Name**: ${entity_name}${entity_type_info}
- **Description**: ${entity_description}
- **Extract from fields**: ${extract_fields}${type_line}

## Context
${context}

## Demonstrations
${demonstrations}

## Output Requirements
- Return a **JSON array** of extracted ${entity_name} entities
- Each element should be a string representing one ${entity_name}
- If no ${entity_name} entities are found, return an empty array []
- Be precise and only extract relevant ${entity_name} entities
- **Deduplication rule:**
  - Remove duplicates and near-duplicates (e.g., case/spacing/punctuation variants, obvious aliases, or versioned forms)
  - Keep **one canonical value** if there are multiple semantically equivalent values
  - Example: `["python", "python3.10", "Python "]` → `["python"]`
- Do not include explanations, comments, or text outside the JSON array
- Validate that the final output is syntactically valid JSON

---

### Text to Extract From
${text_to_extract}

---

### Output JSON Array
"""

    PROPERTIES = {
        # openai related properties
        "openai.api": "ChatCompletion",
        "openai.model": "gpt-4o",
        "openai.stream": False,
        "openai.max_tokens": 4096,
        "openai.temperature": 0,
        # io related properties
        "input_json": "[{\"role\": \"user\"}]",
        "input_context": "$[0]",
        "input_context_field": "content",
        "input_field": "messages",
        "input_template": SINGLE_EXTRACT_PROMPT,
        "output_path": "$.choices[0].message.content",
        # service related properties
        "service_prefix": "openai",
        # output transformations
        "output_transformations": [{"transformation": "replace", "from": "```", "to": ""}, {"transformation": "replace", "from": "json", "to": ""}],
        "output_strip": True,
        "output_cast": "json",
    }

    name = "semantic_extract"
    description = "Extracts entities from natural language text fields using LLM models"
    default_attributes = {
        "entities": {
            "type": "list[dict]",
            "description": "List of entities to extract. Each dict has 'name', 'description' (optional), 'extract_on_fields' (optional list of field names - if not provided, extracts from all fields), and 'type' (optional)",
            "required": True,
        },
        "context": {
            "type": "str",
            "description": "Additional context information that provides domain knowledge or additional instructions for the extraction",
            "required": False,
            "default": "",
        },
        "demonstrations": {"type": "str", "description": "Additional demonstrations to help in-context learning", "required": False, "default": ""},
        "extract_with_single_prompt": {
            "type": "bool",
            "description": "If true, extract all entities in a single prompt, else extract each entity with individual prompt",
            "required": False,
            "default": True,
        },
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=semantic_extract_operator_function,
            description=description or self.description,
            properties=properties,
            validator=semantic_extract_operator_validator,
            explainer=semantic_extract_operator_explainer,
        )

    def _initialize_properties(self):
        super()._initialize_properties()

        # attribute definitions
        self.properties["attributes"] = self.default_attributes

        # service_url, set as default
        self.properties["service_url"] = PROPERTIES["services.openai.service_url"]


if __name__ == "__main__":
    ## calling example

    # Example data for testing
    input_data = [
        [
            {
                "job_id": 1,
                "job_title": "Senior Full Stack Developer",
                "job_description": "We are seeking a senior full stack developer with 5+ years of experience in React, Node.js, Python, and PostgreSQL. Must have experience with AWS, Docker, and CI/CD pipelines. Knowledge of TypeScript and GraphQL is preferred.",
                "location": "location A",
                "company": "company A",
                "salary_range": "salary range A",
            },
            {
                "job_id": 2,
                "job_title": "Machine Learning Engineer",
                "job_description": "Looking for an ML engineer with expertise in Python, TensorFlow, PyTorch, and scikit-learn. Must have 3+ years of experience with data pipelines, Apache Spark, and cloud platforms. PhD in Computer Science or related field preferred.",
                "location": "location B",
                "company": "company B",
                "salary_range": "salary range B",
            },
        ]
    ]

    # Define entities to extract
    entities = [
        {"name": "programming_languages", "description": "Programming languages and frameworks mentioned in the job description", "extract_on_fields": ["job_description"]},
        {"name": "experience_years", "description": "Years of experience requirements mentioned", "type": "int", "extract_on_fields": ["job_description"]},
        {"name": "skills", "description": "Technologies, tools, and platforms mentioned", "extract_on_fields": ["job_description", "job_title"]},
        {"name": "education_qualifications", "description": "Educational requirements and qualifications mentioned", "extract_on_fields": ["job_description"]},
    ]

    print(f"=== Semantic Extract attributes ===")
    print(entities)

    semantic_extract_operator = SemanticExtractOperator()
    properties = semantic_extract_operator.properties
    print(f"=== Semantic Extract PROPERTIES ===")
    print(properties)
    properties['service_url'] = 'ws://localhost:8001'  # update this to your service url

    # Example 1: Single prompt extraction
    print("=== Example 1: Single prompt based extraction ===")
    attributes_single = {"entities": entities, "context": "", "extract_with_single_prompt": True}
    result = semantic_extract_operator_function(input_data, attributes_single, properties)
    print("=== Semantic Extract RESULT (single prompt) ===")
    print(result)

    # Example 2: Individual prompts extraction
    print("=== Example 2: Individual prompts based extraction ===")
    attributes_individual = {"entities": entities, "context": None, "demonstrations": None, "extract_with_single_prompt": False}
    result = semantic_extract_operator_function(input_data, attributes_individual, properties)
    print("=== Semantic Extract RESULT (individual prompts) ===")
    print(result)
