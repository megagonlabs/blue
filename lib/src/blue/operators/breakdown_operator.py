###### Formats
from typing import List, Dict, Any, Callable, Optional

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer
from blue.utils.service_utils import ServiceClient

###############
### Breakdown Operator


def breakdown_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Process natural language query using LLM models and subsqueries along with metadata"""
    # Extract attributes
    query = attributes.get('query', '')
    context = attributes.get('context', '')
    num_alternatives = attributes.get('num_alternatives', 1)
    schema = attributes.get('schema', '')

    # Validate input
    if not query or not query.strip():
        return []

    service_client = ServiceClient(name="breakdown_operator_service_client", properties=properties)
    additional_data = {'query': query, 'context': context, 'num_alternatives': num_alternatives, 'schema': schema}

    return service_client.execute_api_call({}, properties=properties, additional_data=additional_data)


def breakdown_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate breakdown operator attributes."""
    return default_operator_validator(input_data, attributes, properties)


def breakdown_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Explain breakdown operator output. Currently only returns attributes and output"""
    breakdown_explanation = {
        'output': output,
        "attributes": attributes,
    }
    return breakdown_explanation


class BreakdownOperator(Operator, ServiceClient):
    PROMPT = """
Your task is to process a natural language query, and break it down to its subqueries. To do so, translate the natural language query into SQL, 
defining each subquery as common table expressions (CTE). Return the results in JSON format.
The response should be a valid JSON array containing the following information for each CTE:
- 'name': name of the CTE
- 'description': natural language description of the CTE, representing the subquery
- 'sql': sql statement corresponding to the CTE
- 'table':  name of the CTE table
- 'columns': a list of columns of the table
- 'dependency': a list of dependent tables, defined as CTE.


Here are additional requirements:
- Generate {num_alternatives} number of alternatives
- The output should be a JSON array, each containing an alternative set of CTEs matching the natural language query.
- There might be optional context provided. Use it to assist the query if provided.
- There might be specificed schema, whenever possible try to match it.
- Each object should contain the requested information in a structured format
- Please try to return non-empty output. If the query is not clear, please use your best judgement to return a non-empty output.
- The response should be well-formatted and easy to parse.
- Output the JSON directly. Do not generate explanation or other additional output.

Query:
${query}

Schema:
${schema}

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

    name = "breakdown"
    description = "Processes natural language query and break it down to subqueries using common table expressions"
    default_attributes = {
        "query": {"type": "str", "description": "Natural language query to process", "required": True},
        "context": {"type": "str", "description": "Optional context to provide domain knowledge", "required": False, "default": ""},
        "schema": {"type": "str", "description": "Optional schema to match", "required": False, "default": []},
        "num_alternatives": {"type": "int", "description": "Optional number of alternatives to generate", "required": False, "default": 1},
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=breakdown_operator_function,
            description=description or self.description,
            properties=properties or self.PROPERTIES,
            validator=breakdown_operator_validator,
            explainer=breakdown_operator_explainer,
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
        "query": "what are the top skills required for the most frequently advertised manager role in jurong?",
        "context": "Consider a job database in an HR company",
        "schema": "",
        "num_alternatives": 3,
    }
    print(f"=== breakdown attributes ===")
    print(attributes)

    # just used to get the default properties
    breakdown_operator = BreakdownOperator()
    properties = breakdown_operator.properties
    print(f"=== breakdown PROPERTIES ===")
    print(properties)
    properties['service_url'] = 'ws://localhost:8001'  # update this to your service url
    result = breakdown_operator.function(input_data, attributes, properties)
    print("=== breakdown RESULT ===")
    print(result)
