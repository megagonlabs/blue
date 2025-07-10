###### Formats
from typing import List, Dict, Any, Callable, Optional

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer
from blue.utils.service_utils import ServiceClient

###############
### NL2LLM Operator


def nl2llm_operator_function(input_data: List[List[Dict[str, Any]]], params: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Process natural language query using LLM models and return structured data"""
    # Extract parameters
    query = params.get('query', '')
    context = params.get('context', '')
    attr_names = params.get('attr_names', [])

    # Validate input
    if not query or not query.strip():
        return []

    # Option 1: if we input the NL2LLMOperator or ServiceClient in someway into this function, we can directly use call the service client to execute the query
    # currently we use option 2

    # Option 2: Otherwise, we create a service client here
    # Create service client for OpenAI calls, use input properties of the function
    service_client = ServiceClient(name="nl2llm_operator_service_client", properties=properties)
    return [service_client.execute_api_call(query, properties=service_client.properties, additional_data={'context': context, 'attr_names': attr_names})]


def nl2llm_operator_validator(params: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate nl2llm operator parameters."""
    return default_operator_validator(params, properties)


def nl2llm_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], params: Dict[str, Any]) -> Dict[str, Any]:
    """Explain nl2llm operator output. Currently only returns parameters and output"""
    nl2llm_explanation = {
        'output': output,
        "parameters": params,
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

Query: ${input}

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
        # io related properties (used by requestor operator)
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
    default_parameters = {
        "query": {"type": "str", "description": "Natural language query to process", "required": True},
        "context": {"type": "str", "description": "Optional context to provide domain knowledge", "required": False, "default": ""},
        "attr_names": {"type": "list[str]", "description": "Optional list of attribute names for the output objects", "required": False, "default": []},
    }

    def __init__(self, name: str = "nl2llm", description: str = None, properties: Dict[str, Any] = None, function: Callable = None, validator: Callable = None, explainer: Callable = None):
        if description is None:
            description = self.description

        if properties is None:
            properties = {}
        if "parameters" not in properties:
            properties["parameters"] = self.default_parameters
        if function is None:
            function = nl2llm_operator_function
        if validator is None:
            validator = nl2llm_operator_validator
        if explainer is None:
            explainer = nl2llm_operator_explainer

        super().__init__(
            name=name,
            description=description,
            properties=properties,
            function=function,
            validator=validator,
            explainer=explainer,
        )

    def _initialize_properties(self):
        super()._initialize_properties()  # get default properties for Operator
        self.properties.update(self.PROPERTIES)  # update with NL2LLM specific properties


if __name__ == "__main__":
    ## calling example

    # Test data - natural language query
    input_data = [[]]  # empty input data for query type data operator
    params = {
        "query": "What are the top 5 programming languages in 2024?",
        "context": "Focus on popularity and job market demand",
        "attr_names": ["language", "popularity_rank", "description"],
    }
    print(f"=== NL2LLM PARAMETERS ===")
    print(params)

    # just used to get the default properties
    nl2llm_operator = NL2LLMOperator(properties=params)
    properties = nl2llm_operator.properties
    print(f"=== NL2LLM PROPERTIES ===")
    print(properties)
    properties['service_url'] = 'ws://<your_service_url>:8001'  # please change this to your service url

    # call the function
    result = nl2llm_operator.function(input_data, params, properties)
    print("=== NL2LLM RESULT ===")
    print(result)
