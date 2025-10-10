###### Formats
from typing import List, Dict, Any, Callable, Optional

import traceback
import logging

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer
from blue.utils.service_utils import ServiceClient
from blue.properties import PROPERTIES

###############
### Query Breakdown Operator


def query_breakdown_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """
    Process natural language query using LLM models, identifies subsqueries along with metadata such as sql, columns, dependencies, and generality of the subquery.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]), passes through unchanged.
        attributes: Dictionary containing query breakdown parameters including query, context, num_alternatives, and schema.
        properties: Optional properties dictionary containing service client information. Defaults to None.

    Returns:
        List containing the output of the query breakdown execution.
    """
    # Extract attributes
    query = attributes.get('query', '')
    context = attributes.get('context', '')
    num_alternatives = attributes.get('num_alternatives', 1)
    schema = attributes.get('schema', '')

    # Validate input
    if not query or not query.strip():
        return []

    service_client = ServiceClient(name="query_breakdown_operator_service_client", properties=properties)
    additional_data = {'query': query, 'context': context, 'num_alternatives': num_alternatives, 'schema': schema}

    results = service_client.execute_api_call({}, properties=properties, additional_data=additional_data)
    return results


def query_breakdown_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """
    Validate query breakdown operator attributes.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) to validate.
        attributes: Dictionary containing operator attributes to validate.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        True if attributes are valid, False otherwise."""
    return default_operator_validator(input_data, attributes, properties)


def query_breakdown_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """
    Explain query breakdown operator output. Currently only returns attributes and output.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the operation."""
    query_breakdown_explanation = {
        'output': output,
        "attributes": attributes,
    }
    return query_breakdown_explanation


class QueryBreakdownOperator(Operator, ServiceClient):
    """Query Breakdown Operator

    This operator processes a natural language query and breaks it down into subqueries using common table expressions (CTEs).
    It leverages LLM models to generate SQL statements, descriptions, columns, dependencies, and generality scores for each subquery.

    Attributes:
    ----------
    | Name             | Type | Required | Default | Description                                      |
    |-----------------|------|----------|---------|--------------------------------------------------|
    | `query`           | str  | :fontawesome-solid-circle-check: {.green-check}     | -       | Natural language query to process               |
    | `context`         | str  |     | ""      | Optional context to provide domain knowledge    |
    | `schema`          | str  |     | []      | Optional schema to match                        |
    | `num_alternatives` | int  |     | 1       | Optional number of alternatives to generate     |

    """

    PROMPT = """
Your task is to process a natural language query, and break it down to its subqueries.  
Your strategy is to translate the natural language query into SQL, defining each subquery as common table expressions (CTE):
* Each subquery should be sufficiently self-contained and independent in terms of specific data to retrieve. 
* Break down into as many subsqueries as necessary but don't do excessively. 
* Only last subquery should join all the subqueries to answer the natural language query. Return the results in JSON format.

Return the results in JSON format.
The response should be a valid JSON array containing the following information for each CTE:
- 'description': natural language description of the CTE, representing the subquery
- 'sql': sql statement corresponding to the CTE
- 'table':  name of the CTE table, use short generic table names 
- 'columns': a list of columns of the table, each with a name and type (suitable for sql)
- 'dependency': a list of dependent tables names, as defined in respective CTEs
- 'generality': score of 0 to 10, where a score of 10 indicating whether the subquery can be completed answered through public general knowledge sources and a score of 0 indicating subquery can only be answered through private data sources

Here are additional requirements:
- Create a total of ${num_alternatives} alternatives.
- The output should be a JSON array, each containing an alternative set of CTEs. 
- Each alternative set of CTE should be in a JSON array with each CTE as a JSON object in the array.
- As such the overall output should be a JSON array of JSON arrays each representing an alternative set. The second level of JSONArray contains JSON objects.
- Output should not be 3 levels of JSON Arrays. 
- Avoid using IN within a CTE. Instead breakdown further and create another CTE and have another CTE finally that uses JOIN to put the subqueries together. 
- Dependency field should only contain table names defined in other CTEs.
- Use columns with ids sparingly. When joining especially different tables use columns that have values instead of ids.
- There might be optional context provided. Use it to assist the query if provided.
- There might be specificed schema, whenever possible try to match it.
- Each object should contain the requested information in a structured format
- Please try to return non-empty output. If the query is not clear, please use your best judgement to return a non-empty output.
- The response should be well-formatted and easy to parse.
- Output the JSON directly. Do not generate explanation or other additional output.

Below is an example: 
Query: 
what jobs are available for data scientists in bay area? 

Output: 
[[{"description":"Retrieve all jobs for data scientist roles","sql":"SELECT job_title, company_name, location FROM jobs WHERE LOWER(job_title) LIKE '%data scientist%'","table":"ds_roles","columns":[{"name":"job_title","type":"VARCHAR"},{"name":"company_name","type":"VARCHAR"},{"name":"location","type":"VARCHAR"}],"dependency":[],"generality":3},{"description":"Retrieve locations that are considered part of the Bay Area","sql":"SELECT city FROM locations WHERE city IN ('San Francisco', 'San Jose', 'Oakland', 'Palo Alto', 'Mountain View', 'Sunnyvale', 'Berkeley')","table":"bay_locs","columns":[{"name":"city","type":"VARCHAR"}],"dependency":[],"generality":8},{"description":"Join data scientist job listings with Bay Area locations to find available data scientist jobs in the Bay Area","sql":"SELECT d.job_title, d.company_name, d.location FROM ds_roles d JOIN bay_locs b ON LOWER(d.location) = LOWER(b.city)","table":"ds_jobs_bayarea","columns":[{"name":"job_title","type":"VARCHAR"},{"name":"company_name","type":"VARCHAR"},{"name":"location","type":"VARCHAR"}],"dependency":["ds_roles","bay_locs"],"generality":2}]]

Below is Your task:

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
        # "openai.model": "gpt-4o",
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

    name = "query_breakdown"
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
            function=query_breakdown_operator_function,
            description=description or self.description,
            properties=properties,
            validator=query_breakdown_operator_validator,
            explainer=query_breakdown_operator_explainer,
        )

    def _initialize_properties(self):
        super()._initialize_properties()

        # attribute definitions
        self.properties["attributes"] = self.default_attributes

        # service_url, set as default
        self.properties["service_url"] = PROPERTIES["services.openai.service_url"]


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
    query_breakdown_operator = QueryBreakdownOperator()
    properties = query_breakdown_operator.properties
    print(f"=== query breakdown PROPERTIES ===")
    print(properties)
    properties['service_url'] = 'ws://localhost:8001'  # update this to your service url
    result = query_breakdown_operator.function(input_data, attributes, properties)
    print("=== query breakdown RESULT ===")
    print(result)
