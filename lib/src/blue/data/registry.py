###### Parsers, Formats, Utils
import argparse
import logging
import json

import yaml
import numpy as np

###### Blue
from blue.utils import json_utils
from blue.registry import Registry

from blue.data.schema import DataSchema
from blue.utils.similarity_utils import compute_bm25_score, normalize_bm25_scores, compute_vector_score

###### Supported Data Sources
from blue.data.sources.mongodb_source import MongoDBSource
from blue.data.sources.neo4j_source import NEO4JSource
from blue.data.sources.postgres_source import PostgresDBSource
from blue.data.sources.mysql_source import MySQLDBSource
from blue.data.sources.sqlite_source import SQLiteDBSource
from blue.data.sources.openai_source import OpenAISource

###### Backend, Databases
import redis
from redis.commands.json.path import Path
from redis.commands.search.field import TextField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query


###############
### DataRegistry
#
class DataRegistry(Registry):
    def __init__(self, name="DATA_REGISTRY", id=None, platform_id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):
        super().__init__(name=name, id=id, platform_id=platform_id, sid=sid, cid=cid, prefix=prefix, suffix=suffix, properties=properties)
        self._init_binary_connection()

    def _init_binary_connection(self):
        host = self.properties["db.host"]
        port = self.properties["db.port"]

        self.connection_no_decode = redis.Redis(host=host, port=port, decode_responses=False)

    ###### initialization
    def _initialize_properties(self):
        super()._initialize_properties()

        # Search configuration
        self.properties['search_bm25_weight'] = 0.3
        self.properties['search_vector_weight'] = 0.7
        # self.properties['search_bm25_max_score'] = 20.0
        self.properties['search_bm25_normalization'] = 'minmax'  # 'linear', 'log', 'minmax'
        self.properties['search_enable_schema'] = True
        # threshold
        self.properties['search_bm25_threshold'] = 0.0
        self.properties['search_vector_threshold'] = 0.5
        self.properties['search_combined_threshold'] = 0.36

        # hierarchical search by chain from children to parent
        self.properties['search_hierarchical_enabled'] = True
        self.properties['search_hierarchical_database_types'] = ['database', 'collection', 'entity']
        self.properties['search_hierarchical_collection_types'] = ['collection', 'entity']

    ######### source
    def register_source(self, source, created_by, description="", properties={}, rebuild=False):
        """
        Register a new data source in the registry.

        Parameters:
            source (str): Unique name or ID of the source.
            created_by (str): Identifier of the user or process creating the source.
            description (str, optional): Optional textual description. Defaults to "".
            properties (dict, optional): Additional metadata or attributes. Defaults to {}.
            rebuild (bool, optional): If True, rebuilds related structures after registration. Defaults to False.
        """
        super().register_record(source, 'source', '/', created_by=created_by, description=description, properties=properties, rebuild=rebuild)

    def update_source(self, source, description=None, icon=None, properties=None, rebuild=False):
        """
        Update an existing data source record.

        Parameters:
            source (str): Source identifier.
            description (str, optional): Updated description. Defaults to None.
            icon (str, optional): Optional icon path or identifier. Defaults to None.
            properties (dict, optional): Updated source properties. Defaults to None.
            rebuild (bool, optional): If True, rebuilds related data structures. Defaults to False.
        """
        super().update_record(source, 'source', '/', description=description, icon=icon, properties=properties, rebuild=rebuild)

    def deregister_source(self, source, rebuild=False):
        """
        Remove a data source from the registry.

        Parameters:
            source (str): Identifier of the source to deregister.
            rebuild (bool, optional): If True, rebuilds related registry structures. Defaults to False.
        """
        record = self.get_source(source)
        super().deregister(record, rebuild=rebuild)

    def get_sources(self):
        """
        Retrieve all registered data sources.

        Returns:
            list: A list of registered source records.
        """
        return super().list_records(type="source", scope="/")

    def get_source(self, source):
        """
        Retrieve a specific data source record by name.

        Parameters:
            source (str): Source identifier.

        Returns:
            dict: Source record details if found.
        """
        return super().get_record(source, 'source', '/')

    # description
    def get_source_description(self, source):
        """
        Retrieve the description of a specific data source.

        Parameters:
            source (str): Source identifier.

        Returns:
            str: The description of the source.
        """
        return super().get_record_description(source, 'source', '/')

    def set_source_description(self, source, description, rebuild=False):
        """
        Update the description for a given data source.

        Parameters:
            source (str): Source identifier.
            description (str): New description text.
            rebuild (bool, optional): Whether to rebuild registry indexes. Defaults to False.
        """
        super().set_record_description(source, 'source', '/', description, rebuild=rebuild)

    # properties
    def get_source_properties(self, source):
        """
        Retrieve all properties associated with a data source.

        Parameters:
            source (str): Source identifier.

        Returns:
            dict: Dictionary of key-value properties for the source.
        """
        return super().get_record_properties(source, 'source', '/')

    def get_source_property(self, source, key):
        """
        Retrieve a single property value for a given source.

        Parameters:
            source (str): Source identifier.
            key (str): Property key.

        Returns:
            Any: The value associated with the given key.
        """
        return super().get_record_property(source, 'source', '/', key)

    def set_source_property(self, source, key, value, rebuild=False):
        """
        Set or update a property for a given source.

        Parameters:
            source (str): Source identifier.
            key (str): Property key.
            value (Any): Property value.
            rebuild (bool, optional): If True, rebuilds related structures. Defaults to False.
        """
        super().set_record_property(source, 'source', '/', key, value, rebuild=rebuild)

    def delete_source_property(self, source, key, rebuild=False):
        """
        Delete a property from a specific source.

        Parameters:
            source (str): Source identifier.
            key (str): Property key to remove.
            rebuild (bool, optional): If True, rebuilds related registry structures. Defaults to False.
        """
        super().delete_record_property(source, 'source', '/', key, rebuild=rebuild)

    ######### source/database
    def register_source_database(self, source, database, description="", properties={}, rebuild=False):
        """
        Register a new database under a specific source in the data registry.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the database to register.
            description (str, optional): A description of the database. Defaults to "".
            properties (dict, optional): Additional properties for the database record. Defaults to {}.
            rebuild (bool, optional): If True, rebuilds the index or structure after registration. Defaults to False.
        """
        super().register_record(database, 'database', f'/source/{source}', description=description, properties=properties, rebuild=rebuild)

    def update_source_database(self, source, database, description=None, properties=None, rebuild=False):
        """
        Update an existing database record under a given source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the database to update.
            description (str, optional): Updated description for the database. Defaults to None.
            properties (dict, optional): Updated properties for the database. Defaults to None.
            rebuild (bool, optional): If True, rebuilds the index or structure after the update. Defaults to False.
        """
        super().update_record(database, 'database', f'/source/{source}', description=description, properties=properties, rebuild=rebuild)

    def deregister_source_database(self, source, database, rebuild=False):
        """
        Deregister (remove) a database record from a specific source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the database to remove.
            rebuild (bool, optional): If True, rebuilds the index or structure after deregistration. Defaults to False.
        """
        record = self.get_source_database(source, database)
        super().deregister(record, rebuild=rebuild)

    def get_source_databases(self, source):
        """
        Retrieve all databases registered under a specific source.

        Parameters:
            source (str): The name or ID of the parent source.

        Returns:
            list: A list of database records registered under the source.
        """
        return super().filter_record_contents(source, 'source', '/', filter_type='database')

    def get_source_database(self, source, database):
        """
        Retrieve a specific database record under a given source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the database to fetch.

        Returns:
            dict: The database record details if found, otherwise None.
        """
        return super().filter_record_contents(source, 'source', '/', filter_type='database', filter_name=database, single=True)

    # description
    def get_source_database_description(self, source, database):
        """
        Get the description text of a specific database under a given source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the database.

        Returns:
            str: The description of the database.
        """
        return super().get_record_description(database, 'database', f'/source/{source}')

    def set_source_database_description(self, source, database, description, rebuild=False):
        """
        Set or update the description of a specific database under a given source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the database.
            description (str): The new description text for the database.
            rebuild (bool, optional): If True, rebuilds the index or structure after update. Defaults to False.
        """
        super().set_record_description(database, 'database', f'/source/{source}', description, rebuild=rebuild)

    # properties
    def get_source_database_properties(self, source, database):
        """
        Get all properties associated with a specific database under a given source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the database.

        Returns:
            dict: A dictionary of property key-value pairs.
        """
        return super().get_record_properties(database, 'database', f'/source/{source}')

    def get_source_database_property(self, source, database, key):
        """
        Retrieve a single property value for a specific database under a given source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the database.
            key (str): The property key to look up.

        Returns:
            Any: The value of the specified property key.
        """
        return super().get_record_property(database, 'database', f'/source/{source}', key)

    def set_source_database_property(self, source, database, key, value, rebuild=False):
        """
        Set or update a property for a specific database under a given source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the database.
            key (str): The property key.
            value (Any): The value to assign to the property.
            rebuild (bool, optional): If True, rebuilds the index or structure after the update. Defaults to False.
        """
        super().set_record_property(database, 'database', f'/source/{source}', key, value, rebuild=rebuild)

    ######### source/database/collection
    def register_source_database_collection(self, source, database, collection, description="", properties={}, rebuild=False):
        """
        Register a new collection under a specific database and source in the data registry.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the parent database.
            collection (str): The name or ID of the collection to register.
            description (str, optional): A description of the collection. Defaults to "".
            properties (dict, optional): Additional properties for the collection record. Defaults to {}.
            rebuild (bool, optional): If True, rebuilds the index or structure after registration. Defaults to False.
        """
        super().register_record(collection, 'collection', f'/source/{source}/database/{database}', description=description, properties=properties, rebuild=rebuild)

    def update_source_database_collection(self, source, database, collection, description=None, properties=None, rebuild=False):
        """
        Update an existing collection record under a given database and source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the parent database.
            collection (str): The name or ID of the collection to update.
            description (str, optional): Updated description for the collection. Defaults to None.
            properties (dict, optional): Updated properties for the collection. Defaults to None.
            rebuild (bool, optional): If True, rebuilds the index or structure after update. Defaults to False.

        Returns:
            tuple: A tuple (original_record, merged_record) representing the record before and after the update.
        """
        original_record, merged_record = super().update_record(
            collection, 'collection', f'/source/{source}/database/{database}', description=description, properties=properties, rebuild=rebuild
        )
        return original_record, merged_record

    def deregister_source_database_collection(self, source, database, collection, rebuild=False):
        """
        Deregister (remove) a collection record from a specific database and source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the parent database.
            collection (str): The name or ID of the collection to remove.
            rebuild (bool, optional): If True, rebuilds the index or structure after deregistration. Defaults to False.
        """
        record = self.get_source_database_collection(source, database, collection)
        super().deregister(record, rebuild=rebuild)

    def get_source_database_collections(self, source, database):
        """
        Retrieve all collections registered under a specific database and source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the parent database.

        Returns:
            list: A list of collection records registered under the database.
        """
        return super().filter_record_contents(database, 'database', f'/source/{source}', filter_type='collection')

    def get_source_database_collection(self, source, database, collection):
        """
        Retrieve a specific collection record under a given database and source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the parent database.
            collection (str): The name or ID of the collection to fetch.

        Returns:
            dict: The collection record details if found, otherwise None.
        """
        return super().filter_record_contents(database, 'database', f'/source/{source}', filter_type='collection', filter_name=collection, single=True)

    # description
    def get_source_database_collection_description(self, source, database, collection):
        """
        Get the description text of a specific collection under a given database and source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the parent database.
            collection (str): The name or ID of the collection.

        Returns:
            str: The description of the collection.
        """
        return super().get_record_description(collection, 'collection', f'/source/{source}/database/{database}')

    def set_source_database_collection_description(self, source, database, collection, description, rebuild=False):
        """
        Set or update the description of a specific collection under a given database and source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the parent database.
            collection (str): The name or ID of the collection.
            description (str): The new description text for the collection.
            rebuild (bool, optional): If True, rebuilds the index or structure after update. Defaults to False.
        """
        super().set_record_description(collection, 'collection', f'/source/{source}/database/{database}', description, rebuild=rebuild)

    # properties
    def get_source_database_collection_properties(self, source, database, collection):
        """
        Get all properties associated with a specific collection under a given database and source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the parent database.
            collection (str): The name or ID of the collection.

        Returns:
            dict: A dictionary of property key-value pairs.
        """
        return super().get_record_properties(collection, 'collection', f'/source/{source}/database/{database}')

    def get_source_database_collection_property(self, source, database, collection, key):
        """
        Retrieve a single property value for a specific collection under a given database and source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the parent database.
            collection (str): The name or ID of the collection.
            key (str): The property key to look up.

        Returns:
            Any: The value of the specified property key.
        """
        return super().get_record_property(collection, 'collection', f'/source/{source}/database/{database}', key)

    def set_source_database_collection_property(self, source, database, collection, key, value, rebuild=False):
        """
        Set or update a property for a specific collection under a given database and source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the parent database.
            collection (str): The name or ID of the collection.
            key (str): The property key.
            value (Any): The value to assign to the property.
            rebuild (bool, optional): If True, rebuilds the index or structure after the update. Defaults to False.
        """
        super().set_record_property(collection, 'collection', f'/source/{source}/database/{database}', key, value, rebuild=rebuild)

    ######### source/database/collection/entity
    def register_source_database_collection_entity(self, source, database, collection, entity, description="", properties={}, rebuild=False):
        """
        Register a new entity under a specific collection, database, and source in the data registry.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the parent database.
            collection (str): The name or ID of the parent collection.
            entity (str): The name or ID of the entity to register.
            description (str, optional): A description of the entity. Defaults to "".
            properties (dict, optional): Additional properties for the entity record. Defaults to {}.
            rebuild (bool, optional): If True, rebuilds the index or structure after registration. Defaults to False.
        """
        super().register_record(entity, 'entity', f'/source/{source}/database/{database}/collection/{collection}', description=description, properties=properties, rebuild=rebuild)

    def update_source_database_collection_entity(self, source, database, collection, entity, description=None, properties=None, rebuild=False):
        """
        Update an existing entity record under a specific collection, database, and source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the parent database.
            collection (str): The name or ID of the parent collection.
            entity (str): The name or ID of the entity to update.
            description (str, optional): Updated description for the entity. Defaults to None.
            properties (dict, optional): Updated properties for the entity. Defaults to None.
            rebuild (bool, optional): If True, rebuilds the index or structure after update. Defaults to False.

        Returns:
            tuple: A tuple (original_record, merged_record) representing the record before and after the update.
        """
        original_record, merged_record = super().update_record(
            entity, 'entity', f'/source/{source}/database/{database}/collection/{collection}', description=description, properties=properties, rebuild=rebuild
        )
        return original_record, merged_record

    def deregister_source_database_collection_entity(self, source, database, collection, entity, rebuild=False):
        """
        Deregister (remove) an entity record from a specific collection, database, and source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the parent database.
            collection (str): The name or ID of the parent collection.
            entity (str): The name or ID of the entity to remove.
            rebuild (bool, optional): If True, rebuilds the index or structure after deregistration. Defaults to False.
        """
        record = self.get_source_database_collection_entity(source, database, collection, entity)
        super().deregister(record, rebuild=rebuild)

    def get_source_database_collection_entities(self, source, database, collection):
        """
        Retrieve all entities registered under a specific collection, database, and source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the parent database.
            collection (str): The name or ID of the parent collection.

        Returns:
            list: A list of entity records registered under the specified collection.
        """
        return super().filter_record_contents(collection, 'collection', f'/source/{source}/database/{database}', filter_type='entity')

    def get_source_database_collection_entity(self, source, database, collection, entity):
        """
        Retrieve a specific entity record under a given collection, database, and source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the parent database.
            collection (str): The name or ID of the parent collection.
            entity (str): The name or ID of the entity to fetch.

        Returns:
            dict: The entity record details if found, otherwise None.
        """
        return super().filter_record_contents(collection, 'collection', f'/source/{source}/database/{database}', filter_type='entity', filter_name=entity, single=True)

    # description
    def get_source_database_collection_entity_description(self, source, database, collection, entity):
        """
        Get the description text of a specific entity under a given collection, database, and source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the parent database.
            collection (str): The name or ID of the parent collection.
            entity (str): The name or ID of the entity.

        Returns:
            str: The description of the entity.
        """
        return super().get_record_description(entity, 'entity', f'/source/{source}/database/{database}/collection/{collection}')

    def set_source_database_collection_entity_description(self, source, database, collection, entity, description, rebuild=False):
        """
        Set or update the description of a specific entity under a given collection, database, and source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the parent database.
            collection (str): The name or ID of the parent collection.
            entity (str): The name or ID of the entity.
            description (str): The new description text for the entity.
            rebuild (bool, optional): If True, rebuilds the index or structure after update. Defaults to False.
        """
        super().set_record_description(entity, 'entity', f'/source/{source}/database/{database}/collection/{collection}', description, rebuild=rebuild)

    # properties
    def get_source_database_collection_entity_properties(self, source, database, collection, entity):
        """
        Get all properties associated with a specific entity under a given collection, database, and source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the parent database.
            collection (str): The name or ID of the parent collection.
            entity (str): The name or ID of the entity.

        Returns:
            dict: A dictionary of property key-value pairs.
        """
        return super().get_record_properties(entity, 'entity', f'/source/{source}/database/{database}/collection/{collection}')

    def get_source_database_collection_entity_property(self, source, database, collection, entity, key):
        """
        Retrieve a single property value for a specific entity under a given collection, database, and source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the parent database.
            collection (str): The name or ID of the parent collection.
            entity (str): The name or ID of the entity.
            key (str): The property key to look up.

        Returns:
            Any: The value of the specified property key.
        """
        return super().get_record_property(entity, 'entity', f'/source/{source}/database/{database}/collection/{collection}', key)

    def set_source_database_collection_entity_property(self, source, database, collection, entity, key, value, rebuild=False):
        """
        Set or update a property for a specific entity under a given collection, database, and source.

        Parameters:
            source (str): The name or ID of the parent source.
            database (str): The name or ID of the parent database.
            collection (str): The name or ID of the parent collection.
            entity (str): The name or ID of the entity.
            key (str): The property key.
            value (Any): The value to assign to the property.
            rebuild (bool, optional): If True, rebuilds the index or structure after the update. Defaults to False.
        """
        super().set_record_property(entity, 'entity', f'/source/{source}/database/{database}/collection/{collection}', key, value, rebuild=rebuild)

    ######### source/database/collection/entity/attribute
    def register_source_database_collection_entity_attribute(self, source, database, collection, entity, attribute, description="", properties=None, rebuild=False):
        """
        Register a new attribute under a specific entity within a collection, database, and source.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database under the source.
            collection (str): Name of the collection under the database.
            entity (str): Name of the entity under the collection.
            attribute (str): Name of the attribute to register.
            description (str, optional): Description of the attribute.
            properties (dict, optional): Properties for the attribute.
            rebuild (bool, optional): Whether to rebuild dependent data structures after registration.
        """
        if properties is None:
            properties = {}
        scope = f'/source/{source}/database/{database}/collection/{collection}/entity/{entity}'

        super().register_record(attribute, 'attribute', scope, description=description, properties=properties, rebuild=rebuild)

    def update_source_database_collection_entity_attribute(self, source, database, collection, entity, attribute, description=None, properties=None, rebuild=False):
        """
        Update an existing attribute under a specific entity.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database under the source.
            collection (str): Name of the collection under the database.
            entity (str): Name of the entity under the collection.
            attribute (str): Name of the attribute to update.
            description (str, optional): New description for the attribute.
            properties (dict, optional): Updated properties for the attribute.
            rebuild (bool, optional): Whether to rebuild dependent data structures after update.

        Returns:
            tuple: (original_record, merged_record) containing the state before and after update.
        """
        scope = f'/source/{source}/database/{database}/collection/{collection}/entity/{entity}'
        return super().update_record(attribute, 'attribute', scope, description=description, properties=properties, rebuild=rebuild)

    def deregister_source_database_collection_entity_attribute(self, source, database, collection, entity, attribute, rebuild=False):
        """
        Remove an attribute from a specific entity.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database under the source.
            collection (str): Name of the collection under the database.
            entity (str): Name of the entity under the collection.
            attribute (str): Name of the attribute to deregister.
            rebuild (bool, optional): Whether to rebuild dependent data structures after deregistration.
        """
        record = self.get_source_database_collection_entity_attribute(source, database, collection, entity, attribute)
        super().deregister(record, rebuild=rebuild)

    def get_source_database_collection_entity_attributes(self, source, database, collection, entity):
        """
        Retrieve all attributes under a specific entity.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database under the source.
            collection (str): Name of the collection under the database.
            entity (str): Name of the entity under the collection.

        Returns:
            list: List of attributes under the entity.
        """
        scope = f'/source/{source}/database/{database}/collection/{collection}'
        return super().filter_record_contents(entity, 'entity', scope, filter_type='attribute')

    def get_source_database_collection_entity_attribute(self, source, database, collection, entity, attribute):
        """
        Retrieve a specific attribute under an entity.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database under the source.
            collection (str): Name of the collection under the database.
            entity (str): Name of the entity under the collection.
            attribute (str): Name of the attribute to retrieve.

        Returns:
            dict: Attribute record if found, else None.
        """
        scope = f'/source/{source}/database/{database}/collection/{collection}'
        return super().filter_record_contents(entity, 'entity', scope, filter_type='attribute', filter_name=attribute, single=True)

    def set_source_database_collection_entity_attribute_property(self, source, database, collection, entity, attribute, key, value, rebuild=False):
        """
        Set or update a specific property of an attribute.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database under the source.
            collection (str): Name of the collection under the database.
            entity (str): Name of the entity under the collection.
            attribute (str): Name of the attribute.
            key (str): Property key to set.
            value (Any): Property value to set.
            rebuild (bool, optional): Whether to rebuild dependent data structures after update.
        """
        scope = f'/source/{source}/database/{database}/collection/{collection}/entity/{entity}'
        super().set_record_property(attribute, 'attribute', scope, key, value, rebuild=rebuild)

    def get_source_database_collection_entity_attribute_property(self, source, database, collection, entity, attribute, key):
        """
        Retrieve a specific property of an attribute.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database under the source.
            collection (str): Name of the collection under the database.
            entity (str): Name of the entity under the collection.
            attribute (str): Name of the attribute.
            key (str): Property key to retrieve.

        Returns:
            Any: Value of the requested property.
        """
        scope = f'/source/{source}/database/{database}/collection/{collection}/entity/{entity}'
        return super().get_record_property(attribute, 'attribute', scope, key)

    # description
    def get_source_database_collection_entity_attribute_description(self, source, database, collection, entity, attribute):
        """
        Get the description of a specific attribute.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database under the source.
            collection (str): Name of the collection under the database.
            entity (str): Name of the entity under the collection.
            attribute (str): Name of the attribute.

        Returns:
            str: Description of the attribute.
        """
        return super().get_record_description(attribute, 'attribute', f'/source/{source}/database/{database}/collection/{collection}/entity/{entity}')

    def set_source_database_collection_entity_attribute_description(self, source, database, collection, entity, attribute, description, rebuild=False):
        """
        Set or update the description of a specific attribute.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database under the source.
            collection (str): Name of the collection under the database.
            entity (str): Name of the entity under the collection.
            attribute (str): Name of the attribute.
            description (str): Description to set.
            rebuild (bool, optional): Whether to rebuild dependent data structures after update.
        """
        super().set_record_description(attribute, 'attribute', f'/source/{source}/database/{database}/collection/{collection}/entity/{entity}', description, rebuild=rebuild)

    ######### source/database/collection/relation
    def register_source_database_collection_relation(self, source, database, collection, relation, description="", properties={}, rebuild=False):
        """
        Register a new relation under a specific collection in a database and source.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database under the source.
            collection (str): Name of the collection under the database.
            relation (str): Name of the relation to register.
            description (str, optional): Description of the relation.
            properties (dict, optional): Properties for the relation.
            rebuild (bool, optional): Whether to rebuild dependent data structures after registration.
        """
        super().register_record(relation, 'relation', f'/source/{source}/database/{database}/collection/{collection}', description=description, properties=properties, rebuild=rebuild)

    def update_source_database_collection_relation(self, source, database, collection, relation, description=None, properties=None, rebuild=False):
        """
        Update an existing relation under a specific collection.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database under the source.
            collection (str): Name of the collection under the database.
            relation (str): Name of the relation to update.
            description (str, optional): New description for the relation.
            properties (dict, optional): Updated properties for the relation.
            rebuild (bool, optional): Whether to rebuild dependent data structures after update.

        Returns:
            tuple: (original_record, merged_record) containing the state before and after update.
        """
        original_record, merged_record = super().update_record(
            relation, 'relation', f'/source/{source}/database/{database}/collection/{collection}', description=description, properties=properties, rebuild=rebuild
        )
        return original_record, merged_record

    def deregister_source_database_collection_relation(self, source, database, collection, relation, rebuild=False):
        """
        Remove a relation from a specific collection.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database under the source.
            collection (str): Name of the collection under the database.
            relation (str): Name of the relation to deregister.
            rebuild (bool, optional): Whether to rebuild dependent data structures after deregistration.
        """
        record = self.get_source_database_collection_relation(source, database, collection, relation)
        super().deregister(record, rebuild=rebuild)

    def get_source_database_collection_relations(self, source, database, collection):
        """
        Retrieve all relations under a specific collection.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database under the source.
            collection (str): Name of the collection under the database.

        Returns:
            list: List of relations under the collection.
        """
        return super().filter_record_contents(collection, 'collection', f'/source/{source}/database/{database}', filter_type='relation')

    def get_source_database_collection_relation(self, source, database, collection, relation):
        """
        Retrieve a specific relation under a collection.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database under the source.
            collection (str): Name of the collection under the database.
            relation (str): Name of the relation to retrieve.

        Returns:
            dict: Relation record if found, else None.
        """
        return super().filter_record_contents(collection, 'collection', f'/source/{source}/database/{database}', filter_type='relation', filter_name=relation, single=True)

    # description
    def get_source_database_collection_relation_description(self, source, database, collection, relation):
        """
        Get the description of a specific relation.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database under the source.
            collection (str): Name of the collection under the database.
            relation (str): Name of the relation.

        Returns:
            str: Description of the relation.
        """
        return super().get_record_description(relation, 'relation', f'/source/{source}/database/{database}/collection/{collection}')

    def set_source_database_collection_relation_description(self, source, database, collection, relation, description, rebuild=False):
        """
        Set or update the description of a specific relation.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database under the source.
            collection (str): Name of the collection under the database.
            relation (str): Name of the relation.
            description (str): Description to set.
            rebuild (bool, optional): Whether to rebuild dependent data structures after update.
        """
        super().set_record_description(relation, 'relation', f'/source/{source}/database/{database}/collection/{collection}', description, rebuild=rebuild)

    # properties
    def get_source_database_collection_relation_properties(self, source, database, collection, relation):
        """
        Retrieve all properties of a specific relation.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database under the source.
            collection (str): Name of the collection under the database.
            relation (str): Name of the relation.

        Returns:
            dict: Properties of the relation.
        """
        return super().get_record_properties(relation, 'relation', f'/source/{source}/database/{database}/collection/{collection}')

    def get_source_database_collection_relation_property(self, source, database, collection, relation, key):
        """
        Retrieve a specific property of a relation.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database under the source.
            collection (str): Name of the collection under the database.
            relation (str): Name of the relation.
            key (str): Property key to retrieve.

        Returns:
            Any: Value of the requested property.
        """
        return super().get_record_property(relation, 'relation', f'/source/{source}/database/{database}/collection/{collection}', key)

    def set_source_database_collection_relation_property(self, source, database, collection, relation, key, value, rebuild=False):
        """
        Set or update a specific property of a relation.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database under the source.
            collection (str): Name of the collection under the database.
            relation (str): Name of the relation.
            key (str): Property key to set.
            value (Any): Property value to set.
            rebuild (bool, optional): Whether to rebuild dependent data structures after update.
        """
        super().set_record_property(relation, 'relation', f'/source/{source}/database/{database}/collection/{collection}', key, value, rebuild=rebuild)

    ######### source/database/collection/relation/attribute
    def register_source_database_collection_relation_attribute(self, source, database, collection, relation, attribute, description="", properties={}, rebuild=False):
        """
        Register a new attribute under a specific relation.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database.
            collection (str): Name of the collection.
            relation (str): Name of the relation.
            attribute (str): Name of the attribute to register.
            description (str, optional): Description of the attribute.
            properties (dict, optional): Properties for the attribute.
            rebuild (bool, optional): Whether to rebuild dependent data structures after registration.
        """
        super().register_record(
            attribute, 'attribute', f'/source/{source}/database/{database}/collection/{collection}/relation/{relation}', description=description, properties=properties, rebuild=rebuild
        )

    def update_source_database_collection_relation_attribute(self, source, database, collection, relation, attribute, description=None, properties=None, rebuild=False):
        """
        Update an existing attribute under a specific relation.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database.
            collection (str): Name of the collection.
            relation (str): Name of the relation.
            attribute (str): Name of the attribute to update.
            description (str, optional): New description for the attribute.
            properties (dict, optional): Updated properties for the attribute.
            rebuild (bool, optional): Whether to rebuild dependent data structures after update.

        Returns:
            tuple: (original_record, merged_record) containing the state before and after update.
        """
        scope = f'/source/{source}/database/{database}/collection/{collection}/relation/{relation}'
        return super().update_record(attribute, 'attribute', scope, description=description, properties=properties, rebuild=rebuild)

    def deregister_source_database_collection_relation_attribute(self, source, database, collection, relation, attribute, rebuild=False):
        """
        Remove an attribute from a specific relation.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database.
            collection (str): Name of the collection.
            relation (str): Name of the relation.
            attribute (str): Name of the attribute to deregister.
            rebuild (bool, optional): Whether to rebuild dependent data structures after deregistration.
        """
        record = self.get_source_database_collection_relation_attribute(source, database, collection, relation, attribute)
        super().deregister(record, rebuild=rebuild)

    def get_source_database_collection_relation_attributes(self, source, database, collection, relation):
        """
        Retrieve all attributes under a specific relation.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database.
            collection (str): Name of the collection.
            relation (str): Name of the relation.

        Returns:
            list: List of attributes under the relation.
        """
        scope = f'/source/{source}/database/{database}/collection/{collection}/relation/{relation}'
        return super().filter_record_contents(relation, 'relation', scope, filter_type='attribute')

    def get_source_database_collection_relation_attribute(self, source, database, collection, relation, attribute):
        """
        Retrieve a specific attribute under a relation.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database.
            collection (str): Name of the collection.
            relation (str): Name of the relation.
            attribute (str): Name of the attribute.

        Returns:
            dict: Attribute record if found, else None.
        """
        scope = f'/source/{source}/database/{database}/collection/{collection}/relation/{relation}'
        return super().filter_record_contents(relation, 'relation', scope, filter_type='attribute', filter_name=attribute, single=True)

    def set_source_database_collection_relation_attribute_property(self, source, database, collection, relation, attribute, key, value, rebuild=False):
        """
        Set or update a specific property of a relation attribute.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database.
            collection (str): Name of the collection.
            relation (str): Name of the relation.
            attribute (str): Name of the attribute.
            key (str): Property key to set.
            value (Any): Property value to set.
            rebuild (bool, optional): Whether to rebuild dependent data structures after update.
        """
        scope = f'/source/{source}/database/{database}/collection/{collection}/relation/{relation}'
        super().set_record_property(attribute, 'attribute', scope, key, value, rebuild=rebuild)

    def get_source_database_collection_relation_attribute_property(self, source, database, collection, relation, attribute, key):
        """
        Retrieve a specific property of a relation attribute.

        Parameters:
            source (str): Name of the source.
            database (str): Name of the database.
            collection (str): Name of the collection.
            relation (str): Name of the relation.
            attribute (str): Name of the attribute.
            key (str): Property key to retrieve.

        Returns:
            Any: Value of the requested property.
        """
        scope = f'/source/{source}/database/{database}/collection/{collection}/relation/{relation}'
        return super().get_record_property(attribute, 'attribute', scope, key)

    ######### sync
    # source connection (part of properties)
    def get_source_connection(self, source):
        """
        Retrieve the connection information for a specific source.

        Parameters:
            source (str): Name of the source.

        Returns:
            Any: The connection information stored in the source's properties.
        """
        return self.get_source_property(source, 'connection')

    def set_source_connection(self, source, connection, rebuild=False):
        """
        Set or update the connection information for a specific source.

        Parameters:
            source (str): Name of the source.
            connection (Any): Connection information to set (e.g., connection string or config dict).
            rebuild (bool, optional): Whether to rebuild dependent data structures after updating the connection.
        """
        self.set_source_property(source, 'connection', connection, rebuild=rebuild)

    def connect_source(self, source):
        """
        Establish a connection to the specified data source based on its configuration.

        Determines the source protocol (e.g., MongoDB, Postgres, MySQL, etc.) from its
        stored properties and initializes the corresponding source connector class.

        Parameters:
            source (str): Identifier of the data source to connect to.

        Returns:
            BaseSource | None: An instance of the appropriate source connector if a
            matching protocol is found, otherwise None.
        """
        source_connection = None

        properties = self.get_source_properties(source)

        if properties:
            if 'connection' in properties:
                connection_properties = properties["connection"]

                protocol = connection_properties["protocol"]
                if protocol:
                    if protocol == "mongodb":
                        source_connection = MongoDBSource(source, properties=properties)
                    elif protocol == "bolt":
                        source_connection = NEO4JSource(source, properties=properties)
                    elif protocol == "postgres":
                        source_connection = PostgresDBSource(source, properties=properties)
                    elif protocol == "mysql":
                        source_connection = MySQLDBSource(source, properties=properties)
                    elif protocol == "sqlite":
                        source_connection = SQLiteDBSource(source, properties=properties)
                    elif protocol == "openai":
                        source_connection = OpenAISource(source, properties=properties)

        return source_connection

    def execute_query(self, query, source, database=None, collection=None, optional_properties={}):
        """Execute a query against a data source. Currently separate for OpenAI and other sources."""
        # Connect to the source
        source_connection = self.connect_source(source)
        if source_connection:
            return source_connection.execute_query(query=query, database=database, collection=collection, optional_properties=optional_properties)
        return None

    ######### create operations
    def create_source_database(self, source, database, properties={}, overwrite=False, rebuild=True, recursive=False):
        """
        Create a new database in the specified source.

        Parameters:
            source (str): Source name or identifier.
            database (str): Database name.
            properties (dict, optional): Properties to set on the database. Defaults to {}.
            overwrite (bool, optional): Overwrite existing database if it exists. Defaults to False.
            rebuild (bool, optional): Rebuild registry index after creation. Defaults to True.
            recursive (bool, optional): Recurse into sub-objects when syncing. Defaults to False.

        Returns:
            None
        """
        source_connection = self.connect_source(source)
        if source_connection:
            # check if database already exists in registry
            if self.get_source_database(source, database):
                if overwrite:
                    self.deregister_source_database(source, database, rebuild=rebuild)
                    # TODO: deregister recursively
                else:
                    return None
            create_res = source_connection.create_database(database, properties=properties, overwrite=overwrite)
            if create_res and create_res['status'] in ["success", "registry_only"]:
                self.sync_source(source, rebuild=rebuild, recursive=recursive)
                # update database properties if provided
                for key, value in properties.items():
                    self.set_source_database_property(source, database, key, value, rebuild=rebuild)
        return None

    def create_source_database_collection(self, source, database, collection, properties={}, overwrite=False, rebuild=True, recursive=False):
        """
        Create a new collection in the specified database.

        Parameters:
            source (str): Source name or identifier.
            database (str): Database name.
            collection (str): Collection name.
            properties (dict, optional): Properties to set on the collection. Defaults to {}.
            overwrite (bool, optional): Overwrite existing collection if it exists. Defaults to False.
            rebuild (bool, optional): Rebuild registry index after creation. Defaults to True.
            recursive (bool, optional): Recurse into sub-objects when syncing. Defaults to False.

        Returns:
            None
        """
        source_connection = self.connect_source(source)
        if source_connection:
            # check if collection already exists in registry
            if self.get_source_database_collection(source, database, collection):
                if overwrite:
                    self.deregister_source_database_collection(source, database, collection, rebuild=rebuild)
                    # TODO: deregister recursively
                else:
                    return None
            create_res = source_connection.create_database_collection(database, collection, properties=properties, overwrite=overwrite)
            if create_res and create_res['status'] in ["success", "registry_only"]:
                self.sync_source_database(source, database, rebuild=rebuild, recursive=recursive)
                # update collection properties if provided
                for key, value in properties.items():
                    self.set_source_database_collection_property(source, database, collection, key, value, rebuild=rebuild)
        return None

    def create_source_database_collection_entity(self, source, database, collection, entity, properties={}, creation_properties={}, overwrite=False, rebuild=True, recursive=False):
        """
        Create a new entity (table) in the specified collection.

        Parameters:
            source (str): Source name or identifier.
            database (str): Database name.
            collection (str): Collection name.
            entity (str): Entity (table) name.
            properties (dict, optional): Properties to set on the entity. Defaults to {}.
            creation_properties (dict, optional): Properties for initial creation. Defaults to {}.
            overwrite (bool, optional): Overwrite existing entity if it exists. Defaults to False.
            rebuild (bool, optional): Rebuild registry index after creation. Defaults to True.
            recursive (bool, optional): Recurse into sub-objects when syncing. Defaults to False.

        Returns:
            None
        """
        source_connection = self.connect_source(source)
        if source_connection:
            # check if entity already exists in registry
            if self.get_source_database_collection_entity(source, database, collection, entity):
                if overwrite:
                    self.deregister_source_database_collection_entity(source, database, collection, entity, rebuild=rebuild)
                    # TODO: deregister recursively
                else:
                    return None
            create_res = source_connection.create_database_collection_entity(database, collection, entity, properties=creation_properties, overwrite=overwrite)
            if create_res and create_res['status'] in ["success", "registry_only"]:
                # currently sync is not supported for entity, so we sync the collection instead
                self.sync_source_database_collection(source, database, collection, rebuild=rebuild, recursive=recursive)
                # update entity properties if provided
                for key, value in properties.items():
                    self.set_source_database_collection_entity_property(source, database, collection, entity, key, value, rebuild=rebuild)
        return None

    def create_source_database_collection_relation(self, source, database, collection, relation, properties={}, overwrite=False, rebuild=True, recursive=False):
        """
        Create a new relation in the specified collection.

        Parameters:
            source (str): Source name or identifier.
            database (str): Database name.
            collection (str): Collection name.
            relation (str): Relation name.
            properties (dict, optional): Properties to set on the relation. Defaults to {}.
            overwrite (bool, optional): Overwrite existing relation if it exists. Defaults to False.
            rebuild (bool, optional): Rebuild registry index after creation. Defaults to True.
            recursive (bool, optional): Recurse into sub-objects when syncing. Defaults to False.

        Returns:
            None
        """
        source_connection = self.connect_source(source)
        if source_connection:
            # check if relation already exists in registry
            if self.get_source_database_collection_relation(source, database, collection, relation):
                if overwrite:
                    self.deregister_source_database_collection_relation(source, database, collection, relation, rebuild=rebuild)
                else:
                    return None
            create_res = source_connection.create_database_collection_relation(database, collection, relation, properties=properties, overwrite=overwrite)
            if create_res and create_res['status'] in ["success", "registry_only"]:
                # currently sync is not supported for relation, so we sync the collection instead
                self.sync_source_database_collection(source, database, collection, rebuild=rebuild, recursive=recursive)
                # update relation properties if provided
                for key, value in properties.items():
                    self.set_source_database_collection_relation_property(source, database, collection, relation, key, value, rebuild=rebuild)
        return None

    def collect_source_stats(self, source, recursive=False, rebuild=False):
        """
        Collect statistics for a data source and optionally its databases.

        Parameters:
            source (str): Source name or identifier.
            recursive (bool, optional): Collect stats recursively for all databases. Defaults to False.
            rebuild (bool, optional): Rebuild registry index after collecting stats. Defaults to False.

        Returns:
            None
        """
        source_connection = self.connect_source(source)
        if source_connection:
            source_stats = source_connection.fetch_source_stats()
            if source_stats:
                self.set_source_property(source, "stats", source_stats, rebuild=rebuild)
            if recursive:
                databases = self.get_source_databases(source)
                for database in databases:
                    self.collect_source_database_stats(source, database, source_connection, recursive=recursive, rebuild=rebuild)

    def collect_source_database_stats(self, source, database, source_connection=None, recursive=False, rebuild=False):
        """
        Collect statistics for a database and optionally its collections.

        Parameters:
            source (str): Source name or identifier.
            database (str): Database name.
            source_connection (object, optional): Pre-existing connection to source. Defaults to None.
            recursive (bool, optional): Collect stats recursively for all collections. Defaults to False.
            rebuild (bool, optional): Rebuild registry index after collecting stats. Defaults to False.

        Returns:
            None
        """
        if source_connection is None:
            source_connection = self.connect_source(source)
        if source_connection:
            db_stats = source_connection.fetch_database_stats(database)
            if db_stats:
                self.set_source_database_property(source, database, "stats", db_stats, rebuild=rebuild)

            if recursive:
                collections = self.get_source_database_collections(source, database)
                for collection in collections:
                    self.collect_source_database_collection_stats(source, database, collection, source_connection, recursive=recursive, rebuild=rebuild)

    def collect_source_database_collection_stats(self, source, database, collection, source_connection=None, recursive=False, rebuild=False, sample_limit=10):
        """
        Collect statistics for a collection, its entities, relations, and attributes.

        Parameters:
            source (str): Source name or identifier.
            database (str): Database name.
            collection (str): Collection name.
            source_connection (object, optional): Pre-existing connection to source. Defaults to None.
            recursive (bool, optional): Collect stats recursively for entities and relations. Defaults to False.
            rebuild (bool, optional): Rebuild registry index after collecting stats. Defaults to False.
            sample_limit (int, optional): Maximum number of samples for attribute stats. Defaults to 10.

        Returns:
            None
        """
        entities = self.get_source_database_collection_entities(source, database, collection)
        relations = self.get_source_database_collection_relations(source, database, collection)

        if entities is None:
            entities = []

        if relations is None:
            relations = []

        if source_connection is None:
            source_connection = self.connect_source(source)
        if source_connection:

            collection_stats = source_connection.fetch_collection_stats(database, collection, entities, relations)

            if collection_stats:
                self.set_source_database_collection_property(source, database, collection, "stats", collection_stats, rebuild=rebuild)

            if entities:
                for entity_dict in entities:
                    entity = entity_dict.get("name")

                    ent_stats = source_connection.fetch_entity_stats(database, collection, entity)

                    self.set_source_database_collection_entity_property(source, database, collection, entity, "stats", ent_stats, rebuild=rebuild)

                    contents = entity_dict.get("contents", {})
                    attributes = contents.get("attribute", {})

                    for attr_name, attr_info in attributes.items():
                        attr_stats = source_connection.fetch_property_stats(database, collection, entity, attr_name, sample_limit=sample_limit)

                        # Store stats under this attribute
                        self.set_source_database_collection_entity_attribute_property(source, database, collection, entity, attr_name, "stats", attr_stats, rebuild=rebuild)

    ### currerntly, data.py doesn't call sync_all
    def sync_all(self, recursive=False, rebuild=False):
        """
        Synchronize all sources with the registry.

        Parameters:
            recursive (bool, optional): If True, recursively sync databases and collections. Defaults to False.
            rebuild (bool, optional): If True, rebuild the registry index after syncing. Defaults to False.

        Returns:
            None
        """
        sources = self.get_sources()
        for source in sources:
            source_name = source.get('name')
            if source_name:
                self.sync_source(source_name, recursive=recursive, rebuild=rebuild)

    def sync_source(self, source, recursive=False, rebuild=False):
        """
        Synchronize a single source with the registry.

        This updates the source metadata, adds new databases, removes missing databases,
        merges existing ones, and optionally recurses into database syncing.

        Parameters:
            source (str): Source name or identifier.
            recursive (bool, optional): If True, recursively sync databases and collections. Defaults to False.
            rebuild (bool, optional): If True, rebuild the registry index after syncing. Defaults to False.

        Returns:
            None
        """
        source_connection = self.connect_source(source)
        if source_connection:
            # fetch source metadata
            metadata = source_connection.fetch_metadata()

            # update source properties
            properties = {}
            properties['metadata'] = metadata
            description = ""
            if 'description' in metadata:
                description = metadata['description']

            current_description = self.get_source_description(source)

            if description.strip() and metadata:
                if not current_description or current_description.strip() == "":
                    self.update_source(source, description=description, properties=properties, rebuild=rebuild)
                else:
                    self.update_source(source, description=current_description, properties=properties, rebuild=rebuild)

            # fetch databases
            fetched_dbs = source_connection.fetch_databases()
            fetched_dbs_set = set(fetched_dbs)

            # get existing databases
            registry_dbs = self.get_source_databases(source)
            registry_dbs_set = set(json_utils.json_query(registry_dbs, '$[*].name', single=False))

            adds = set()
            removes = set()
            merges = set()

            ## compute add / remove / merge
            for db in fetched_dbs_set:
                if db in registry_dbs_set:
                    merges.add(db)
                else:
                    adds.add(db)
            for db in registry_dbs_set:
                if db not in fetched_dbs_set:
                    removes.add(db)

            # update registry
            # add
            for db in adds:
                self.register_source_database(source, db, description="", properties={}, rebuild=rebuild)

            # remove
            for db in removes:
                self.deregister_source_database(source, db, rebuild=rebuild)

            ## recurse
            if recursive:
                for db in fetched_dbs_set:
                    self.sync_source_database(source, db, source_connection=source_connection, recursive=recursive, rebuild=rebuild)
            else:
                for db in adds:
                    #  sync to update description, properties, schema
                    self.sync_source_database(source, db, source_connection=source_connection, recursive=False, rebuild=rebuild)

                for db in merges:
                    #  sync to update description, properties, schema
                    self.sync_source_database(source, db, source_connection=source_connection, recursive=False, rebuild=rebuild)

    def sync_source_database(self, source, database, source_connection=None, recursive=False, rebuild=False):
        """
        Synchronize a specific database with the registry.

        Updates database metadata, adds/removes/merges collections,
        and optionally recurses into collection syncing.

        Parameters:
            source (str): Source name or identifier.
            database (str): Database name.
            source_connection (object, optional): Pre-existing connection to the source. Defaults to None.
            recursive (bool, optional): If True, recursively sync collections. Defaults to False.
            rebuild (bool, optional): If True, rebuild the registry index after syncing. Defaults to False.

        Returns:
            None
        """
        if source_connection is None:
            source_connection = self.connect_source(source)

        if source_connection:
            # fetch database metadata
            metadata = source_connection.fetch_database_metadata(database)

            # update source database properties
            properties = {}
            properties['metadata'] = metadata
            description = ""
            if 'description' in metadata:
                description = metadata['description']

            current_description = self.get_source_database_description(source, database)

            if description.strip() and metadata:
                if not current_description or current_description.strip() == "":
                    self.update_source_database(source, database, description=description, properties=properties, rebuild=rebuild)

                else:
                    self.update_source_database(source, database, description=current_description, properties=properties, rebuild=rebuild)

            # fetch collections
            fetched_collections = source_connection.fetch_database_collections(database)
            fetched_collections_set = set(fetched_collections)

            # get existing collections
            registry_collections = self.get_source_database_collections(source, database)
            registry_collections_set = set(json_utils.json_query(registry_collections, '$[*].name', single=False))
            adds = set()
            removes = set()
            merges = set()

            ## compute add / remove / merge
            for collection in fetched_collections_set:
                if collection in registry_collections_set:
                    merges.add(collection)
                else:
                    adds.add(collection)
            for collection in registry_collections_set:
                if collection not in fetched_collections_set:
                    removes.add(collection)

            # update registry
            # add
            for collection in adds:
                self.register_source_database_collection(source, database, collection, description="", properties={}, rebuild=rebuild)

            # remove
            for collection in removes:
                self.deregister_source_database_collection(source, database, collection)

            ## recurse
            if recursive:
                for collection in fetched_collections_set:
                    self.sync_source_database_collection(source, database, collection, source_connection=source_connection, recursive=recursive, rebuild=rebuild)

            else:
                for collection in adds:
                    # sync to update description, properties, schema
                    self.sync_source_database_collection(source, database, collection, source_connection=source_connection, recursive=False, rebuild=rebuild)

                for collection in merges:
                    # sync to update description, properties, schema
                    self.sync_source_database_collection(source, database, collection, source_connection=source_connection, recursive=False, rebuild=rebuild)

    def sync_source_database_collection(self, source, database, collection, source_connection=None, recursive=False, rebuild=False):
        """
        Synchronize a specific collection within a database.

        Updates collection metadata, entities, relations, and their attributes.
        Adds new items, removes missing ones, and merges existing items.
        Sets the final schema after all updates.

        Parameters:
            source (str): Source name or identifier.
            database (str): Database name.
            collection (str): Collection name.
            source_connection (object, optional): Pre-existing connection to the source. Defaults to None.
            recursive (bool, optional): Currently not used; included for API consistency. Defaults to False.
            rebuild (bool, optional): If True, rebuild the registry index after syncing. Defaults to False.

        Returns:
            None
        """
        if source_connection is None:
            source_connection = self.connect_source(source)

        if source_connection:
            # fetch collection metadata
            metadata = source_connection.fetch_database_collection_metadata(database, collection)

            # update source database collection properties
            properties = {}
            properties['metadata'] = metadata
            description = ""
            if 'description' in metadata:
                description = metadata['description']

            current_description = self.get_source_database_collection_description(source, database, collection)

            if description.strip() and metadata:
                if not current_description or current_description.strip() == "":
                    self.update_source_database_collection(source, database, collection, description=description, properties=properties, rebuild=rebuild)
                else:
                    self.update_source_database_collection(source, database, collection, description=current_description, properties=properties, rebuild=rebuild)

            entities = source_connection.fetch_database_collection_entities(database, collection)
            relations = source_connection.fetch_database_collection_relations(database, collection)

            fetched_entities_set = set(entities.keys())
            fetched_relations_set = set(relations.keys())

            ## entities
            registry_entities = self.get_source_database_collection_entities(source, database, collection)
            registry_entities_set = set(json_utils.json_query(registry_entities, '$[*].name', single=False))

            adds = set()
            removes = set()
            merges = set()

            ## compute add / remove / merge
            for entity in fetched_entities_set:
                if entity in registry_entities_set:
                    merges.add(entity)
                else:
                    adds.add(entity)
            for entity in registry_entities_set:
                if entity not in fetched_entities_set:
                    removes.add(entity)

            # update registry
            # add
            for entity in adds:
                self.register_source_database_collection_entity(source, database, collection, entity, description="", properties={}, rebuild=rebuild)

            # remove
            for entity in removes:
                self.deregister_source_database_collection_entity(source, database, collection, entity)

            # update
            for entity in merges:
                self.update_source_database_collection_entity(source, database, collection, entity, description="", properties={}, rebuild=rebuild)

            # ---------------- entity attributes ---------------- #
            for entity in fetched_entities_set:
                entity_obj = entities[entity]
                entity_properties = entity_obj.get("properties", {})

                fetched_attrs = entity_obj.get("contents", {}).get("attributes", {})
                registry_attrs = self.get_source_database_collection_entity_attributes(source, database, collection, entity) or {}

                registry_attrs_set = set(json_utils.json_query(registry_attrs, '$[*].name', single=False))
                fetched_attrs_set = set(fetched_attrs.keys())

                attr_adds = fetched_attrs_set - registry_attrs_set
                attr_removes = registry_attrs_set - fetched_attrs_set
                attr_merges = fetched_attrs_set & registry_attrs_set

                for attr in attr_adds:
                    self.register_source_database_collection_entity_attribute(source, database, collection, entity, attr, description="", properties=fetched_attrs[attr], rebuild=rebuild)
                for attr in attr_removes:
                    self.deregister_source_database_collection_entity_attribute(source, database, collection, entity, attr)
                for attr in attr_merges:
                    self.update_source_database_collection_entity_attribute(source, database, collection, entity, attr, description="", properties=fetched_attrs[attr], rebuild=rebuild)

            ## relations
            # get existing schema entities
            registry_relations = self.get_source_database_collection_relations(source, database, collection)
            registry_relations_set = set(json_utils.json_query(registry_relations, '$[*].name', single=False))

            adds = set()
            removes = set()
            merges = set()

            ## compute add / remove / merge
            for relation in fetched_relations_set:
                if relation in registry_relations_set:
                    merges.add(relation)
                else:
                    adds.add(relation)
            for relation in registry_relations_set:
                if relation not in fetched_relations_set:
                    removes.add(relation)

            # update registry
            # add
            for relation in adds:
                self.register_source_database_collection_relation(source, database, collection, relation, description="", properties=relations[relation], rebuild=rebuild)

            # remove
            for relation in removes:
                self.deregister_source_database_collection_relation(source, database, collection, relation)

            # update
            for relation in merges:
                self.update_source_database_collection_relation(source, database, collection, relation, description="", properties=relations[relation], rebuild=rebuild)

            # ---------------- relation attributes ---------------- #
            for relation in fetched_relations_set:
                relation_obj = relations[relation]
                relation_properties = relation_obj.get("properties", {})

                fetched_attrs = relation_obj.get("contents", {}).get("attributes", {})
                registry_attrs = self.get_source_database_collection_relation_attributes(source, database, collection, relation) or {}

                registry_attrs_set = set(json_utils.json_query(registry_attrs, '$[*].name', single=False))
                fetched_attrs_set = set(fetched_attrs.keys())

                attr_adds = fetched_attrs_set - registry_attrs_set
                attr_removes = registry_attrs_set - fetched_attrs_set
                attr_merges = fetched_attrs_set & registry_attrs_set

                for attr in attr_adds:
                    self.register_source_database_collection_relation_attribute(source, database, collection, relation, attr, description="", properties=fetched_attrs[attr], rebuild=rebuild)
                for attr in attr_removes:
                    self.deregister_source_database_collection_relation_attribute(source, database, collection, relation, attr)
                for attr in attr_merges:
                    self.update_source_database_collection_relation_attribute(source, database, collection, relation, attr, description="", properties=fetched_attrs[attr], rebuild=rebuild)

            ## set schema after all entities and relations are processed
            try:
                schema = self.get_data_source_schema(source, database, collection, format="json")
                if schema and schema != "{}":
                    self.set_source_database_collection_property(source, database, collection, "schema", schema, rebuild=True)
            except Exception as e:
                self.logger.warning(f"Failed to set collection schema for {collection}: {e}")

    ###############
    ##  data sources search
    def get_data_source_schema(self, source, database, collection, format="dict"):
        """Return the schema by combining entities and relations, default in dict format"""
        schema = {}
        entities = self.get_source_database_collection_entities(source, database, collection)
        relations = self.get_source_database_collection_relations(source, database, collection)
        schema['entities'] = entities
        schema['relations'] = relations
        if format == "dict":
            return schema
        elif format == "json":
            return json.dumps(schema, indent=2)
        elif format == "yaml":
            return yaml.dump(schema)

        # build DataSchema class and return string representation
        schema = DataSchema()
        schema.entities = entities
        schema.relations = relations
        # note: please update the schema representation in DataSchema class if the default __str__ doesn't satisfy your needs
        return str(schema)

    ###### registry functions
    def _build_index_schema(self):
        """
        Build the schema for the search index, including text fields and vector fields.

        Returns:
        list: List of index field definitions (TextField, VectorField).
        """
        schema = list(super()._build_index_schema())
        schema.extend(
            [
                TextField("values"),
                TextField("schema"),
                VectorField(
                    "schema_vector",
                    "FLAT",
                    {
                        "TYPE": "FLOAT32",
                        "DIM": self.vector_dimensions,
                        "DISTANCE_METRIC": "COSINE",
                    },
                ),
            ]
        )
        return schema

    def _set_index_record(self, record, recursive=False, pipe=None):
        """
        Add or update a record in the search index, optionally recursively for nested contents.

        Parameters:
            record (dict): Record containing 'name', 'type', 'scope', 'description', and optionally 'contents' and 'properties'.
            recursive (bool, optional): If True, recursively index nested records. Defaults to False.
            pipe (Redis pipeline, optional): Redis pipeline to batch commands. If None, a new pipeline is created.
        """
        if self.embeddings_model is None:
            self._init_search_index()

        if 'name' not in record:
            return

        name = record['name']
        type = record['type']
        scope = record['scope']
        description = record['description']

        schema = None
        # In current implementation, schema is only available for collection type
        if type == 'collection' and 'properties' in record:
            schema = record['properties'].get('schema', None)

        if type == "attribute":
            props = record.get("properties", {})
            info = props.get("info", {})
            values = info.get("values", [])
            if isinstance(values, list) and values:
                self._create_index_doc(name, type, scope, description, schema=schema, values=values, pipe=pipe)
            else:
                self._create_index_doc(name, type, scope, description, schema=schema, pipe=pipe)
        else:
            self._create_index_doc(name, type, scope, description, schema=schema, pipe=pipe)

        if recursive:
            contents = record['contents']
            for type_key in contents:
                contents_by_type = contents[type_key]
                for record_key in contents_by_type:
                    r = contents_by_type[record_key]
                    self._set_index_record(r, recursive=recursive, pipe=pipe)

    def _create_index_doc(self, name, type, scope, description, schema=None, values=None, pipe=None):
        """
        Create a single index document in the search index.

        Parameters:
            name (str): Name of the entity/attribute/collection/relation.
            type (str): Type of record (e.g., "collection", "attribute").
            scope (str): Scope of the record (e.g., full path or database/collection).
            description (str): Description text for the record.
            schema (str, optional): Schema string representation for collections. Defaults to None.
            values (list, optional): List of attribute values to include in the embedding. Defaults to None.
            pipe (Redis pipeline, optional): Redis pipeline to batch commands. If None, a new pipeline is created.
        """
        if self.embeddings_model is None:
            self._init_search_index()

        # the 'vector' field is based on name + description
        text = name
        if description:
            text += ' ' + description

        values_str = None

        if values:
            text += " " + " ".join(map(str, values))
            values_str = json.dumps(values, ensure_ascii=False)

        vector = self._compute_embedding_vector(text)

        doc = {'name': name, 'type': type, 'scope': scope, 'description': description, 'vector': vector}

        if values_str:
            doc["values"] = values_str

        # extra schema and schema_vector fields
        if schema is not None:
            if not isinstance(schema, str):
                schema = str(schema)
            schema_vector = self._compute_embedding_vector(schema)
            doc['schema'] = schema
            doc['schema_vector'] = schema_vector

        doc_key = self._Registry__doc_key(name, type, scope)

        if pipe:
            pipe.hset(doc_key, mapping=doc)
        else:
            pipe = self.connection.pipeline()
            pipe.hset(doc_key, mapping=doc)
            res = pipe.execute()

    def _delete_index_doc(self, name, type, scope, pipe=None):
        """
        Delete a document from the search index.

        Parameters:
            name (str): Name of the entity/attribute/collection/relation.
            type (str): Type of record.
            scope (str): Scope of the record.
            pipe (Redis pipeline, optional): Redis pipeline to batch commands. If None, a new pipeline is created.
        """
        if self.embeddings_model is None:
            self._init_search_index()

        doc_key = self._Registry__doc_key(name, type, scope)

        # Define fields to delete
        base_fields = ["name", "type", "scope", "description", "values", "vector"]

        # In current implementation, schema is only available for collection type
        if type == 'collection':
            base_fields.extend(["schema", "schema_vector"])

        if pipe:
            if base_fields:
                pipe.hdel(doc_key, *base_fields)
        else:
            pipe = self.connection.pipeline()
            if base_fields:
                pipe.hdel(doc_key, *base_fields)
            res = pipe.execute()

    def _prepare_search_parameters(
        self,
        input_query,
        type=None,
        scope=None,
        bm25_weight=None,
        vector_weight=None,
        bm25_normalization=None,
        bm25_threshold=None,
        vector_threshold=None,
        combined_threshold=None,
        enable_schema=None,
        hierarchical_enabled=None,
        hierarchical_database_types=None,
        hierarchical_collection_types=None,
        redis_search_limit=None,
    ):
        """Prepare and validate search parameters"""
        if input_query:
            input_query = input_query.strip()

        # Use properties if not provided
        bm25_weight = bm25_weight if bm25_weight is not None else self.properties.get('search_bm25_weight', 0.3)
        vector_weight = vector_weight if vector_weight is not None else self.properties.get('search_vector_weight', 0.7)
        bm25_normalization = bm25_normalization if bm25_normalization is not None else self.properties.get('search_bm25_normalization', 'minmax')
        enable_schema = enable_schema if enable_schema is not None else self.properties.get('search_enable_schema', True)

        # thresholds
        bm25_threshold = bm25_threshold if bm25_threshold is not None else self.properties.get('search_bm25_threshold', 0.0)
        vector_threshold = vector_threshold if vector_threshold is not None else self.properties.get('search_vector_threshold', 0.5)
        combined_threshold = combined_threshold if combined_threshold is not None else self.properties.get('search_combined_threshold', 0.36)

        # hierarchical search
        hierarchical_enabled = hierarchical_enabled if hierarchical_enabled is not None else self.properties.get('search_hierarchical_enabled', True)
        hierarchical_database_types = (
            hierarchical_database_types if hierarchical_database_types is not None else self.properties.get('search_hierarchical_database_types', ['database', 'collection', 'entity'])
        )
        hierarchical_collection_types = (
            hierarchical_collection_types if hierarchical_collection_types is not None else self.properties.get('search_hierarchical_collection_types', ['collection', 'entity'])
        )

        # Redis search limit
        redis_search_limit = redis_search_limit if redis_search_limit is not None else self.properties.get('search_redis_limit', 1000)

        # Validate weights
        if bm25_weight < 0 or vector_weight < 0:
            raise ValueError("Weights must be non-negative")
        total_weight = bm25_weight + vector_weight
        if total_weight != 0:
            # Normalize weights to sum to 1.0
            bm25_weight /= total_weight
            vector_weight /= total_weight

        # validate thresholds
        if bm25_threshold < 0 or bm25_threshold > 1:
            raise ValueError("BM25 threshold must be between 0 and 1 (normalized)")
        if vector_threshold < 0 or vector_threshold > 1:
            raise ValueError("Vector threshold must be between 0 and 1 (normalized)")
        if combined_threshold < 0 or combined_threshold > 1:
            raise ValueError("Combined threshold must be between 0 and 1")

        # validate Redis search limit
        if redis_search_limit < 1:
            raise ValueError("Redis search limit must be at least 1")

        if self.embeddings_model is None:
            self._init_search_index()

        return {
            'input_query': input_query,
            'type': type,
            'scope': scope,
            'bm25_weight': bm25_weight,
            'vector_weight': vector_weight,
            'bm25_threshold': bm25_threshold,
            'vector_threshold': vector_threshold,
            'combined_threshold': combined_threshold,
            'bm25_normalization': bm25_normalization,
            'enable_schema': enable_schema,
            'redis_search_limit': redis_search_limit,
            'index_name': self._get_index_name(),
        }

    def _build_search_query(self, params, search_types=None):
        """Build Redis search query"""
        search_type = params['type']
        scope = params['scope']

        # Build type and scope constraints
        qs = ""

        # Handle scope (wildcard vs exact match)
        if scope:
            if scope == "/":
                qs = qs
            elif "*" in scope:
                # Wildcard / prefix search -> no quotes
                qs = f"(@scope:{scope}) " + qs
            else:
                # Exact match -> keep quotes
                qs = f'(@scope:"{scope}") ' + qs

        if search_types:
            # For hierarchical search with multiple types
            # Use Redis Search OR syntax without extra parentheses
            type_constraint = " | ".join([f'@type:{t}' for t in search_types])
            qs = f"({type_constraint}) " + qs
        elif search_type:
            # For regular search with single type
            qs = "(@type: \"" + search_type + "\")" + qs

        # Set final query
        if qs:
            q = qs
        else:
            q = "*"

        query_params = {}
        return q, query_params

    def _compute_vector_score(self, result, query_vector, doc_vector, schema_vector, params):
        """Compute vector similarity for a result using precomputed vectors."""
        if query_vector is None:
            return 0.0

        if doc_vector is None:
            return 0.0  # fallback: no vector stored

        vector_score = compute_vector_score(query_vector, doc_vector, normalize_score=True)

        # For collections, also check schema vector similarity if enabled
        if params['enable_schema'] and result.type == 'collection' and getattr(result, 'schema', None):
            if schema_vector is not None:
                schema_vector_score = compute_vector_score(query_vector, schema_vector, normalize_score=True)
                vector_score = max(vector_score, schema_vector_score)

        return vector_score

    def search_records(
        self,
        input_query,
        type=None,
        scope=None,
        approximate=False,
        hybrid=False,
        page=0,
        page_size=5,
        page_limit=10,
        bm25_weight=None,
        vector_weight=None,
        bm25_threshold=None,
        vector_threshold=None,
        combined_threshold=None,
        bm25_normalization=None,
        enable_schema=None,
        redis_search_limit=None,
    ):
        """
        Search records using BM25 relevance, vector similarity, and optional schema-based scoring.

        This method retrieves records from the search index and ranks them using a combination of BM25
        and vector similarity scores. It supports schema inclusion, score normalization, thresholds,
        and pagination.

        Parameters
        ----------
        input_query : str
            The search query text to match against records.
        type : str, optional
            The type of record to search (e.g., 'database', 'collection'). Defaults to None (all types).
        scope : str, optional
            The scope of the search. Special handling for "/" to restrict results to top-level records. Defaults to None.
        approximate : bool, optional
            Flag indicating whether to perform approximate search (not currently used). Defaults to False.
        hybrid : bool, optional
            Flag indicating whether to use hybrid BM25 + vector search (not currently used). Defaults to False.
        page : int, optional
            Zero-based page number for paginated results. Defaults to 0.
        page_size : int, optional
            Number of results per page. Defaults to 5.
        page_limit : int, optional
            Maximum number of pages to retrieve. Defaults to 10.
        bm25_weight : float, optional
            Weight factor for BM25 score when combining with vector score. Defaults to None.
        vector_weight : float, optional
            Weight factor for vector similarity score when combining with BM25. Defaults to None.
        bm25_threshold : float, optional
            Minimum normalized BM25 score to include a result. Defaults to None.
        vector_threshold : float, optional
            Minimum vector similarity score to include a result. Defaults to None.
        combined_threshold : float, optional
            Minimum combined score (BM25 + vector) to include a result. Defaults to None.
        bm25_normalization : str or float, optional
            Method or factor to normalize BM25 scores to [0, 1]. Defaults to None.
        enable_schema : bool, optional
            Whether to include schema text in BM25 scoring for collection records. Defaults to None.
        redis_search_limit : int, optional
            Maximum number of records to retrieve from Redis search before filtering/pagination. Defaults to None.

        Returns
        -------
        List[dict]
            A paginated list of search results, each represented as a dictionary containing:
            - `id`, `name`, `type`, `scope`, `description`, `schema` (if present)
            - `bm25_score` (raw BM25 score)
            - `vector_score` (raw vector similarity score)
            - `normalized_bm25_score` (BM25 normalized to [0, 1])
            - `combined_score` (weighted combination of BM25 and vector scores)
            - `score` (inverted score for ranking: lower is better)

        Notes
        -----
        - Computes BM25 score using document text and optionally schema text.
        - Computes vector similarity between the query embedding and document embeddings.
        - Applies thresholds to BM25, vector, and combined scores to filter results.
        - Inverts the combined score so that lower scores are better for consumer applications.
        - Supports pagination via `page` and `page_size` parameters.
        - Special handling for `scope='/'` restricts results to top-level records only.
        """
        params = self._prepare_search_parameters(
            input_query, type, scope, bm25_weight, vector_weight, bm25_threshold, vector_threshold, combined_threshold, bm25_normalization, enable_schema, redis_search_limit=redis_search_limit
        )

        q, query_params = self._build_search_query(params)
        query = Query(q).return_fields("id", "name", "type", "scope", "description", "schema").paging(0, params['redis_search_limit'])

        results = self.connection.ft(params['index_name']).search(query, query_params).docs
        print(f"  Found {len(results)} entities in index")

        # Special handling for scope = '/'
        if scope == "/":
            filtered_results = []
            for result in results:
                if result.scope == "/":
                    filtered_results.append(result)
            results = filtered_results

        query_vector = None
        if input_query:
            query_vector = self._compute_embedding_vector(input_query)

        # Compute and attach all scores directly to result objects
        for i, result in enumerate(results):
            # Compute BM25 score [0, inf] range, higher is better
            doc_text = f"{result.name} {getattr(result, 'description', '')}".rstrip()
            # Get schema text if available and schema scoring is enabled
            schema_text = None
            if params['enable_schema'] and result.type == 'collection' and getattr(result, 'schema', None):
                schema_text = getattr(result, 'schema', '')

            bm25_score = compute_bm25_score(input_query, doc_text, schema_text) if input_query else 0.0

            doc_key = self._Registry__doc_key(result.name, result.type, result.scope)

            vector_bytes = self.connection_no_decode.execute_command("HGET", doc_key, "vector")
            schema_vector_bytes = self.connection_no_decode.execute_command("HGET", doc_key, "schema_vector")

            # Compute vector score
            vector_score = self._compute_vector_score(result, query_vector, vector_bytes, schema_vector_bytes, params)

            result.bm25_score = bm25_score
            result.vector_score = vector_score

        # Normalize BM25 scores to [0, 1] range, higher is better
        all_bm25_scores = [result.bm25_score for result in results]
        normalized_bm25_scores = normalize_bm25_scores(all_bm25_scores, params['bm25_normalization'])
        for i, result in enumerate(results):
            result.normalized_bm25_score = normalized_bm25_scores[i]

        # Apply thresholds and compute final scores
        final_results = []

        for result in results:
            normalized_bm25 = result.normalized_bm25_score
            combined_score = params['bm25_weight'] * normalized_bm25 + params['vector_weight'] * result.vector_score

            # Invert combined score so lower = better
            inverted_score = 1.0 - combined_score

            # Apply thresholds on inverted score for consumer consistency
            if normalized_bm25 < params['bm25_threshold'] or result.vector_score < params['vector_threshold'] or inverted_score > (1.0 - params['combined_threshold']):
                continue

            # Attach final scores to result object
            result.normalized_bm25 = normalized_bm25
            result.combined_score = combined_score

            # Convert to dictionary format
            output_dict = {
                "name": result.name,
                "description": getattr(result, 'description', ''),
                "type": result.type,
                "scope": result.scope,
                "id": result.id,
                "score": inverted_score,  ## this is for consumers,
                "bm25_score": result.bm25_score,
                "vector_score": result.vector_score,
                "normalized_bm25_score": normalized_bm25,
            }
            if hasattr(result, 'schema') and result.schema:
                output_dict['schema'] = result.schema
            final_results.append(output_dict)

        # Sort by inverted score, lower is better
        final_results.sort(key=lambda x: x['score'])

        # Pagination
        page_results = final_results[page * page_size : (page + 1) * page_size]
        return page_results

    def search_records_hierarchical(
        self,
        input_query,
        type=None,
        scope=None,
        page=0,
        page_size=5,
        page_limit=10,
        bm25_weight=None,
        vector_weight=None,
        bm25_threshold=None,
        vector_threshold=None,
        combined_threshold=None,
        enable_schema=None,
        bm25_normalization=None,
        redis_search_limit=None,
    ):
        """
        Perform a hierarchical search over records, considering parent-child relationships for databases and collections.

        This method supports both standard and hierarchical searches. For `type` values other than
        'database' or 'collection', it delegates to `search_records`. For hierarchical searches, it computes
        BM25 and vector similarity scores, optionally including schema information, and aggregates results
        across parent-child hierarchies.

        Parameters
        ----------
        input_query : str
            The search query text to match against records.
        type : str, optional
            The type of record to search ('database', 'collection', etc.). Defaults to None.
        scope : str, optional
            The scope of the search. Special handling for "/" to filter top-level records. Defaults to None.
        page : int, optional
            The zero-based page number to return. Defaults to 0.
        page_size : int, optional
            Number of results per page. Defaults to 5.
        page_limit : int, optional
            Maximum number of pages to retrieve. Defaults to 10.
        bm25_weight : float, optional
            Weighting factor for BM25 score when combining with vector score. Defaults to None.
        vector_weight : float, optional
            Weighting factor for vector similarity score when combining with BM25. Defaults to None.
        bm25_threshold : float, optional
            Minimum BM25 score threshold for including results. Defaults to None.
        vector_threshold : float, optional
            Minimum vector similarity score threshold for including results. Defaults to None.
        combined_threshold : float, optional
            Minimum combined score threshold for including results. Defaults to None.
        enable_schema : bool, optional
            Whether to include schema text in scoring for collection records. Defaults to None.
        bm25_normalization : str or float, optional
            Method or factor to normalize BM25 scores to [0, 1]. Defaults to None.
        redis_search_limit : int, optional
            Maximum number of records to retrieve from Redis search before filtering/pagination. Defaults to None.

        Returns
        -------
        List[dict]
            A paginated list of search results grouped hierarchically by parent-child relationships.
            Each result dictionary contains:
            - `id`, `name`, `type`, `scope`, `description`, `schema`
            - `bm25_score` (raw BM25 score)
            - `vector_score` (raw vector similarity score)
            - `normalized_bm25_score` (BM25 score normalized to [0, 1])
            - `score` (combined hierarchical score used for sorting)

        Notes
        -----
        - If `type` is not 'database' or 'collection', a standard non-hierarchical search is performed.
        - Vector embeddings are computed for the query and stored document vectors for similarity scoring.
        - Hierarchical aggregation merges scores for parent and child records before sorting and pagination.
        - Special handling exists for `scope='/'` to restrict results to top-level records only.
        """

        # Check if this should be a regular search instead of hierarchical
        if type not in ['database', 'collection']:
            return self.search_records(
                input_query=input_query,
                type=type,
                scope=scope,
                page=page,
                page_size=page_size,
                page_limit=page_limit,
                bm25_weight=bm25_weight,
                vector_weight=vector_weight,
                bm25_threshold=bm25_threshold,
                vector_threshold=vector_threshold,
                combined_threshold=combined_threshold,
                bm25_normalization=bm25_normalization,
                enable_schema=enable_schema,
                redis_search_limit=redis_search_limit,
            )

        params = self._prepare_search_parameters(
            input_query, type, scope, bm25_weight, vector_weight, bm25_threshold, vector_threshold, combined_threshold, bm25_normalization, enable_schema, redis_search_limit=redis_search_limit
        )

        # Determine search types for hierarchical search
        if type == 'database':
            search_types = self.properties.get('search_hierarchical_database_types', ['database', 'collection', 'entity'])
        elif type == 'collection':
            search_types = self.properties.get('search_hierarchical_collection_types', ['collection', 'entity'])
        else:
            search_types = [type]

        q, query_params = self._build_search_query(params, search_types)
        query = Query(q).return_fields("id", "name", "type", "scope", "description", "schema").paging(0, params['redis_search_limit'])
        results = self.connection.ft(params['index_name']).search(query, query_params).docs

        if not results:
            return []

        # Special handling for scope = '/'
        if scope == "/":
            filtered_results = []
            for result in results:
                if result.scope == "/":
                    filtered_results.append(result)
            results = filtered_results

        query_vector = None
        if input_query:
            query_vector = self._compute_embedding_vector(input_query)

        # Compute and attach all scores directly to result objects
        for i, result in enumerate(results):
            # Compute BM25 score
            doc_text = f"{result.name} {getattr(result, 'description', '')}".rstrip()
            # Get schema text if available and schema scoring is enabled
            schema_text = None
            if params['enable_schema'] and result.type == 'collection' and getattr(result, 'schema', None):
                schema_text = getattr(result, 'schema', '')

            bm25_score = compute_bm25_score(input_query, doc_text, schema_text) if input_query else 0.0

            doc_key = self._Registry__doc_key(result.name, result.type, result.scope)

            vector_bytes = self.connection_no_decode.execute_command("HGET", doc_key, "vector")
            schema_vector_bytes = self.connection_no_decode.execute_command("HGET", doc_key, "schema_vector")

            # Compute vector score
            vector_score = self._compute_vector_score(result, query_vector, vector_bytes, schema_vector_bytes, params)

            # Attach scores directly to result object
            result.bm25_score = bm25_score
            result.vector_score = vector_score

        # Normalize BM25 scores to [0, 1] range, higher is better
        all_bm25_scores = [result.bm25_score for result in results]
        normalized_bm25_scores = normalize_bm25_scores(all_bm25_scores, params['bm25_normalization'])
        for i, result in enumerate(results):
            result.normalized_bm25_score = normalized_bm25_scores[i]

        # Group results by parent and collect scores
        hierarchical_results = self._build_hierarchical_results(results, type, params)

        # Sort by score, lower is better
        hierarchical_results.sort(key=lambda x: x['score'])

        # Pagination
        page_results = hierarchical_results[page * page_size : (page + 1) * page_size]
        return page_results

    def _build_hierarchical_results(self, results, target_type, params):
        """Build hierarchical results"""
        if not results:
            return []

        # Build hierarchy graph with node IDs
        hierarchy = self._build_hierarchy_by_node_id(results)

        # Get target candidate nodes that match type
        target_nodes = self._get_target_candidate_nodes(hierarchy, target_type)

        # For each target candidate node, update score by itself and all children
        hierarchical_results = []

        for node_id in target_nodes:
            best_score, best_record = self._update_node_score_with_children(node_id, hierarchy, params)
            if best_record is not None:

                hierarchical_results.append(
                    {
                        "name": hierarchy[node_id]['record'].name,
                        "type": hierarchy[node_id]['record'].type,
                        "scope": hierarchy[node_id]['record'].scope,
                        "id": hierarchy[node_id]['record'].id,
                        "description": hierarchy[node_id]['record'].description,
                        "score": best_score,
                        "bm25_score": best_record.bm25_score,
                        "vector_score": best_record.vector_score,
                        "normalized_bm25_score": best_record.normalized_bm25_score,
                        "best_record_id": best_record.id,
                        "best_record_name": best_record.name,
                        "best_record_type": best_record.type,
                        "best_record_scope": best_record.scope,
                    }
                )
        return hierarchical_results

    def _build_hierarchy_by_node_id(self, results):
        """Build hierarchy graph from results using node IDs"""
        if not results:
            return {}

        hierarchy = {}
        edges = []

        # Create nodes for all results
        for result in results:
            if not hasattr(result, 'id') or not hasattr(result, 'scope') or not hasattr(result, 'type') or not hasattr(result, 'name'):
                continue  # Skip invalid results

            node_id = result.id
            hierarchy[node_id] = {'record': result, 'children': [], 'parent': None}

        # Build scope to ID mapping
        scope2id = {}
        for result in results:
            if not hasattr(result, 'id') or not hasattr(result, 'scope') or not hasattr(result, 'type') or not hasattr(result, 'name'):
                continue

            scope = result.scope
            child_scope = f"{scope}/{result.type}/{result.name}"
            scope2id[child_scope] = result.id

        # Build edges
        for result in results:
            if not hasattr(result, 'id') or not hasattr(result, 'scope') or not hasattr(result, 'type') or not hasattr(result, 'name'):
                continue
            if result.scope in scope2id:
                parent_id = scope2id[result.scope]
                child_id = result.id
                # Only add edge if both parent and child exist in hierarchy
                if parent_id in hierarchy and child_id in hierarchy:
                    edges.append((parent_id, child_id))

        # Build hierarchy from edges
        for edge in edges:
            parent_id, child_id = edge
            if parent_id in hierarchy and child_id in hierarchy:
                hierarchy[parent_id]['children'].append(child_id)
                hierarchy[child_id]['parent'] = parent_id

        return hierarchy

    def _get_target_candidate_nodes(self, hierarchy, target_type):
        """Get target candidate nodes that match the specified type."""
        target_nodes = set()
        for node_id, node_data in hierarchy.items():
            if node_data['record'].type == target_type:
                target_nodes.add(node_id)
        return list(target_nodes)

    def _update_node_score_with_children(self, node_id, hierarchy, params):
        """Update node score by itself and all children (nested) scores"""
        if node_id not in hierarchy:
            return float('inf'), None  # invalid / worst score

        node_data = hierarchy[node_id]
        record = node_data['record']

        # Get all children (nested) including the node itself
        all_related_nodes = {node_id} | self._get_all_children_recursive(node_id, hierarchy)

        # Find the best score among all related nodes
        best_score, best_record = self._find_best_score_among_nodes(all_related_nodes, hierarchy, params)

        return best_score, best_record

    def _get_all_children_recursive(self, node_id, hierarchy, visited=None):
        """Get all children (nested) of a node recursively using set for efficiency"""
        if visited is None:
            visited = set()

        # Prevent infinite recursion in case of cycles
        if node_id in visited:
            return set()

        visited.add(node_id)
        children = set()

        if node_id not in hierarchy:
            return children

        node_data = hierarchy[node_id]

        for child_id in node_data['children']:
            children.add(child_id)
            # Recursively get all descendants
            descendants = self._get_all_children_recursive(child_id, hierarchy, visited)
            children.update(descendants)

        return children

    def _find_best_score_among_nodes(self, node_ids, hierarchy, params):
        """Find the best score among a set of nodes"""
        best_score = 1.0
        best_record = None

        for node_id in node_ids:
            if node_id not in hierarchy:
                continue

            record = hierarchy[node_id]['record']
            normalized_bm25 = record.normalized_bm25_score
            combined_score = params['bm25_weight'] * normalized_bm25 + params['vector_weight'] * record.vector_score

            # Invert combined score so lower = better
            inverted_score = 1.0 - combined_score

            # Apply thresholds same as search_records
            if normalized_bm25 < params['bm25_threshold'] or record.vector_score < params['vector_threshold'] or inverted_score > (1.0 - params['combined_threshold']):
                continue

            # Keep the best (lowest inverted_score) node
            if best_record is None or inverted_score < best_score:
                best_score = inverted_score
                best_record = record

        return best_score, best_record
