###### Formats
import json
import copy
from typing import List, Dict, Any, Callable, Optional

import traceback
import logging

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer
from blue.utils.service_utils import ServiceClient
from blue.data.registry import DataRegistry
from blue.properties import PROPERTIES
from blue.blueerror import BlueError

###############
### NL2BN Operator


def nl2bn_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Translate natural language questions into Bayesian Network queries using LLM models.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]), not used for query processing.
        attributes: Dictionary containing query parameters including question, source, database, collection, and other BN query generation settings.
        properties: Optional properties dictionary containing service configuration and data registry information. Defaults to None.

    Returns:
        List containing BN query results or the generated BN query if execution is disabled.
    """
    question = attributes.get('question', '')
    source = attributes.get('source', '')
    database = attributes.get('database', 'default')
    collection = attributes.get('collection', '')
    protocol_variant = attributes.get('protocol_variant', 'pgmpy')
    context = attributes.get('context', '')
    provided_schema = attributes.get('schema', '')
    explanation = attributes.get('explanation', True)
    structured_explanation = attributes.get('structured_explanation', False)
    max_corrections = attributes.get('max_corrections', 2)
    max_num_paths = attributes.get('max_num_paths', 50)

    if not question or not question.strip():
        return [[]]

    if not source or not database or not collection or not protocol_variant:
        raise ValueError("Source, database, collection, and protocol_variant are required")
    
    if protocol_variant not in ['pgmpy']:
        raise ValueError(f"Unsupported protocol_variant: {protocol_variant}. Supported variants: ['pgmpy']")

    data_registry = _get_data_registry_from_properties(properties)
    if not data_registry:
        return [[]]

    # Unified schema/graph_structure handling
    schema_dict = None
    graph_structure = None
    is_structured = False
    schema_info = None
    
    if not provided_schema:
        # Get schema from data registry with protocol="bn" to get metadata with graph_structure
        schema_dict = data_registry.get_data_source_schema(source, database, collection, "bn", format="dict")
        # According to registry.py, metadata should be in schema['metadata']
        # But handle both cases: metadata in schema['metadata'] or schema itself is metadata
        if schema_dict and 'metadata' in schema_dict:
            metadata = schema_dict.get('metadata', {})
            graph_structure = metadata.get('graph_structure', {}) if metadata else {}
        else:
            # Fallback: schema_dict might be the metadata itself (container version difference)
            metadata = schema_dict if schema_dict else {}
            graph_structure = metadata.get('graph_structure', {}) if isinstance(metadata, dict) else {}
        is_structured = bool(graph_structure and 'nodes' in graph_structure and 'edges' in graph_structure)
    else:
        # Parse provided schema
        if isinstance(provided_schema, str):
            try:
                parsed_schema = json.loads(provided_schema)
            except json.JSONDecodeError:
                # Not valid JSON, use as raw string
                schema_info = provided_schema
                is_structured = False
            else:
                # Check if it's structured (has nodes and edges)
                if isinstance(parsed_schema, dict) and 'nodes' in parsed_schema and 'edges' in parsed_schema:
                    graph_structure = parsed_schema
                    is_structured = True
                else:
                    # Not structured, use as raw schema
                    schema_info = json.dumps(parsed_schema, indent=2) if isinstance(parsed_schema, dict) else provided_schema
                    is_structured = False
        else:
            # Schema is already a dict
            if isinstance(provided_schema, dict) and 'nodes' in provided_schema and 'edges' in provided_schema:
                graph_structure = provided_schema
                is_structured = True
            else:
                # Not structured, convert to string
                schema_info = json.dumps(provided_schema, indent=2)
                is_structured = False
    
    if is_structured:
        # Build structured schema section from graph_structure
        schema_info = f"""**Nodes and their states:**

{_extract_nodes_info(graph_structure)}

**Edges** (parent → child relationships):

{_extract_edges_info(graph_structure)}

**Node descriptions:**

{_extract_node_descriptions(graph_structure)}"""
    else:
        # Use raw schema (or schema_dict if from registry)
        if not schema_info:
            schema_info = json.dumps(schema_dict, indent=2) if schema_dict else ""
        schema_info = f"""**Bayesian Network Schema:**

{schema_info}"""

    service_client = ServiceClient(name="nl2bn_operator_service_client", properties=properties)

    additional_data = {
        'question': question,
        'context': context,
        'schema_section': schema_info,
    }
    
    # Execute API call and handle JSON parsing errors as validation errors
    bn_query_data = None
    validation_errors = []
    
    try:
        bn_query_result = service_client.execute_api_call({}, properties=properties, additional_data=additional_data)
        
        # Parse the result to get the query
        if isinstance(bn_query_result, str):
            try:
                bn_query_data = json.loads(bn_query_result)
            except json.JSONDecodeError as e:
                validation_errors.append(f"Invalid JSON response from LLM: {str(e)}")
                bn_query_data = {}
        elif isinstance(bn_query_result, dict):
            bn_query_data = bn_query_result
        else:
            validation_errors.append(f"Invalid response type from LLM: {type(bn_query_result).__name__}")
            bn_query_data = {}
    except BlueError as e:
        # Handle BlueError from service_utils
        error_str = str(e)
        validation_errors.append(f"Service error: {error_str}")
        bn_query_data = {}
    
    # Validate the query structure
    if not validation_errors:
        if 'target_node' not in bn_query_data:
            validation_errors.append("No target_node found in LLM response")
        if 'target_state' not in bn_query_data:
            validation_errors.append("No target_state found in LLM response")
        if 'context' not in bn_query_data:
            bn_query_data['context'] = {}
    
    # Validate and correct the query against graph_structure
    if is_structured and not validation_errors:
        query_validation_errors = _validate_bn_query(bn_query_data, graph_structure)
        validation_errors.extend(query_validation_errors)
    correction_attempts = 0
    
    while validation_errors and correction_attempts < max_corrections:
        logging.info(f"Query validation found errors (attempt {correction_attempts + 1}): {validation_errors}")
        
        # Ask LLM to correct the query
        correction_data = {
            'question': question,
            'original_query': json.dumps(bn_query_data, indent=2),
            'validation_errors': json.dumps(validation_errors, indent=2),
            'schema_section': schema_info,
        }
        
        # Create properties with correction prompt
        correction_properties = copy.deepcopy(properties) if properties else {}
        correction_properties['input_template'] = NL2BNOperator.CORRECTION_PROMPT
        
        correction_result = service_client.execute_api_call(
            {}, 
            properties=correction_properties, 
            additional_data=correction_data
        )
        
        # Parse corrected query (JSON parsing errors become validation errors)
        if isinstance(correction_result, str):
            try:
                bn_query_data = json.loads(correction_result)
                validation_errors = []
            except json.JSONDecodeError as e:
                validation_errors = [f"Invalid JSON in corrected query: {str(e)}"]
                break
        elif isinstance(correction_result, dict):
            bn_query_data = correction_result
            validation_errors = []
        else:
            validation_errors = [f"Invalid correction response type: {type(correction_result).__name__}"]
            break
        
        # Validate query structure
        if not validation_errors:
            if 'target_node' not in bn_query_data:
                validation_errors.append("No target_node found in corrected query")
            if 'target_state' not in bn_query_data:
                validation_errors.append("No target_state found in corrected query")
            if 'context' not in bn_query_data:
                bn_query_data['context'] = {}
        
        # Validate against graph_structure
        if is_structured and not validation_errors:
            query_validation_errors = _validate_bn_query(bn_query_data, graph_structure)
            validation_errors.extend(query_validation_errors)
        correction_attempts += 1
    
    if validation_errors:
        error_message = f"Query validation failed after {max_corrections} correction attempts. Errors: {', '.join(validation_errors)}"
        logging.error(error_message)
        raise ValueError(error_message)

    # Execute the generated BN query
    query_json = json.dumps(bn_query_data)
    logging.info("Generated BN Query: " + query_json)
    
    # Prepare optional properties for explanation
    optional_properties = {}
    if explanation:
        optional_properties['explanation'] = True
        optional_properties['structured_explanation'] = structured_explanation
        optional_properties['max_num_paths'] = max_num_paths
    
    result = data_registry.execute_query(query_json, source, database, collection, optional_properties=optional_properties)
    logging.debug("Result: ")
    logging.debug(result)
    
    # Format result with probability
    formatted_result = _format_execution_result_format(result)
    
    # Extract probability from result
    prob = None
    explanation_text = None
    if formatted_result and len(formatted_result) > 0 and len(formatted_result[0]) > 0:
        first_result = formatted_result[0][0]
        prob = first_result.get('probability', first_result.get('prob'))
        if explanation:
            explanation_text = first_result.get('explanation', '')
    
    # Build output
    output = {
        "prob": prob,
        "query": bn_query_data
    }
    
    # Add explanation if requested and available
    if explanation and explanation_text:
        output['explanation'] = explanation_text
    
    return [[output]]


def _extract_nodes_info(graph_structure: Dict[str, Any]) -> str:
    """Extract nodes and their states from graph_structure."""
    nodes = graph_structure.get('nodes', {})
    
    nodes_list = []
    for node_name, node_info in nodes.items():
        if isinstance(node_info, dict):
            states = node_info.get('states', [])
            states_str = ', '.join(states) if states else 'N/A'
            nodes_list.append(f"- {node_name}: [{states_str}]")
    
    return '\n'.join(nodes_list) if nodes_list else "No nodes found"


def _extract_edges_info(graph_structure: Dict[str, Any]) -> str:
    """Extract edges (parent -> child) from graph_structure."""
    edges = graph_structure.get('edges', {})
    
    edges_list = []
    for parent, children in edges.items():
        if isinstance(children, list):
            for child in children:
                edges_list.append(f"- {parent} → {child}")
        elif isinstance(children, dict):
            # Handle different edge formats
            for child in children.keys():
                edges_list.append(f"- {parent} → {child}")
    
    return '\n'.join(edges_list) if edges_list else "No edges found"


def _validate_bn_query(bn_query_data: Dict[str, Any], graph_structure: Dict[str, Any]) -> List[str]:
    """Validate BN query against graph_structure.
    
    Parameters:
        bn_query_data: The BN query dictionary with target_node, target_state, and context.
        graph_structure: The graph_structure from metadata containing nodes and edges.
    
    Returns:
        List of validation error messages. Empty list if valid.
    """
    errors = []
    nodes = graph_structure.get('nodes', {})
    
    # Validate target_node
    target_node = bn_query_data.get('target_node')
    if not target_node:
        errors.append("Missing target_node")
    elif target_node not in nodes:
        errors.append(f"Target node '{target_node}' not found in BN.")
    else:
        # Validate target_state
        target_state = bn_query_data.get('target_state')
        if not target_state:
            errors.append("Missing target_state")
        else:
            node_info = nodes[target_node]
            node_states = node_info.get('states', [])
            if target_state not in node_states:
                errors.append(f"Target state '{target_state}' not valid for node '{target_node}'. Valid states: {node_states}")
    
    # Validate context nodes and states
    context = bn_query_data.get('context', {})
    if context:
        for ctx_node, ctx_state in context.items():
            if ctx_node not in nodes:
                errors.append(f"Context node '{ctx_node}' not found in BN.")
            else:
                node_info = nodes[ctx_node]
                node_states = node_info.get('states', [])
                if ctx_state not in node_states:
                    errors.append(f"Context state '{ctx_state}' not valid for node '{ctx_node}'. Valid states: {node_states}")
    
    return errors


def _extract_node_descriptions(graph_structure: Dict[str, Any]) -> str:
    """Extract collection description and node descriptions with state descriptions from graph_structure."""
    descriptions = []
    
    # Collection description from graph_structure top-level
    collection_desc = graph_structure.get('description', '')
    if collection_desc:
        descriptions.append(f"Collection: {collection_desc}")
    
    # Node descriptions from graph_structure
    nodes = graph_structure.get('nodes', {})
    
    node_descriptions = []
    for node_name, node_info in nodes.items():
        if isinstance(node_info, dict):
            node_desc = node_info.get('description', '')
            states_desc = node_info.get('states_description', {})
            
            if node_desc:
                desc_line = f"- {node_name}: {node_desc}"
                # Add state descriptions if available
                if states_desc:
                    state_lines = []
                    for state, state_desc in states_desc.items():
                        if state_desc:  # Only add non-empty state descriptions
                            state_lines.append(f"  - {state}: {state_desc}")
                    if state_lines:
                        desc_line += "\n" + "\n".join(state_lines)
                node_descriptions.append(desc_line)
    
    if node_descriptions:
        descriptions.append("Node descriptions:")
        descriptions.extend(node_descriptions)
    
    return '\n'.join(descriptions) if descriptions else "No descriptions available"


def nl2bn_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate nl2bn operator attributes.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) to validate.
        attributes: Dictionary containing operator attributes to validate.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        True if attributes are valid, False otherwise.
    """
    return default_operator_validator(input_data, attributes, properties)


def nl2bn_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for nl2bn operator execution.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the BN query generation and execution operation.
    """
    nl2bn_explanation = {
        'output': output,
        "attributes": attributes,
    }
    return nl2bn_explanation


class NL2BNOperator(Operator, ServiceClient):
    """
    NL2BN operator translates natural language questions into Bayesian Network queries using LLM models.
    It also executes the generated BN query against the specified BN source and return the probability results and optional explanation.

    Attributes:
    ----------
    | Name                  | Type         | Required | Default   | Description                                                                 |
    |-----------------------|--------------|----------|-----------|-----------------------------------------------------------------------------|
    | `question`            | str          | :fontawesome-solid-circle-check: {.green-check}     |           | Natural language question to translate to BN query                          |
    | `source`              | str          | :fontawesome-solid-circle-check: {.green-check}     | ""        | BN data source name                                                         |
    | `database`            | str          | :fontawesome-solid-circle-check: {.green-check}     | "default" | Database name                                                               |
    | `collection`          | str          | :fontawesome-solid-circle-check: {.green-check}     | ""        | Collection/model name                                                       |
    | `protocol_variant`    | str          | :fontawesome-solid-circle-check: {.green-check}     | "pgmpy"   | Protocol variant (one of ['pgmpy'])                                         |
    | `context`             | str          |     | ""        | Optional context for domain knowledge                                       |
    | `schema`              | str          |     | ""        | JSON string of BN schema (optional - fetched automatically if not provided) |
    | `explanation`         | bool         |     | True      | Return natural language explanation for the answer                           |
    | `structured_explanation` | bool     |     | False     | Return structured explanation (only effective when explanation is True)     |
    | `max_corrections`     | int          |     | 2         | Maximum number of correction attempts for query validation                   |
    | `max_num_paths`      | int          |     | 50        | Maximum number of reasoning paths to include in explanation                 |

    """

    PROMPT = """
You are an assistant that maps natural language questions into probabilistic query components for a Bayesian Network.

A Bayesian Network consists of:

- **Nodes** (random variables) - each node represents a variable in the domain

- **States** (possible values each node can take) - the discrete values each variable can assume

- **Directed edges** indicating conditional dependencies between variables

This network encodes a joint probability distribution P(X₁, X₂, ..., Xₙ).  

Each edge A → B means that the conditional probability P(B | A) is directly represented in the network.

--- 

${schema_section}

---

Given the following question, extract:

1. The **target node** being queried (i.e., the variable we want the probability for)

2. The **target state** or value of that variable (must be one of the valid states for that node)

3. Any **observed context** or evidence described in the question (as a dictionary mapping node names to their observed states)

---

Question: ${question}

---

Respond ONLY with a JSON object in the exact format below. Use the original node names and state values exactly as defined above:

{
  "target_node": "node_name",
  "target_state": "state_value",
  "context": {
    "node1": "state1",
    "node2": "state2"
  }
}

Important:
- Use exact node names and state values as shown in the schema information above
- The target_state must be a valid state for the target_node
- All context node states must be valid states for their respective nodes
- If no context is provided in the question, use an empty dictionary {} for context
"""

    CORRECTION_PROMPT = """
You previously generated a Bayesian Network query, but it has validation errors. Please correct the query based on the errors and the BN structure.

**Original Question:**
${question}

**Original Query:**
${original_query}

**Validation Errors:**
${validation_errors}

${schema_section}

---

Please correct the query to fix all validation errors. Respond ONLY with a JSON object in the exact format:

{
  "target_node": "node_name",
  "target_state": "state_value",
  "context": {
    "node1": "state1",
    "node2": "state2"
  }
}

Important:
- Use exact node names and state values from the schema information above
- Ensure all nodes exist in the BN
- Ensure all states are valid for their respective nodes
"""

    PROPERTIES = {
        # nl2bn related
        "execute_query": True,
        # service utils related
        "openai.api": "ChatCompletion",
        "openai.model": "gpt-4o",
        "openai.stream": False,
        "openai.max_tokens": 4096,
        "openai.temperature": 0,
        "input_json": "[{\"role\": \"user\"}]",
        "input_context": "$[0]",
        "input_context_field": "content",
        "input_field": "messages",
        "input_template": PROMPT,
        "output_path": "$.choices[0].message.content",
        "service_prefix": "openai",
        "output_transformations": [{"transformation": "replace", "from": "```", "to": ""}, {"transformation": "replace", "from": "json", "to": ""}],
        "output_strip": True,
        "output_cast": "json",
    }

    name = "nl2bn"
    description = "Translates natural language questions into Bayesian Network queries using LLM models"
    default_attributes = {
        "question": {"type": "str", "description": "Natural language question to translate to BN query", "required": True},
        "source": {"type": "str", "description": "BN data source name", "required": True, "default": ""},
        "database": {"type": "str", "description": "Database name", "required": True, "default": ""},
        "collection": {"type": "str", "description": "Collection/model name", "required": True, "default": ""},
        "protocol_variant": {"type": "str", "description": "Protocol variant (e.g., 'pgmpy')", "required": True, "default": "pgmpy"},
        "context": {"type": "str", "description": "Optional context for domain knowledge", "required": False, "default": ""},
        "schema": {"type": "str", "description": "JSON string of BN schema (optional - will be fetched automatically if not provided)", "required": False, "default": ""},
        "explanation": {"type": "bool", "description": "Return natural language explanation for the answer", "required": False, "default": True},
        "structured_explanation": {"type": "bool", "description": "Return structured explanation (only effective when explanation is True)", "required": False, "default": False},
        "max_corrections": {"type": "int", "description": "Maximum number of correction attempts for query validation", "required": False, "default": 2},
        "max_num_paths": {"type": "int", "description": "Maximum number of reasoning paths to include in explanation (default: 50)", "required": False, "default": 50},
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=nl2bn_operator_function,
            description=description or self.description,
            properties=properties,
            validator=nl2bn_operator_validator,
            explainer=nl2bn_operator_explainer,
        )

    def _initialize_properties(self):
        super()._initialize_properties()

        # attribute definitions
        self.properties["attributes"] = self.default_attributes

        # service_url, set as default
        self.properties["service_url"] = PROPERTIES["services.openai.service_url"]

    def extract_input_attributes(self, input_data, properties=None):
        """Extract input attributes for template substitution"""
        # For NL2BN, input_data is a dictionary containing all the template variables
        if isinstance(input_data, dict):
            return input_data
        return {}


def _get_data_registry_from_properties(properties: Dict[str, Any] = None) -> Optional[DataRegistry]:
    """Get data registry from properties."""
    if not properties:
        return None

    if 'data_registry' in properties and isinstance(properties['data_registry'], DataRegistry):
        return properties['data_registry']

    platform_id = properties.get("platform.name")
    data_registry_id = properties.get("data_registry.name")

    if platform_id and data_registry_id:
        prefix = 'PLATFORM:' + platform_id
        return DataRegistry(id=data_registry_id, prefix=prefix, properties=properties)
    return None


def _format_execution_result_format(result) -> List[List[Dict[str, Any]]]:
    """Format execution result to match the expected output format."""
    # case 1: result is None or empty list
    if result is None or not result or (isinstance(result, list) and len(result) == 0):
        return [[]]
    # case 2: result is dict
    elif isinstance(result, dict):
        return [[result]]
    # case 3: result is list of dicts
    elif isinstance(result, list) and all(isinstance(item, dict) for item in result):
        return [result]
    # case 4: result is list of list of dicts
    elif isinstance(result, list) and all(isinstance(item, list) for item in result):
        for item in result:
            if len(item) > 0 and not all(isinstance(subitem, dict) for subitem in item):
                break
        else:
            return result
    else:
        # unable to format result, raise error
        raise ValueError("Invalid result format from data registry execution: " + str(result))


if __name__ == "__main__":
    ## calling example with data registry integration
    ## Note: this example assumes a data registry is already running with the specified platform and registry names, and a BN source is already registered with the data registry

    input_data = [[]]
    attributes = {
        "question": "What is the probability of cirrhosis being present given that the patient has alcoholism, diabetes, and obesity?",
        "source": "bn_test7",  # please update your data source name accordingly
        "database": "default", # please update your database name accordingly
        "collection": "hepar2", # please update your collection name (BN folder name) accordingly
        "protocol_variant": "pgmpy",
        "context": "This is a Bayesian Network for liver disease diagnosis",
        "explanation": True,
        "structured_explanation": False,
    }

    print(f"=== NL2BN attributes ===")
    print(attributes)

    # Get default properties
    nl2bn_operator = NL2BNOperator()
    properties = nl2bn_operator.properties
    properties.update(
        {
            "service_url": "ws://localhost:8001",  # update this to your service url
            "platform.name": "chen", # update this to your platform name
            "data_registry.name": "default", # update this to your data registry name
        }
    )

    print(f"=== NL2BN PROPERTIES ===")
    print(properties)

    # call the function
    # Option 1: directly call the nl2bn_operator_function
    result = nl2bn_operator_function(input_data, attributes, properties)
    print("=== NL2BN RESULT (Option 1)===")
    print(result)
    # Option 2: use the function method
    result = nl2bn_operator.function(input_data, attributes, properties)
    print("=== NL2BN RESULT (Option 2)===")
    print(result)

