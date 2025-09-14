###### Formats
from typing import List, Dict, Any, Callable, Optional

import traceback

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer
from blue.data.registry import DataRegistry

###############
### Create Table Operator


def create_table_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    # Extract attributes
    source = attributes.get('source', 'default_source')
    database = attributes.get('database', 'default')
    collection = attributes.get('collection', 'public')
    overwrite = attributes.get('overwrite', False)
    
    # Get data registry from properties - follow agent pattern
    data_registry = _get_data_registry_from_properties(properties)
    if not data_registry:
        print("Error: Data registry not found")
        return [[]]
    
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
        # Validate input data
        if not input_data or not input_data[0]:
            return [[]]

        # Get table definition from input data
        table_def = input_data[0][0]
        if not isinstance(table_def, dict):
            return [[]]

        table_name = table_def.get('name')
        if not table_name:
            return [[]]
        
        description = table_def.get('description', '')
        created_by = table_def.get('created_by')
        
        # Registry properties (metadata)
        registry_properties = table_def.get('registry_properties', {})
        # Creation properties (for specific creation function(s) inside of the source)
        creation_properties = table_def.get('creation_properties', {})

        # Create the table using data registry
        data_registry.create_source_database_collection_entity(source=source, database=database, collection=collection, entity=table_name, properties=registry_properties, creation_properties=creation_properties, overwrite=overwrite, rebuild=True, recursive=False)

        # Set the description after table creation
        if description:
            data_registry.set_source_database_collection_entity_description(source=source, database=database, collection=collection, entity=table_name, description=description, rebuild=True)

        # Set the created_by after table creation
        if created_by:
            data_registry.set_record_data(name=table_name, type='entity', scope=f'/source/{source}/database/{database}/collection/{collection}', key='created_by', value=created_by, rebuild=True)

        print(f"Successfully created table '{table_name}' in database '{database}' collection '{collection}' of source '{source}'.")

        return [[]]

    except Exception as e:
        print("EXCEPTION")
        print(traceback.format_exc())
        return [[]]


def create_table_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate create table operator attributes."""
    try:
        if not default_operator_validator(input_data, attributes, properties):
            return False
    except Exception:
        return False

    # Check required attributes
    source = attributes.get('source', '')
    database = attributes.get('database', '')
    
    if not source or not source.strip():
        return False
    if not database or not database.strip():
        return False

    # Validate input data structure - expect single table dictionary
    if not input_data or not input_data[0] or len(input_data[0]) != 1:
        return False

    # Validate table definition
    table_def = input_data[0][0]
    if not isinstance(table_def, dict):
        return False
    
    # Check required fields
    required_fields = ['name']
    for field in required_fields:
        if field not in table_def:
            return False
    
    registry_properties = table_def.get('registry_properties', {})
    if registry_properties and not isinstance(registry_properties, dict):
        return False
    
    # There should be creation_properties and it should contains cols_definition
    creation_properties = table_def.get('creation_properties', {})
    if not creation_properties or not isinstance(creation_properties, dict):
        return False

    cols_definition = creation_properties.get('cols_definition', [])
    if not isinstance(cols_definition, list) or not cols_definition:
        return False

    return True


def create_table_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Explain create table operator output."""
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
    """

    PROPERTIES = {}

    name = "create_table"
    description = "Creates tables (entities) in database collections using the data registry. If the table already exists, it will be overwritten if overwrite is True."
    default_attributes = {
        "source": {"type": "str", "description": "Name of the data source where the table will be created", "required": True, "default": "default_source"},
        "database": {"type": "str", "description": "Name of the database where the table will be created", "required": True, "default": "default"},
        "collection": {"type": "str", "description": "Name of the collection where the table will be created. For SQLite sources, defaults to 'public' if not specified", "required": False, "default": "public"},
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
