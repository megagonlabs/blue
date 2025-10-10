###### Formats
from typing import List, Dict, Any, Callable, Optional

import traceback
import logging

###### Blue
from blue.operators.operator import Operator, default_operator_validator, default_operator_explainer
from blue.data.registry import DataRegistry

###############
### Insert Table Operator


def insert_table_operator_function(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> List[List[Dict[str, Any]]]:
    """Insert data rows into database tables in a data source.

    Parameters:
        input_data: List of JSON arrays (List[List[Dict[str, Any]]]) containing records to insert.
        attributes: Dictionary containing insertion parameters including source, database, collection, table, and batch_size.
        properties: Optional properties dictionary containing data registry information. Defaults to None.

    Returns:
        List containing the input data passed through unchanged.
    """
    # Extract attributes
    source = attributes.get('source', 'default_source')
    database = attributes.get('database', 'default')
    collection = attributes.get('collection', 'public')
    table = attributes.get('table', '')
    batch_size = attributes.get('batch_size', 100)

    # Get data registry from properties - follow agent pattern
    data_registry = _get_data_registry_from_properties(properties)
    if not data_registry:
        logging.error("Error: Data registry not found")
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
        # Validate input data
        if not input_data or not input_data[0]:
            return [[]]

        # Process each data group
        total_inserted = 0
        for group_idx, row_group in enumerate(input_data):
            if not row_group:
                continue

            group_inserted = _insert_data_group(data_registry, source, database, collection, table, row_group, batch_size, group_idx)

            if group_inserted is None:
                return [[]]

            total_inserted += group_inserted

        logging.info(f"Successfully inserted {total_inserted} rows into table '{table}' in database '{database}' collection '{collection}' of source '{source}'.")

        # Return summary of inserted data
        # return [[{"table": table, "rows_inserted": total_inserted, "source": source, "database": database, "collection": collection}]]
        return input_data

    except Exception as e:
        logging.error(traceback.format_exc())
        return input_data


def insert_table_operator_validator(input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any], properties: Dict[str, Any] = None) -> bool:
    """Validate insert table operator attributes.

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
    database = attributes.get('database', '')
    table = attributes.get('table', '')

    if not source or not source.strip():
        return False
    if not database or not database.strip():
        return False
    if not table or not table.strip():
        return False

    # Validate batch_size if provided
    batch_size = attributes.get('batch_size', 100)
    if not isinstance(batch_size, int) or batch_size <= 0:
        return False

    return True


def insert_table_operator_explainer(output: Any, input_data: List[List[Dict[str, Any]]], attributes: Dict[str, Any]) -> Dict[str, Any]:
    """Generate explanation for insert table operator execution.

    Parameters:
        output: The output result from the operator execution.
        input_data: The input data that was processed.
        attributes: The attributes used for the operation.

    Returns:
        Dictionary containing explanation of the table insertion operation.
    """
    source = attributes.get('source', 'default_source')
    database = attributes.get('database', 'default')
    collection = attributes.get('collection', 'public')
    table = attributes.get('table', '')
    batch_size = attributes.get('batch_size', 100)
    total_rows = sum(len(row_group) for row_group in input_data)
    num_data_groups = len(input_data)

    insert_table_explanation = {
        'input_data': input_data,
        'attributes': attributes,
        'explanation': f"Insert table operator inserted {total_rows} data rows from {num_data_groups} data groups into table '{table}' in database '{database}' collection '{collection}' of source '{source}' using batch size {batch_size}.",
    }
    return insert_table_explanation


###############
### InsertTableOperator
#
class InsertTableOperator(Operator):
    """
    Insert table operator that inserts data rows into database tables

    Attributes:
    ----------
    | Name       | Type | Required | Default          | Description                                                                 |
    |------------|------|----------|-----------------|-----------------------------------------------------------------------------|
    | `source`     | str  | :fontawesome-solid-circle-check: {.green-check}     | default_source  | Name of the data source where the table is located                          |
    | `database`   | str  | :fontawesome-solid-circle-check: {.green-check}     | default         | Name of the database where the table is located                             |
    | `collection` | str  |     | public          | Name of the collection where the table is located. For SQLite sources, defaults to 'public' if not specified |
    | `table`      | str  | :fontawesome-solid-circle-check: {.green-check}     | ""              | Name of the table to insert data into                                       |
    | `batch_size` | int  |     | 100             | Number of rows to insert in each batch (default: 100)                       |

    """

    PROPERTIES = {}

    name = "insert_table"
    description = "Inserts data rows into database tables in a data source."
    default_attributes = {
        "source": {"type": "str", "description": "Name of the data source where the table is located", "required": True, "default": "default_source"},
        "database": {"type": "str", "description": "Name of the database where the table is located", "required": True, "default": "default"},
        "collection": {
            "type": "str",
            "description": "Name of the collection where the table is located. For SQLite sources, defaults to 'public' if not specified",
            "required": False,
            "default": "public",
        },
        "table": {"type": "str", "description": "Name of the table to insert data into", "required": True, "default": ""},
        "batch_size": {"type": "int", "description": "Number of rows to insert in each batch (default: 100)", "required": False, "default": 100},
    }

    def __init__(self, description: str = None, properties: Dict[str, Any] = None):
        super().__init__(
            self.name,
            function=insert_table_operator_function,
            description=description or self.description,
            properties=properties,
            validator=insert_table_operator_validator,
            explainer=insert_table_operator_explainer,
        )

    def _initialize_properties(self):
        super()._initialize_properties()

        # attribute definitions
        self.properties["attributes"] = self.default_attributes


###########
### Helper functions


def _insert_data_group(data_registry, source, database, collection, table, row_group, batch_size, group_idx):
    """Insert a single data group into the table."""
    # Extract data rows from this group
    data_rows = []
    for row in row_group:
        if isinstance(row, dict) and row:  # Only add non-empty rows
            data_rows.append(row)
    if not data_rows:
        return 0

    # Insert data in batches
    group_inserted = 0
    for i in range(0, len(data_rows), batch_size):
        batch = data_rows[i : i + batch_size]
        if not batch:
            continue

        # Get column names from first row
        columns = list(batch[0].keys())
        columns_str = ', '.join([f'"{col}"' for col in columns])
        placeholders = ', '.join(['?' for _ in columns])

        insert_query = f'INSERT INTO "{table}" ({columns_str}) VALUES ({placeholders})'

        # Prepare data for batch insert
        batch_data = []
        for row in batch:
            row_values = []
            for col in columns:
                value = row.get(col)
                # Handle None values properly
                if value is None:
                    row_values.append(None)
                else:
                    row_values.append(value)
            batch_data.append(tuple(row_values))

        # Execute batch insert using data registry
        try:
            # Use the data registry's execute_query method
            source_connection = data_registry.connect_source(source)
            if source_connection:
                db_connection = source_connection._db_connect(database)
                cursor = db_connection.cursor()

                # Execute batch insert
                cursor.executemany(insert_query, batch_data)
                db_connection.commit()

                # Get number of inserted rows
                inserted_count = cursor.rowcount
                group_inserted += inserted_count

                # Close connection
                source_connection._db_disconnect(db_connection)

            else:
                return None

        except Exception as e:
            logging.error(f"Error inserting group {group_idx + 1}, batch {i//batch_size + 1}: {str(e)}")
            logging.error(traceback.format_exc())
            return None

    return group_inserted


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
    # Example input data - job skills data
    input_data = [
        [
            {"skill_id": 1, "skill_name": "Python", "category": "Programming", "level": 3, "description": "Python programming language", "extraction_date": "2025-01-15", "resume_id": 101},
            {"skill_id": 2, "skill_name": "SQL", "category": "Database", "level": 2, "description": "Structured Query Language", "extraction_date": "2025-01-15", "resume_id": 101},
            {
                "skill_id": 3,
                "skill_name": "Machine Learning",
                "category": "AI/ML",
                "level": 4,
                "description": "Machine learning algorithms and techniques",
                "extraction_date": "2025-01-16",
                "resume_id": 102,
            },
        ]
    ]

    # Example attributes
    attributes = {"source": "sqlite_test_source", "database": "sqlite_test_db", "collection": "public", "table": "job_skills", "batch_size": 100}

    # Example properties
    properties = {"platform.name": "test_platform", "data_registry.name": "test_registry"}
