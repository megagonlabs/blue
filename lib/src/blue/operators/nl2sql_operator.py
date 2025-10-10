###### Formats
import json
from typing import List, Dict, Any, Callable, Optional

import traceback
import logging

###### External
import psycopg2
import mysql.connector

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer
from blue.utils.service_utils import ServiceClient
from blue.data.schema import DataSchema
from blue.data.registry import DataRegistry
from blue.properties import PROPERTIES

###############
### NL2SQL Operator


def nl2sql_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Translate natural language questions into SQL queries using LLM models.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]), not used for query processing.
        attributes: Dictionary containing query parameters including question, source, protocol, database, collection, and other SQL generation settings.
        properties: Optional properties dictionary containing service configuration and data registry information. Defaults to None.

    Returns:
        List containing SQL query results or the generated SQL query if execution is disabled.
    """
    question = attributes.get('question', '')
    source = attributes.get('source', '')
    protocol = attributes.get('protocol', 'postgres')
    database = attributes.get('database', '')
    collection = attributes.get('collection', '')
    force_query_prefixes = attributes.get('force_query_prefixes', 'SELECT')
    case_insensitive = attributes.get('case_insensitive', True)
    additional_requirements = attributes.get('additional_requirements', '')
    context = attributes.get('context', '')
    schema = attributes.get('schema', '')
    attr_names = attributes.get('attr_names', [])

    if not question or not question.strip():
        return [[]]

    # protocol, database, collection are required
    if not protocol or not database or not collection:
        raise ValueError("Protocol, database, and collection are required")

    data_registry = _get_data_registry_from_properties(properties)
    if not data_registry:
        return [[]]

    # get schema from data registry
    schema = data_registry.get_data_source_schema(source, database, collection)
    logging.debug("SCHEMA:")
    logging.debug(schema)
    # convert schema to JSON string if it's a dictionary
    if isinstance(schema, dict):
        schema_str = json.dumps(schema, indent=2)
    else:
        schema_str = str(schema)

    execute_query = properties.get('execute_query', True) if properties else True
    validate_query_prefixes = properties.get('validate_query_prefixes', ['SELECT']) if properties else ['SELECT']
    if protocol not in ['postgres', 'mysql', 'sqlite']:
        raise ValueError(f"Unsupported protocol: {protocol}. Supported protocols are: postgres, mysql, sqlite")

    service_client = ServiceClient(name="nl2sql_operator_service_client", properties=properties)

    # Create optional attr_names_section
    attr_names_section = ""
    if attr_names and len(attr_names) > 0:
        attr_names_list = ", ".join(attr_names)
        attr_names_section = f"## Target Field Names (SELECT AS):\nPlease use the following field names as column aliases if it's not same with the column names. Use 'AS' keyword if needed to alias columns:\n{attr_names_list}\n"

    additional_data = {
        'question': question,
        'schema': schema_str,
        'protocol': protocol,
        'sensitivity': 'insensitive' if case_insensitive else 'sensitive',
        'force_query_prefixes': force_query_prefixes,
        'additional_requirements': additional_requirements,
        'context': context,
        'attr_names_section': attr_names_section,
    }
    sql_result = service_client.execute_api_call({}, properties=properties, additional_data=additional_data)

    # Parse the result to get the query
    if isinstance(sql_result, str):
        try:
            sql_data = json.loads(sql_result)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from LLM: {str(e)}")
    elif isinstance(sql_result, dict):
        sql_data = sql_result
    else:
        raise ValueError("Invalid response from LLM: " + str(sql_result))

    generated_query = sql_data.get('query', '')
    if not generated_query:
        raise ValueError("No query found in LLM response")

    # Validate query prefix
    if not any(generated_query.upper().startswith(prefix.upper()) for prefix in validate_query_prefixes):
        raise ValueError(f'Invalid query prefix: {generated_query}')

    # If execution is enabled, execute the generated SQL
    if execute_query and generated_query:
        # use data registry to execute query
        logging.info("Generated Query: " + generated_query)
        result = data_registry.execute_query(generated_query, source, database, collection)
        logging.debug("Result: ")
        logging.debug(result)
        result = _format_execution_result_format(result)
        return result
    # if execution is disabled, return the sql query only
    return [[{"sql": generated_query}]]


def nl2sql_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate nl2sql operator attributes.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) to validate.
        attributes: Dictionary containing operator attributes to validate.
        properties: Optional properties dictionary. Defaults to None.

    Returns:
        True if attributes are valid, False otherwise.
    """
    return default_operator_validator(input_data, attributes, properties)


def nl2sql_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for nl2sql operator execution.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the SQL generation and execution operation.
    """
    nl2sql_explanation = {
        'output': output,
        "attributes": attributes,
    }
    return nl2sql_explanation


class NL2SQLOperator(Operator, ServiceClient):
    """
    NL2SQL operator translates natural language questions into SQL queries using LLM models.
    It can also execute the generated SQL query against the specified database and return the results.

    Attributes:
    ----------
    | Name                  | Type         | Required | Default   | Description                                                                 |
    |-----------------------|--------------|----------|-----------|-----------------------------------------------------------------------------|
    | `source`              | str          | :fontawesome-solid-circle-check: {.green-check}     | ""        | Data source name                                                            |
    | `question`            | str          | :fontawesome-solid-circle-check: {.green-check}     |           | Natural language question to translate to SQL                               |
    | `protocol`            | str          | :fontawesome-solid-circle-check: {.green-check}     | "postgres"| Database protocol (postgres, mysql, sqlite)                                 |
    | `database`            | str          | :fontawesome-solid-circle-check: {.green-check}     | ""        | Database name                                                               |
    | `collection`          | str          | :fontawesome-solid-circle-check: {.green-check}     | ""        | Collection/schema name                                                      |
    | `case_insensitive`    | bool         |     | True      | Case insensitive string matching                                            |
    | `additional_requirements`| str         |     | ""        | Additional requirements for SQL generation                                  |
    | `context`             | str          |     | ""        | Optional context for domain knowledge                                       |
    | `schema`              | str          |     | ""        | JSON string of database schema (optional - will be fetched automatically if not provided) |
    | `attr_names`          | list[str]    |     | []        | Optional list of target field names for the output objects                 |

    """

    PROMPT = """
Your task is to translate a natural language question into a SQL query based on the provided database schema.

## Here are the requirements:
- The output should be a JSON object with the following fields:
  - "question": the original natural language question
  - "query": the SQL query that is translated from the natural language question
- The SQL query should be compatible with the provided schema.
- The SQL query should be compatible with the syntax of the corresponding database's protocol.
- For enum fields, do not use LOWER(), ILIKE, or other string functions. Compare enum fields using exact equality.
- Always do case-${sensitivity} matching for string comparison.
- The query should start with any of the following prefixes: ${force_query_prefixes}
- When interpreting the "question" use additional context provided, if available.
- Output the JSON directly. Do not generate explanation or other additional output.
${additional_requirements}

## Database Protocol: 
```
${protocol}
```

##Database Schema:
```
${schema}
```

## Context: ${context}

## Question: ${question}

${attr_names_section}

---
## Output (JSON only):
"""

    PROPERTIES = {
        # nl2sql related
        "execute_query": True,
        # "force_query_prefixes": "SELECT",
        "validate_query_prefixes": ["SELECT"],
        # service utils related
        "openai.api": "ChatCompletion",
        "openai.model": "gpt-4o",
        "openai.stream": False,
        "openai.max_tokens": 512,
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
        # connection
        # "connection": {"host": "localhost", "port": 5432, "protocol": "postgres", "user": "postgres", "password": "postgres"},
    }

    name = "nl2sql"
    description = "Translates natural language questions into SQL queries using LLM models"
    default_attributes = {
        "source": {"type": "str", "description": "Data source name", "required": True, "default": ""},
        "question": {"type": "str", "description": "Natural language question to translate to SQL", "required": True},
        "protocol": {"type": "str", "description": "Database protocol (postgres, mysql, sqlite)", "required": True, "default": "postgres"},
        "database": {"type": "str", "description": "Database name", "required": True, "default": ""},
        "collection": {"type": "str", "description": "Collection/schema name", "required": True, "default": ""},
        "case_insensitive": {"type": "bool", "description": "Case insensitive string matching", "required": False, "default": True},
        "additional_requirements": {"type": "str", "description": "Additional requirements for SQL generation", "required": False, "default": ""},
        "context": {"type": "str", "description": "Optional context for domain knowledge", "required": False, "default": ""},
        "schema": {"type": "str", "description": "JSON string of database schema (optional - will be fetched automatically if not provided)", "required": False, "default": ""},
        "attr_names": {"type": "list[str]", "description": "Optional list of target field names for the output objects", "required": False, "default": []},
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=nl2sql_operator_function,
            description=description or self.description,
            properties=properties,
            validator=nl2sql_operator_validator,
            explainer=nl2sql_operator_explainer,
        )

    def _initialize_properties(self):
        super()._initialize_properties()

        # attribute definitions
        self.properties["attributes"] = self.default_attributes

        # service_url, set as default
        self.properties["service_url"] = PROPERTIES["services.openai.service_url"]

    def extract_input_attributes(self, input_data, properties=None):
        """Extract input attributes for template substitution"""
        # For NL2SQL, input_data is a dictionary containing all the template variables
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


###############
### Helper Functions of NL2SQL Operator, the following functions are for local run usage only without need of Blue data registry. Please do not use these functions in production.
def _fetch_database_schema(protocol: str, database: str, collection: str, properties: Dict[str, Any]) -> str:
    """Fetch database schema directly from the database."""
    connection_attributes = properties.get('connection', {})
    if not connection_attributes:
        raise ValueError("No connection attributes provided for schema fetching")

    try:
        if protocol == 'postgres':
            return _fetch_postgres_schema(database, collection, connection_attributes)
        elif protocol == 'mysql':
            return _fetch_mysql_schema(database, collection, connection_attributes)
        else:
            raise ValueError(f"Unsupported protocol for schema fetching: {protocol}")
    except Exception as e:
        raise ValueError(f"Error fetching schema: {str(e)}")


def _fetch_postgres_schema(database: str, collection: str, connection_attributes: Dict[str, Any]) -> str:
    """Fetch PostgreSQL schema."""
    # Connect to the database
    conn = psycopg2.connect(
        host=connection_attributes.get('host'),
        port=connection_attributes.get('port'),
        database=database,
        user=connection_attributes.get('user'),
        password=connection_attributes.get('password'),
    )

    try:
        cursor = conn.cursor()

        # fallback to use the "public" schema in PostgreSQL if collection is not provided
        schema_name = collection if collection else 'public'

        # Get enum types
        enum_query = """
        SELECT
          n.nspname AS schema,
          t.typname AS type_name,
          e.enumlabel AS enum_value
        FROM
          pg_type t
        JOIN
          pg_enum e ON t.oid = e.enumtypid
        JOIN
          pg_catalog.pg_namespace n ON n.oid = t.typnamespace
        WHERE
          n.nspname NOT IN ('pg_catalog', 'information_schema')
        ORDER BY
          t.typname, e.enumsortorder;
        """
        cursor.execute(enum_query)
        enum_data = cursor.fetchall()

        # Build enum types dictionary
        enum_types = {}
        for schema, type_name, enum_value in enum_data:
            if type_name not in enum_types:
                enum_types[type_name] = []
            enum_types[type_name].append(enum_value)

        # Get columns (same as original)
        query = """
        SELECT table_name, column_name, data_type, udt_name
        FROM information_schema.columns
        WHERE table_schema = %s
        """
        cursor.execute(query, (schema_name,))
        data = cursor.fetchall()

        # Use DataSchema like the original
        schema = DataSchema()

        for table_name, column_name, data_type, udt_name in data:
            if not schema.has_entity(table_name):
                schema.add_entity(table_name)

            if enum_types and udt_name in enum_types:
                schema.add_entity_property(table_name, column_name, {"type": data_type, "enum": enum_types[udt_name]})
            else:
                schema.add_entity_property(table_name, column_name, data_type)

        return schema.to_json()

    finally:
        cursor.close()
        conn.close()


def _fetch_mysql_schema(database: str, collection: str, connection_attributes: Dict[str, Any]) -> str:
    """Fetch MySQL schema."""
    # Connect to the database
    conn = mysql.connector.connect(
        host=connection_attributes.get('host'),
        port=connection_attributes.get('port'),
        database=database,
        user=connection_attributes.get('user'),
        password=connection_attributes.get('password'),
    )

    try:
        cursor = conn.cursor(buffered=True)

        # TODO: Do better ER extraction from tables, columns, exploiting column semantics, foreign keys, etc.
        query = "SELECT table_name, column_name, data_type from information_schema.columns WHERE table_schema = '{}'".format(database)
        cursor.execute(query)
        data = cursor.fetchall()

        # Use DataSchema like the original
        schema = DataSchema()

        for table_name, column_name, data_type in data:
            if not schema.has_entity(table_name):
                schema.add_entity(table_name)
            schema.add_entity_property(table_name, column_name, data_type)

        return schema.to_json()

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    ## calling example with data registry integration
    ## Note: this example assumes a data registry is already running with the specified platform and registry names, and a postgres source is already registered with the data registry

    input_data = [[]]
    attributes = {
        "question": "what is the most frequently advertised manager role in jurong?",
        # "question": "what are the top 10 project manager jobs in jurong with a minimum salary of 4000?",
        "source": "postgres_example",  # please udpate your data source name accordingly
        "protocol": "postgres",
        "database": "postgres",
        "collection": "public",
        "case_insensitive": True,
        "additional_requirements": "",
        "context": "This is a job database with information about job postings, skills, companies, and salaries",
        # schema will be fetched automatically from data registry
    }

    print(f"=== NL2SQL attributes ===")
    print(attributes)

    # Get default properties
    nl2sql_operator = NL2SQLOperator()
    properties = nl2sql_operator.properties
    properties.update(
        {
            "service_url": "ws://localhost:8001",  # update this to your service url
            "platform.name": "example_platform",
            "data_registry.name": "default",
        }
    )

    print(f"=== NL2SQL PROPERTIES ===")
    print(properties)

    # call the function
    # Option 1: directly call the nl2sql_operator_function
    result = nl2sql_operator_function(input_data, attributes, properties)
    print("=== NL2SQL RESULT (Option 1)===")
    print(result)
    # Option 2: use the function method
    result = nl2sql_operator.function(input_data, attributes, properties)
    print("=== NL2SQL RESULT (Option 2)===")
    print(result)
