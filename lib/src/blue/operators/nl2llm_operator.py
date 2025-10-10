###### Formats
from typing import List, Dict, Any, Callable, Optional

import traceback
import logging

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer
from blue.utils.service_utils import ServiceClient
from blue.properties import PROPERTIES

###############
### NL2LLM Operator


def nl2llm_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Process natural language query using LLM models and return structured data.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]), not used for query processing.
        attributes: Dictionary containing query parameters including query, context, and attrs.
        properties: Optional properties dictionary containing service configuration. Defaults to None.

    Returns:
        List containing structured data results from the natural language query.
    """
    # Extract attributes
    query = attributes.get('query', '')
    context = attributes.get('context', '')
    attrs = attributes.get('attrs', [])

    if not query or not query.strip():
        return []

    # create attrs section in the prompt
    attrs_formatted = ""
    if attrs:
        attrs_formatted = "Required output attributes:\n"
        for attr in attrs:
            if 'type' in attr:
                attrs_formatted += f"- {attr['name']}: {attr['type']}\n"
            else:
                attrs_formatted += f"- {attr['name']}: (type will be inferred)\n"

    service_client = ServiceClient(name="nl2llm_operator_service_client", properties=properties)
    additional_data = {'query': query, 'context': context, 'attrs': attrs_formatted}

    return [service_client.execute_api_call({}, properties=properties, additional_data=additional_data)]


def nl2llm_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate nl2llm operator attributes.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) to validate.
        attributes: Dictionary containing operator attributes to validate.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        True if attributes are valid, False otherwise.
    """
    if not default_operator_validator(input_data, attributes, properties):
        return False

    # if attrs is provided, validate each element is a dict with 'name' key
    if 'attrs' in attributes and attributes['attrs']:
        for attr in attributes['attrs']:
            if not isinstance(attr, dict) or 'name' not in attr:
                return False
    return True


def nl2llm_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for nl2llm operator execution.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the operation.
    """
    return {
        'output': output,
        "attributes": attributes,
    }


class NL2LLMOperator(Operator, ServiceClient):
    """
    NL2LLM operator processes natural language query using LLM models and returns structured data.

    Attributes:
    ----------
    | Name    | Type       | Required | Default | Description                                               |
    |---------|------------|----------|---------|-----------------------------------------------------------|
    | `query`   | str        | :fontawesome-solid-circle-check: {.green-check}      | -       | Natural language query to process                         |
    | `context` | str        |        | ""      | Optional context to provide domain knowledge             |
    | `attrs`   | list[dict] |        | []      | List of attribute specifications (dicts with name and optional type) |

    """

    PROMPT = """
You are an intelligent system that converts a natural language query into a structured JSON output.

### General Requirements:
- Always output a **valid JSON array** of objects.
- Each element must be a well-formed JSON object with key–value pairs.
- Do **not** include explanations, comments, or additional text outside of the JSON.
- Strive to return non-empty output. If the query is vague, use best judgement to produce a meaningful result.

### Attributes:
- If output attributes are specified, every object must include them.
- If types are specified, ensure values match those types exactly (e.g., string, int, float, boolean, date, list, dict, etc.).
- If types are **not** specified, infer them reasonably from the query and context.
- If no attributes are provided, return the most relevant structured JSON representation of the query.

### Context:
- Use the provided context if it exists and is non-empty.

### Output Formatting:
- Return only the JSON array.
- No prose, explanations, or formatting (such as Markdown fences).
- Ensure strict JSON compliance (no trailing commas, keys quoted, etc.).

---

Query: ${query}

Attributes:
${attrs}

Context:
${context}

Output:
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
        "input_template": PROMPT,
        "output_path": "$.choices[0].message.content",
        # service related properties
        "service_prefix": "openai",
        # output transformations
        "output_transformations": [{"transformation": "replace", "from": "```", "to": ""}, {"transformation": "replace", "from": "json", "to": ""}],
        "output_strip": True,
        "output_cast": "json",
    }

    name = "nl2llm"
    description = "Processes natural language query using LLM models and returns structured data"
    default_attributes = {
        "query": {"type": "str", "description": "Natural language query to process", "required": True},
        "context": {"type": "str", "description": "Optional context to provide domain knowledge", "required": False, "default": ""},
        "attrs": {"type": "list[dict]", "description": "List of attribute specifications (dicts with name and optional type)", "required": False, "default": []},
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=nl2llm_operator_function,
            description=description or self.description,
            properties=properties,
            validator=nl2llm_operator_validator,
            explainer=nl2llm_operator_explainer,
        )

    def _initialize_properties(self):
        super()._initialize_properties()

        # attribute definitions
        self.properties["attributes"] = self.default_attributes

        # service_url, set as default
        self.properties["service_url"] = PROPERTIES["services.openai.service_url"]


if __name__ == "__main__":
    ## calling example

    input_data = [[]]  # empty input data for query type data operator
    attributes = {
        "query": "What are the top 5 programming languages in 2024?",
        "context": "Focus on popularity and job market demand",
        "attrs": [
            {"name": "language", "type": "string"},
            {"name": "popularity_rank", "type": "int"},
            {"name": "latest_release_date", "type": "date"},
            {"name": "most_similar_3_languages"},
            {"name": "description"},
        ],
    }
    print(f"=== NL2LLM attributes ===")
    print(attributes)

    # just used to get the default properties
    nl2llm_operator = NL2LLMOperator()
    properties = nl2llm_operator.properties
    print(f"=== NL2LLM PROPERTIES ===")
    print(properties)
    properties['service_url'] = 'ws://localhost:8001'  # update this to your service url

    # call the function
    result = nl2llm_operator_function(input_data, attributes, properties)
    print("=== NL2LLM RESULT ===")
    print(result)

    # attributes without types
    attributes = {
        "query": "What are the top 5 programming languages in 2024?",
        "context": "Focus on popularity and job market demand",
        "attrs": [{"name": "language"}, {"name": "popularity_rank"}, {"name": "latest_release_date"}, {"name": "most_similar_3_languages"}, {"name": "description"}],
    }
    print(f"=== NL2LLM attributes ===")
    print(attributes)
    result = nl2llm_operator_function(input_data, attributes, properties)
    print("=== NL2LLM RESULT ===")
    print(result)
