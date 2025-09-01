###### Formats
from typing import List, Dict, Any, Callable, Optional

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer
from blue.utils.service_utils import ServiceClient

###############
### NL2LLM Operator


def nl2llm_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Process natural language query using LLM models and return structured data"""
    # Extract attributes
    query = attributes.get('query', '')
    context = attributes.get('context', '')
    attr_names = attributes.get('attr_names', [])

    # Validate input
    if not query or not query.strip():
        return []

    # Option 1: if we input the NL2LLMOperator or ServiceClient in someway into this function, we can directly use call the service client to execute the query
    # currently we use option 2

    # Option 2: Otherwise, we create a service client here
    service_client = ServiceClient(name="nl2llm_operator_service_client", properties=properties)
    additional_data = {'query': query, 'context': context, 'attr_names': attr_names}

    return [service_client.execute_api_call({}, properties=properties, additional_data=additional_data)]


def nl2llm_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate nl2llm operator attributes."""
    return default_operator_validator(input_data, attributes, properties)


def nl2llm_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Explain nl2llm operator output. Currently only returns attributes and output"""
    nl2llm_explanation = {
        'output': output,
        "attributes": attributes,
    }
    return nl2llm_explanation


class NL2LLMOperator(Operator, ServiceClient):
    PROMPT = """
Your task is to process a natural language query and return the results in JSON format.
The response should be a valid JSON array containing the requested information.

Here are the requirements:
- There might be optional context provided for domain knowledge. Use it to assist the query if provided and not empty.
- There might be specificed attr_names, which are the attributes of the objects in the output.
- The output should be a JSON array of objects. Each element is a JSON object with proper attribute value pairs.
- Each object should contain the requested information in a structured format
- When interpreting the query, use additional context provided if provided and not empty.
- Please try to return non-empty output. If the query is not clear, please use your best judgement to return a non-empty output.
- The response should be well-formatted and easy to parse
- Output the JSON directly. Do not generate explanation or other additional output.

Query: ${query}

Attr_names:
${attr_names}

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
        "attr_names": {"type": "list[str]", "description": "Optional list of attribute names for the output objects", "required": False, "default": []},
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=nl2llm_operator_function,
            description=description or self.description,
            properties=properties or self.PROPERTIES,
            validator=nl2llm_operator_validator,
            explainer=nl2llm_operator_explainer,
        )

    def _initialize_properties(self):
        super()._initialize_properties()

        # attribute definitions
        self.properties["attributes"] = self.default_attributes


if __name__ == "__main__":
    ## calling example

    # Test data - natural language query
    input_data = [[]]  # empty input data for query type data operator
    attributes = {
        "query": "What are the top 5 programming languages in 2024?",
        "context": "Focus on popularity and job market demand",
        # "attr_names": ["language", "popularity_rank", "description"],
        "attr_names": ["language", "year"],
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
    # Option 1: directly call the nl2llm_operator_function
    result = nl2llm_operator_function(input_data, attributes, properties)
    print("=== NL2LLM RESULT (Option 1)===")
    print(result)
    # Option 2: use the function method
    attributes['attr_names'] = ["language", "popularity_rank", "description", "latest_release_date"]
    result = nl2llm_operator.function(input_data, attributes, properties)
    print("=== NL2LLM RESULT (Option 2)===")
    print(result)
