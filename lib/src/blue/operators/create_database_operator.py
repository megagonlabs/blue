###### Formats
from typing import List, Dict, Any, Callable, Optional

import traceback
import logging

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer
from blue.data.registry import DataRegistry

###############
### Create Database Operator


def create_database_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Create databases in data sources using the data registry.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]), passes through unchanged.
        attributes: Dictionary containing database creation parameters including source, database, description, and other database properties.
        properties: Optional properties dictionary containing data registry information. Defaults to None.

    Returns:
        List containing the input data passed through unchanged.
    """
    # Extract attributes
    overwrite = attributes.get('overwrite', False)
    source = attributes.get('source', '')
    database = attributes.get('database')
    database_description = attributes.get('description', '')
    database_properties = attributes.get('properties', {})

    # Get data registry from properties - follow agent pattern
    data_registry = _get_data_registry_from_properties(properties)
    if not data_registry:
        logging.error("Error: Data registry not found")
        # pass through input to output
        return input_data

    try:

        # Create the database using data registry
        data_registry.create_source_database(source=source, database=database, properties=database_properties, overwrite=overwrite, rebuild=True, recursive=False)

        # Set the description after database creation
        if database_description:
            data_registry.set_source_database_description(source=source, database=database, description=database_description, rebuild=True)

        # Set the created_by after database creation
        created_by = attributes.get('created_by')
        if created_by:
            data_registry.set_record_data(name=database, type='database', scope=f'/source/{source}', key='created_by', value=created_by, rebuild=True)

        logging.info(f"Successfully created database '{database}' in source '{source}'.")

        # pass through input to output
        return input_data

    except Exception as e:
        logging.error(traceback.format_exc())
        # pass through input to output
        return input_data


def create_database_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate create database operator attributes.

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

    return True


def create_database_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for create database operator execution.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the database creation operation.
    """
    source = attributes.get('source', '')
    overwrite = attributes.get('overwrite', False)
    try:
        database_name = input_data[0][0].get('name', '') if input_data and input_data[0] else ''
    except (IndexError, KeyError, TypeError, AttributeError):
        database_name = ''

    create_database_explanation = {
        'input_data': input_data,
        'attributes': attributes,
        'explanation': f"Create database operator {'overwrote' if overwrite else 'created'} database '{database_name}' in source '{source}'.",
    }
    return create_database_explanation


###############
### CreateDatabaseOperator
#
class CreateDatabaseOperator(Operator):
    """
    Create database operator that creates databases in data sources.

    Attributes:
    ----------
    | Name         | Type | Required | Default | Description |
    |---------------|------|-----------|----------|--------------|
    | `source`      | str  | :fontawesome-solid-circle-check: {.green-check}       | ""       | Name of the data source where the database will be created. |
    | `database`    | str  | :fontawesome-solid-circle-check: {.green-check}       | ""       | Name of the database to be created. |
    | `description` | str  |         | ""       | Description of the database to be created. |
    | `properties`  | str  |         | {}       | Properties of the database to be created. |
    | `created_by`  | str  |         | ""       | Creator of the database. |
    | `overwrite`   | bool |         | False    | Whether to overwrite the existing database. |

    """

    PROPERTIES = {}

    name = "create_database"
    description = "Creates databases in data sources using the data registry. If the database already exists, it will be overwritten if overwrite is True."
    default_attributes = {
        "source": {"type": "str", "description": "Name of the data source where the database will be created", "required": True, "default": ""},
        "database": {"type": "str", "description": "Name of the database to be created", "required": True, "default": ""},
        "description": {"type": "str", "description": "Description of the database to be created", "required": False, "default": ""},
        "properties": {"type": "str", "description": "Properties of the database to be created", "required": False, "default": {}},
        "created_by": {"type": "str", "description": "Creator of the database", "required": False, "default": ""},
        "overwrite": {"type": "bool", "description": "Whether to overwrite the existing database", "required": False, "default": False},
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=create_database_operator_function,
            description=description or self.description,
            properties=properties,
            validator=create_database_operator_validator,
            explainer=create_database_operator_explainer,
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
