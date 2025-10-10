###### Formats
from typing import List, Dict, Any, Callable, Optional

import traceback
import logging

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer
from blue.data.registry import DataRegistry

###############
### Create Table Operator


def create_table_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Create tables (entities) in database collections using the data registry.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]), passes through unchanged.
        attributes: Dictionary containing table creation parameters including source, database, collection, table, columns, and other table properties.
        properties: Optional properties dictionary containing data registry information. Defaults to None.

    Returns:
        List containing the input data passed through unchanged.
    """
    # Extract attributes
    overwrite = attributes.get('overwrite', False)
    source = attributes.get('source', 'default_source')
    database = attributes.get('database', 'default')
    collection = attributes.get('collection', 'public')
    table = attributes.get('table')
    table_description = attributes.get('description', '')
    table_properties = attributes.get('properties', {})
    columns = attributes.get('columns')
    misc = attributes.get('misc', {})

    # Get data registry from properties - follow agent pattern
    data_registry = _get_data_registry_from_properties(properties)
    if not data_registry:
        logging.error("Error: Data registry not found")
        # pass through input to output
        return input_data

    # Set collection to 'public' for SQLite sources even caller specifies a different collection
    try:
        source_properties = data_registry.get_source_properties(source)
        if source_properties and 'connection' in source_properties:
            protocol = source_properties['connection'].get('protocol', '')
            if protocol == 'sqlite':
                collection = 'public'  # always use 'public' for SQLite as collection name
    except Exception:
        pass

    try:

        # TODO: modify this after discussion
        # creation related properties
        creation_properties = misc
        creation_properties['cols_definition'] = columns

        # Create the table using data registry
        data_registry.create_source_database_collection_entity(
            source=source,
            database=database,
            collection=collection,
            entity=table,
            properties=table_properties,
            creation_properties=creation_properties,
            overwrite=overwrite,
            rebuild=True,
            recursive=False,
        )

        # Set the description after table creation
        if table_description:
            data_registry.set_source_database_collection_entity_description(source=source, database=database, collection=collection, entity=table, description=table_description, rebuild=True)

        # Set the created_by after table creation
        created_by = attributes.get('created_by')
        if created_by:
            data_registry.set_record_data(name=table, type='entity', scope=f'/source/{source}/database/{database}/collection/{collection}', key='created_by', value=created_by, rebuild=True)

        logging.info(f"Successfully created table '{table}' in database '{database}' collection '{collection}' of source '{source}'.")

        # pass through input to output
        return input_data

    except Exception as e:
        logging.error(traceback.format_exc())
        # pass through input to output
        return input_data


def create_table_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate create table operator attributes.

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

    # Check required attributes
    source = attributes.get('source', '')
    if not source or not source.strip():
        return False

    database = attributes.get('database', '')
    if not database or not database.strip():
        return False

    collection = attributes.get('collection', 'public')
    if not collection or not collection.strip():
        return False

    table = attributes.get('table', '')
    if not table or not table.strip():
        return False

    columns = attributes.get('columns', [])
    if not isinstance(columns, list) or not columns:
        return False

    # Validate each column definition
    for column in columns:
        if not isinstance(column, dict):
            return False
        if 'name' not in column or not column['name']:
            return False
        # type is optional but if provided should be a string
        if 'type' in column and not isinstance(column['type'], str):
            return False
        # misc is optional but if provided should be a string
        if 'misc' in column and not isinstance(column['misc'], str):
            return False

    misc = attributes.get('misc', {})
    # Validate primary_key if provided
    primary_key = misc.get('primary_key', [])
    if primary_key:
        if not isinstance(primary_key, list):
            return False
        # Check that all primary key columns exist in columns
        col_names = [col['name'] for col in columns]
        for pk_col in primary_key:
            if pk_col not in col_names:
                return False

    # Validate foreign_keys if provided
    foreign_keys = misc.get('foreign_keys', [])
    if foreign_keys:
        if not isinstance(foreign_keys, list):
            return False
        for fk in foreign_keys:
            if not isinstance(fk, dict):
                return False
            required_fk_fields = ['foreign_keys_source_columns', 'foreign_keys_target_table', 'foreign_keys_target_columns']
            for field in required_fk_fields:
                if field not in fk:
                    return False
            # Check that source columns exist in columns
            col_names = [col['name'] for col in columns]
            for fk_col in fk['foreign_keys_source_columns']:
                if fk_col not in col_names:
                    return False

    return True


def create_table_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for create table operator execution.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the table creation operation.
    """
    source = attributes.get('source', 'default_source')
    database = attributes.get('database', 'default')
    collection = attributes.get('collection', 'public')
    overwrite = attributes.get('overwrite', False)

    try:
        table_name = input_data[0][0].get('name', '') if input_data and input_data[0] else ''
    except (IndexError, KeyError, TypeError, AttributeError):
        table_name = ''

    create_table_explanation = {
        'input_data': input_data,
        'attributes': attributes,
        'explanation': f"Create table operator {'overwrote' if overwrite else 'created'} table '{table_name}' in database '{database}' collection '{collection}' of source '{source}'.",
    }
    return create_table_explanation


###############
### CreateTableOperator
#
class CreateTableOperator(Operator):
    """
    Create table operator that creates tables (entities) in database collections

    Attributes:
    ----------
    | Name         | Type  | Required | Default          | Description                                                                 |
    |---------------|-------|-----------|------------------|-----------------------------------------------------------------------------|
    | `source`        | str   | :fontawesome-solid-circle-check: {.green-check}       | "default_source" | Name of the data source where the table will be created.                   |
    | `database`      | str   | :fontawesome-solid-circle-check: {.green-check}       | "default"        | Name of the database where the table will be created.                      |
    | `collection`    | str   |       | "public"         | Name of the collection where the table will be created. For SQLite sources, defaults to 'public' if not specified. |
    | `table`         | str   | :fontawesome-solid-circle-check: {.green-check}       | ""               | Name of the table to be created.                                           |
    | `description`   | str   |       | ""               | Description of the table to be created.                                    |
    | `properties`    | str   |       | {}               | Properties of the table to be created.                                     |
    | `columns`       | list  | :fontawesome-solid-circle-check: {.green-check}       | []               | Properties of the table to be created.                                     |
    | `misc`          | dict  |       | {}               | Miscellaneous keys such as primary and foreign keys.                       |
    | `created_by`    | str   |       | ""               | Creator of the table.                                                      |
    | `overwrite`     | bool  |       | False            | Whether to overwrite the existing table.                                   |

    """

    PROPERTIES = {}

    name = "create_table"
    description = "Creates tables (entities) in database collections using the data registry. If the table already exists, it will be overwritten if overwrite is True."
    default_attributes = {
        "source": {"type": "str", "description": "Name of the data source where the table will be created", "required": True, "default": "default_source"},
        "database": {"type": "str", "description": "Name of the database where the table will be created", "required": True, "default": "default"},
        "collection": {
            "type": "str",
            "description": "Name of the collection where the table will be created. For SQLite sources, defaults to 'public' if not specified",
            "required": False,
            "default": "public",
        },
        "table": {"type": "str", "description": "Name of the table to be created", "required": True, "default": ""},
        "description": {"type": "str", "description": "Description of the table to be created", "required": False, "default": ""},
        "properties": {"type": "str", "description": "Properties of the table to be created", "required": False, "default": {}},
        "columns": {"type": "list", "description": "Properties of the table to be created", "required": True, "default": []},
        "misc": {"type": "dict", "description": "Miscellaneous keys such as primary and foreign keys ", "required": False, "default": {}},
        "created_by": {"type": "str", "description": "Creator of the table", "required": False, "default": ""},
        "overwrite": {"type": "bool", "description": "Whether to overwrite the existing table", "required": False, "default": False},
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=create_table_operator_function,
            description=description or self.description,
            properties=properties,
            validator=create_table_operator_validator,
            explainer=create_table_operator_explainer,
        )

    def _initialize_properties(self):
        super()._initialize_properties()

        # attribute definitions
        self.properties["attributes"] = self.default_attributes


###########
### Helper functions


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


if __name__ == "__main__":
    # Example input data
    input_data = [[]]

    # Example attributes
    attributes = {
        "source": "sqlite_test_source",
        "database": "sqlite_test_db",
        "collection": "public",
        "table": "job_skills",
        "description": "This is a table that contains skill extraction results from resumes",
        "created_by": "",
        "properties": {"version": "0.1"},
        "columns": [
            {"name": "skill_id", "type": "INTEGER", "misc": "NOT NULL"},
            {"name": "skill_name", "type": "TEXT"},
            {"name": "category", "type": "TEXT"},
            {"name": "level", "type": "INTEGER"},
            {"name": "description"},
            {"name": "extraction_date"},
            {"name": "resume_id"},
        ],
        "misc": {
            "primary_key": ["skill_id"],
            "foreign_keys": [{"foreign_keys_source_columns": ["resume_id"], "foreign_keys_target_table": "resume", "foreign_keys_target_columns": ["resume_id"]}],
        },
        "overwrite": False,
    }
