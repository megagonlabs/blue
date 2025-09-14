###### Formats
from typing import List, Dict, Any, Callable, Optional

import traceback

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer
from blue.data.registry import DataRegistry

###############
### Create Database Operator


def create_database_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    # Extract attributes
    source = attributes.get('source', '')
    overwrite = attributes.get('overwrite', False)

    # Get data registry from properties - follow agent pattern
    data_registry = _get_data_registry_from_properties(properties)
    if not data_registry:
        print("Error: Data registry not found")
        return [[]]

    try:
        # Validate input data
        if not input_data or not input_data[0]:
            return [[]]

        # Get database definition from input data
        db_def = input_data[0][0]
        if not isinstance(db_def, dict):
            return [[]]

        database_name = db_def.get('name')
        if not database_name:
            return [[]]
        description = db_def.get('description', '')
        db_properties = db_def.get('database_properties', {})
        # notes: the key-value pairs in db_properties will be set as database properties in the data registry

        # Create the database using data registry
        data_registry.create_source_database(source=source, database=database_name, properties=db_properties, overwrite=overwrite, rebuild=True, recursive=False)

        # Set the description after database creation
        if description:
            data_registry.set_source_database_description(source=source, database=database_name, description=description, rebuild=True)

        # Set the created_by after database creation
        created_by = db_def.get('created_by')
        if created_by:
            data_registry.set_record_data(name=database_name, type='database', scope=f'/source/{source}', key='created_by', value=created_by, rebuild=True)

        print(f"Successfully created database '{database_name}' in source '{source}'.")

        return [[]]

    except Exception as e:
        print("EXCEPTION")
        print(traceback.format_exc())
        return [[]]


def create_database_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate create database operator attributes."""
    try:
        if not default_operator_validator(input_data, attributes, properties):
            return False
    except Exception:
        return False

    # Check required attributes
    source = attributes.get('source', '')
    if not source or not source.strip():
        return False

    # Validate input data structure - expect single database dictionary
    if not input_data or not input_data[0] or len(input_data[0]) != 1:
        return False

    # Validate database definition
    db_def = input_data[0][0]
    if not isinstance(db_def, dict):
        return False
    required_fields = ['name']
    for field in required_fields:
        if field not in db_def:
            return False

    return True


def create_database_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Explain create database operator output."""
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
    Create database operator that creates databases in data sources
    """

    PROPERTIES = {}

    name = "create_database"
    description = "Creates databases in data sources using the data registry. If the database already exists, it will be overwritten if overwrite is True."
    default_attributes = {
        "source": {"type": "str", "description": "Name of the data source where the database will be created", "required": True, "default": ""},
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
