###### Parsers, Formats, Utils
import argparse
import logging
import json

###### Blue
from blue.utils import log_utils


###############
### DataSource
#
class DataSource:
    def __init__(self, name, properties={}):
        """
        Initialize a generic data source.

        Parameters:
            name (str): Name of the source.
            properties (dict, optional): Additional configuration properties.
        """

        self.name = name

        self._initialize(properties=properties)

        self._start()

    ###### initialization
    def _initialize(self, properties=None):
        """
        Perform internal initialization: properties and logger.
        """
        self._initialize_properties()
        self._update_properties(properties=properties)

        self._initialize_logger()

    def _initialize_properties(self):
        """
        Initialize default properties, including connection settings.
        """

        self.properties = {}

        # connection properties
        self._initialize_connection_properties()

    def _update_properties(self, properties=None):
        """
        Override default properties with provided dictionary.

        Parameters:
            properties (dict, optional): Properties to update.
        """
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def _initialize_connection_properties(self):
        connection_properties = {}

        connection_properties['protocol'] = 'default'
        self.properties['connection'] = connection_properties

    def _initialize_logger(self):
        self.logger = log_utils.CustomLogger()
        # customize log
        self.logger.set_config_data(
            "stack",
            "%(call_stack)s",
        )
        self.logger.set_config_data("source", self.name, -1)

    ###### connection
    def _start_connection(self):
        connection = self.properties['connection']

        self.connection = self._connect(**connection)

    def _stop_connection(self):
        self._disconnect()

    def _connect(self, **connection):
        return None

    def _disconnect(self):
        return None

    def _start(self):
        # self.logger.info('Starting session {name}'.format(name=self.name))
        self._start_connection()

        self.logger.info('Started source {name}'.format(name=self.name))

    def _stop(self):
        self._stop_connection()

        self.logger.info('Stopped source {name}'.format(name=self.name))

    ######### source
    def fetch_metadata(self):
        """
        Retrieve high-level metadata about the data source.

        Returns:
            dict: Source metadata such as name, type, or description.
                Default is an empty dictionary.
        """
        return {}

    def fetch_schema(self):
        """
        Retrieve the overall schema of the data source.

        Returns:
            dict: Schema definition including databases, collections, and entities.
                Default is an empty dictionary.
        """
        return {}

    ######### source/database
    def fetch_databases(self):
        """
        List all databases available in the data source.

        Returns:
            list[str]: Names of databases. Default is an empty list.
        """
        return []

    def fetch_database_metadata(self, database):
        """
        Retrieve metadata for a specific database.

        Parameters:
            database (str): Name of the database.

        Returns:
            dict: Database-level metadata such as size, owner, or creation date.
                Default is an empty dictionary.
        """
        return {}

    def fetch_database_schema(self, database):
        """
        Retrieve the schema of a specific database.

        Parameters:
            database (str): Name of the database.

        Returns:
            dict: Database schema including collections and entities.
                Default is an empty dictionary.
        """
        return {}

    def create_database(self, database, properties={}):
        """
        Create a new database in the data source.

        Parameters:
            database (str): Name of the new database.
            properties (dict, optional): Database-specific configuration options.

        Returns:
            dict: Metadata or result of the creation operation. Default is empty.
        """
        return {}

    ######### source/database/collection
    def fetch_database_collections(self, database):
        """
        List all collections in a database.

        Parameters:
            database (str): Database name.

        Returns:
            list: Collection names (default empty).
        """
        return []

    def fetch_database_collection_metadata(self, database, collection):
        """
        Fetch metadata for a collection.

        Parameters:
            database (str): Database name.
            collection (str): Collection name.

        Returns:
            dict: Collection metadata (default empty).
        """
        return {}

    def fetch_database_collection_entities(self, database, collection):
        """
        Retrieve entities (tables, objects, or equivalent) for a specific collection.

        Parameters:
            database (str): Name of the database.
            collection (str): Name of the collection or schema.

        Returns:
            dict: Dictionary of entities with their properties and metadata.
                Default is empty.
        """
        return {}

    def fetch_database_collection_relations(self, database, collection):
        """
        Retrieve relationships (e.g., foreign keys or links) between entities in a collection.

        Parameters:
            database (str): Name of the database.
            collection (str): Name of the collection or schema.

        Returns:
            dict: Dictionary of relations between entities.
                Default is empty.
        """
        return {}

    def create_database_collection(self, database, collection, properties={}):
        """
        Create a new collection (schema, table group, or equivalent) in a database.

        Parameters:
            database (str): Database name.
            collection (str): Name of the new collection.
            properties (dict, optional): Collection-specific properties.

        Returns:
            dict: Metadata or result of the creation operation. Default is empty.
        """
        return {}

    ######### source/database/collection/entity
    # properties: {
    #     "properties": [    <--- entity properties
    #         {
    #             "name": "",
    #             "type": "",
    #             "misc":
    #         }
    #      ]
    # }
    # note: misc can include primary key, etc. features that are db specific
    #
    def create_database_collection_entity(self, database, collection, entity, properties={}):
        """
        Create a new entity (table, object, or equivalent) within a collection.

        Parameters:
            database (str): Database name.
            collection (str): Collection or schema name.
            entity (str): Name of the entity to create.
            properties (dict, optional): Entity properties, including column definitions,
                                        types, and misc metadata such as primary keys.

        Returns:
            dict: Metadata or result of the creation operation. Default is empty.
        """
        return {}

    ######### source/database/collection/relation
    def create_database_collection_relation(self, database, collection, relation, properties={}):
        """
        Create a new relationship between entities within a collection.

        Parameters:
            database (str): Database name.
            collection (str): Collection or schema name.
            relation (str): Name or identifier of the relation.
            properties (dict, optional): Relation-specific metadata.

        Returns:
            dict: Metadata or result of the creation operation. Default is empty.
        """
        return {}

    ######### execute query
    def execute_query(self, query, database=None, collection=None, optional_properties={}):
        """
        Execute a query on the data source and return results.

        Parameters:
            query (str): Query string to execute.
            database (str, optional): Target database name.
            collection (str, optional): Target collection name.
            optional_properties (dict, optional): Additional execution options.

        Returns:
            list[dict]: List of results, each row as a dictionary.
                        Default is a single empty dictionary.
        """
        return [{}]

    #######  stats ############
    def fetch_source_stats(self):
        """
        Retrieve high-level statistics about the source itself.

        Returns:
            dict or None: Source-level statistics such as connection info,
                        number of databases, or performance metrics.
                        Default is None.
        """
        return None

    def fetch_database_stats(self, database):
        """
        Retrieve statistics for a specific database.

        Parameters:
            database (str): Database name.

        Returns:
            dict or None: Database-level statistics such as size, table count,
                        or other relevant metrics. Default is None.
        """
        return None

    def fetch_collection_stats(self, database, collection_name, schema_json=None, sample_limit=None):
        """
        Retrieve statistics for a specific collection (schema) in a database.

        Parameters:
            database (str): Database name.
            collection_name (str): Collection or schema name.
            schema_json (dict, optional): Schema definition for computing statistics.
            sample_limit (int, optional): Maximum number of samples to collect for properties.

        Returns:
            dict or None: Collection-level statistics such as number of entities,
                        relations, or sampled property values. Default is None.
        """
        return None

    def fetch_entity_stats(self, database, collection, entity):
        """
        Retrieve statistics for a specific entity (table/object) in a collection.

        Parameters:
            database (str): Database name.
            collection (str): Collection or schema name.
            entity (str): Entity name.

        Returns:
            dict or None: Entity-level statistics such as row count, size, or other metrics.
                        Default is None.
        """
        return None

    def fetch_property_stats(self, database, collection, entity, property_name, sample_limit=None):
        """
        Retrieve statistics for a specific property (column/attribute) of an entity.

        Parameters:
            database (str): Database name.
            collection (str): Collection or schema name.
            entity (str): Entity name.
            property_name (str): Property/column name.
            sample_limit (int, optional): Maximum number of sample values to fetch.

        Returns:
            dict or None: Property-level statistics such as count, distinct values,
                        null count, min/max, or sampled values. Default is None.
        """
        return None
