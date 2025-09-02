###### Parsers, Formats, Utils
import argparse
import logging
import json

import yaml

###### Blue
from blue.utils import json_utils
from blue.registry import Registry
from blue.metadata import MetaData 

from blue.data.schema import DataSchema

###### Supported Data Sources
from blue.data.sources.mongodb_source import MongoDBSource
from blue.data.sources.neo4j_source import NEO4JSource
from blue.data.sources.postgres_source import PostgresDBSource
from blue.data.sources.mysql_source import MySQLDBSource
from blue.data.sources.sqlite_source import SQLiteDBSource
from blue.data.sources.openai_source import OpenAISource


###############
### DataRegistry
#
class DataRegistry(Registry):
    def __init__(self, name="DATA_REGISTRY", id=None, platform_id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):
        self.platform_name = platform_id
        self.metadata = MetaData(platform_id=platform_id)
      
        super().__init__(name=name, id=id, sid=sid, cid=cid, prefix=prefix, suffix=suffix, properties=properties)

    ###### initialization
    def _initialize_properties(self):
        super()._initialize_properties()

        
    
    ######### source
    def register_source(self, source, created_by, description="", properties={}, rebuild=False):
        super().register_record(source, 'source', '/', created_by=created_by, description=description, properties=properties, rebuild=rebuild)

    def update_source(self, source, description=None, icon=None, properties=None, rebuild=False):
        super().update_record(source, 'source', '/', description=description, icon=icon, properties=properties, rebuild=rebuild)

    def deregister_source(self, source, rebuild=False):
        record = self.get_source(source)
        super().deregister(record, rebuild=rebuild)

    def get_sources(self):
        return super().list_records(type="source", scope="/")

    def get_source(self, source):
        return super().get_record(source, 'source', '/')

    # description
    def get_source_description(self, source):
        return super().get_record_description(source, 'source', '/')

    def set_source_description(self, source, description, rebuild=False):
        super().set_record_description(source, 'source', '/', description, rebuild=rebuild)

    # properties
    def get_source_properties(self, source):
        return super().get_record_properties(source, 'source', '/')

    def get_source_property(self, source, key):
        return super().get_record_property(source, 'source', '/', key)

    def set_source_property(self, source, key, value, rebuild=False):
        super().set_record_property(source, 'source', '/', key, value, rebuild=rebuild)

    def delete_source_property(self, source, key, rebuild=False):
        super().delete_record_property(source, 'source', '/', key, rebuild=rebuild)

    ######### source/database
    def register_source_database(self, source, database, description="", properties={}, rebuild=False):
        super().register_record(database, 'database', f'/source/{source}', description=description, properties=properties, rebuild=rebuild)

    def update_source_database(self, source, database, description=None, properties=None, rebuild=False):
        super().update_record(database, 'database', f'/source/{source}', description=description, properties=properties, rebuild=rebuild)

    def deregister_source_database(self, source, database, rebuild=False):
        record = self.get_source_database(source, database)
        super().deregister(record, rebuild=rebuild)

    def get_source_databases(self, source):
        return super().filter_record_contents(source, 'source', '/', filter_type='database')

    def get_source_database(self, source, database):
        return super().filter_record_contents(source, 'source', '/', filter_type='database', filter_name=database, single=True)

    # description
    def get_source_database_description(self, source, database):
        return super().get_record_description(database, 'database', f'/source/{source}')

    def set_source_database_description(self, source, database, description, rebuild=False):
        super().set_record_description(database, 'database', f'/source/{source}', description, rebuild=rebuild)

    # properties
    def get_source_database_properties(self, source, database):
        return super().get_record_properties(database, 'database', f'/source/{source}')

    def get_source_database_property(self, source, database, key):
        return super().get_record_property(database, 'database', f'/source/{source}', key)

    def set_source_database_property(self, source, database, key, value, rebuild=False):
        super().set_record_property(database, 'database', f'/source/{source}', key, value, rebuild=rebuild)

    ######### source/database/collection
    def register_source_database_collection(self, source, database, collection, description="", properties={}, rebuild=False):
        super().register_record(collection, 'collection', f'/source/{source}/database/{database}', description=description, properties=properties, rebuild=rebuild)

    def update_source_database_collection(self, source, database, collection, description=None, properties=None, rebuild=False):
        original_record, merged_record = super().update_record(
            collection, 'collection', f'/source/{source}/database/{database}', description=description, properties=properties, rebuild=rebuild
        )
        return original_record, merged_record

    def deregister_source_database_collection(self, source, database, collection, rebuild=False):
        record = self.get_source_database_collection(source, database, collection)
        super().deregister(record, rebuild=rebuild)

    def get_source_database_collections(self, source, database):
        return super().filter_record_contents(database, 'database', f'/source/{source}', filter_type='collection')

    def get_source_database_collection(self, source, database, collection):
        return super().filter_record_contents(database, 'database', f'/source/{source}', filter_type='collection', filter_name=collection, single=True)

    # description
    def get_source_database_collection_description(self, source, database, collection):
        return super().get_record_description(collection, 'collection', f'/source/{source}/database/{database}')

    def set_source_database_collection_description(self, source, database, collection, description, rebuild=False):
        super().set_record_description(collection, 'collection', f'/source/{source}/database/{database}', description, rebuild=rebuild)

    # properties
    def get_source_database_collection_properties(self, source, database, collection):
        return super().get_record_properties(collection, 'collection', f'/source/{source}/database/{database}')

    def get_source_database_collection_property(self, source, database, collection, key):
        return super().get_record_property(collection, 'collection', f'/source/{source}/database/{database}', key)

    def set_source_database_collection_property(self, source, database, collection, key, value, rebuild=False):
        super().set_record_property(collection, 'collection', f'/source/{source}/database/{database}', key, value, rebuild=rebuild)

    ######### source/database/collection/entity
    def register_source_database_collection_entity(self, source, database, collection, entity, description="", properties={}, rebuild=False):
        super().register_record(entity, 'entity', f'/source/{source}/database/{database}/collection/{collection}', description=description, properties=properties, rebuild=rebuild)

    def update_source_database_collection_entity(self, source, database, collection, entity, description=None, properties=None, rebuild=False):
        original_record, merged_record = super().update_record(
            entity, 'entity', f'/source/{source}/database/{database}/collection/{collection}', description=description, properties=properties, rebuild=rebuild
        )
        return original_record, merged_record

    def deregister_source_database_collection_entity(self, source, database, collection, entity, rebuild=False):
        record = self.get_source_database_collection_entity(source, database, collection, entity)
        super().deregister(record, rebuild=rebuild)

    def get_source_database_collection_entities(self, source, database, collection):
        return super().filter_record_contents(collection, 'collection', f'/source/{source}/database/{database}', filter_type='entity')

    def get_source_database_collection_entity(self, source, database, collection, entity):
        return super().filter_record_contents(collection, 'collection', f'/source/{source}/database/{database}', filter_type='entity', filter_name=entity, single=True)

    # description
    def get_source_database_collection_entity_description(self, source, database, collection, entity):
        return super().get_record_description(entity, 'entity', f'/source/{source}/database/{database}/collection/{collection}')

    def set_source_database_collection_entity_description(self, source, database, collection, entity, description, rebuild=False):
        super().set_record_description(entity, 'entity', f'/source/{source}/database/{database}/collection/{collection}', description, rebuild=rebuild)

    # properties
    def get_source_database_collection_entity_properties(self, source, database, collection, entity):
        return super().get_record_properties(entity, 'entity', f'/source/{source}/database/{database}/collection/{collection}')

    def get_source_database_collection_entity_property(self, source, database, collection, entity, key):
        return super().get_record_property(entity, 'entity', f'/source/{source}/database/{database}/collection/{collection}', key)

    def set_source_database_collection_entity_property(self, source, database, collection, entity, key, value, rebuild=False):
        super().set_record_property(entity, 'entity', f'/source/{source}/database/{database}/collection/{collection}', key, value, rebuild=rebuild)

    
    ######### source/database/collection/entity/attribute 
    def register_source_database_collection_entity_attribute(
        self, source, database, collection, entity, attribute,
        description="", properties=None, rebuild=False):
        if properties is None:
            properties = {}
        scope = f'/source/{source}/database/{database}/collection/{collection}/entity/{entity}'
        
        super().register_record(
            attribute, 'attribute', scope,
            description=description, properties=properties, rebuild=rebuild
        )

    def update_source_database_collection_entity_attribute(
        self, source, database, collection, entity, attribute,
        description=None, properties=None, rebuild=False):
        scope = f'/source/{source}/database/{database}/collection/{collection}/entity/{entity}'
        return super().update_record(
            attribute, 'attribute', scope,
            description=description, properties=properties, rebuild=rebuild
        )

    def deregister_source_database_collection_entity_attribute(
        self, source, database, collection, entity, attribute, rebuild=False):
        record = self.get_source_database_collection_entity_attribute(
            source, database, collection, entity, attribute
        )
        super().deregister(record, rebuild=rebuild)

    def get_source_database_collection_entity_attributes(
        self, source, database, collection, entity):
        scope = f'/source/{source}/database/{database}/collection/{collection}'
        return super().filter_record_contents(
            entity, 'entity', scope, filter_type='attribute'
        )

    def get_source_database_collection_entity_attribute(
        self, source, database, collection, entity, attribute):
        scope = f'/source/{source}/database/{database}/collection/{collection}'
        return super().filter_record_contents(
            entity, 'entity', scope,
            filter_type='attribute', filter_name=attribute, single=True
        )

    
    def set_source_database_collection_entity_attribute_property(self, source, database, collection, entity, attribute, key, value, rebuild=False):
        scope = f'/source/{source}/database/{database}/collection/{collection}/entity/{entity}'
        super().set_record_property(attribute, 'attribute', scope, key, value, rebuild=rebuild)


    def get_source_database_collection_entity_attribute_property(self, source, database, collection, entity, attribute, key):
        scope = f'/source/{source}/database/{database}/collection/{collection}/entity/{entity}'
        super().get_record_property(attribute, 'attribute', scope, key)

    
    # description
    def get_source_database_collection_entity_attribute_description(self, source, database, collection, entity, attribute):
        return super().get_record_description(attribute, 'attribute', f'/source/{source}/database/{database}/collection/{collection}/entity/{entity}')

    def set_source_database_collection_entity_attribute_description(self, source, database, collection, entity, attribute, description, rebuild=False):
        super().set_record_description(attribute, 'attribute', f'/source/{source}/database/{database}/collection/{collection}/entity/{entity}', description, rebuild=rebuild)

    
    ######### source/database/collection/relation
    def register_source_database_collection_relation(self, source, database, collection, relation, description="", properties={}, rebuild=False):
        super().register_record(relation, 'relation', f'/source/{source}/database/{database}/collection/{collection}', description=description, properties=properties, rebuild=rebuild)

    def update_source_database_collection_relation(self, source, database, collection, relation, description=None, properties=None, rebuild=False):
        original_record, merged_record = super().update_record(
            relation, 'relation', f'/source/{source}/database/{database}/collection/{collection}', description=description, properties=properties, rebuild=rebuild
        )
        return original_record, merged_record

    def deregister_source_database_collection_relation(self, source, database, collection, relation, rebuild=False):
        record = self.get_source_database_collection_relation(source, database, collection, relation)
        super().deregister(record, rebuild=rebuild)

    def get_source_database_collection_relations(self, source, database, collection):
        return super().filter_record_contents(collection, 'collection', f'/source/{source}/database/{database}', filter_type='relation')

    def get_source_database_collection_relation(self, source, database, collection, relation):
        return super().filter_record_contents(collection, 'collection', f'/source/{source}/database/{database}', filter_type='relation', filter_name=relation, single=True)

    # description
    def get_source_database_collection_relation_description(self, source, database, collection, relation):
        return super().get_record_description(relation, 'relation', f'/source/{source}/database/{database}/collection/{collection}')

    def set_source_database_collection_relation_description(self, source, database, collection, relation, description, rebuild=False):
        super().set_record_description(relation, 'relation', f'/source/{source}/database/{database}/collection/{collection}', description, rebuild=rebuild)

    # properties
    def get_source_database_collection_relation_properties(self, source, database, collection, relation):
        return super().get_record_properties(relation, 'relation', f'/source/{source}/database/{database}/collection/{collection}')

    def get_source_database_collection_relation_property(self, source, database, collection, relation, key):
        return super().get_record_property(relation, 'relation', f'/source/{source}/database/{database}/collection/{collection}', key)

    def set_source_database_collection_relation_property(self, source, database, collection, relation, key, value, rebuild=False):
        super().set_record_property(relation, 'relation', f'/source/{source}/database/{database}/collection/{collection}', key, value, rebuild=rebuild)

    

    
    ######### source/database/collection/relation/attribute 
    def register_source_database_collection_relation_attribute(self, source, database, collection, relation, attribute, description="", properties={}, rebuild=False):
        super().register_record(attribute, 'attribute', f'/source/{source}/database/{database}/collection/{collection}/relation/{relation}', description=description, properties=properties, rebuild=rebuild)

    
    def update_source_database_collection_relation_attribute(self, source, database, collection, relation, attribute, description=None, properties=None, rebuild=False):
        scope = f'/source/{source}/database/{database}/collection/{collection}/relation/{relation}'
        return super().update_record(attribute, 'attribute', scope, description=description, properties=properties, rebuild=rebuild)


    def deregister_source_database_collection_relation_attribute(self, source, database, collection, relation, attribute, rebuild=False):
        record = self.get_source_database_collection_relation_attribute(source, database, collection, relation, attribute)
        super().deregister(record, rebuild=rebuild)

    
    def get_source_database_collection_relation_attributes(
        self, source, database, collection, relation):
        scope = f'/source/{source}/database/{database}/collection/{collection}/relation/{relation}'
        return super().filter_record_contents(relation, 'relation', scope, filter_type='attribute')

    def get_source_database_collection_relation_attribute(
        self, source, database, collection, relation, attribute):
        scope = f'/source/{source}/database/{database}/collection/{collection}/relation/{relation}'
        return super().filter_record_contents(relation, 'relation', scope, filter_type='attribute', filter_name=attribute, single=True)

    def set_source_database_collection_relation_attribute_property(self, source, database, collection, relation, attribute, key, value, rebuild=False):
        scope = f'/source/{source}/database/{database}/collection/{collection}/relation/{relation}'
        super().set_record_property(attribute, 'attribute', scope, key, value, rebuild=rebuild)


    def get_source_database_collection_relation_attribute_property(self, source, database, collection, relation, attribute, key):
        scope = f'/source/{source}/database/{database}/collection/{collection}/relation/{relation}'
        super().get_record_property(attribute, 'attribute', scope, key)

    
    
    ######### sync
    # source connection (part of properties)
    def get_source_connection(self, source):
        return self.get_source_property(source, 'connection')

    def set_source_connection(self, source, connection, rebuild=False):
        self.set_source_property(source, 'connection', connection, rebuild=rebuild)

    def connect_source(self, source):
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

    
    def collect_source_metadata(self, source, recursive=False, rebuild=False):
        # TODO
        pass

    
    def collect_source_database_metadata(self, source, database, recursive=False, rebuild=False):
        ## TODO
        pass

    def collect_source_database_collection_metadata(self, source, database, collection, recursive=False, rebuild=False):
        entities = self.get_source_database_collection_entities(source, database, collection)
        
        #### enriching description #############################
        for entity in entities:
            entity_name = entity.get("name")
            
            attributes = self.get_source_database_collection_entity_attributes(source, database, collection, entity_name)
            entity_attribute_description = self.metadata.enrich_entity(entity, attributes)
        
            try:
                parsed = json_utils.safe_json_parse(entity_attribute_description)
                if not parsed:
                    logging.warning(f"Entity {entity} returned invalid or empty JSON.")
                    continue
            except json.JSONDecodeError:
                logging.warning("LLM did not return valid JSON. Skipping entity enrichment.")
                parsed = {}

            table_desc = parsed.get("table_description", "")
            attribute_descs = parsed.get("attributes", {})
    
            self.set_source_database_collection_entity_description(
                source, database, collection, entity_name, table_desc, rebuild=rebuild)

            for attr, desc in attribute_descs.items():
                self.set_source_database_collection_entity_attribute_description(
                    source, database, collection, entity_name, attr, desc, rebuild=rebuild)
        
    
    def collect_source_stats(self, source, recursive=False, rebuild=False):
        source_connection = self.connect_source(source)
        if source_connection:
            source_stats = source_connection.fetch_source_stats()
            if source_stats:
                self.set_source_property(source, "stats", source_stats, rebuild=rebuild)

    
    def collect_source_database_stats(self, source, database, source_connection=None, recursive=False, rebuild=False):
        if source_connection is None:
            source_connection = self.connect_source(source)
        if source_connection:
            db_stats = source_connection.fetch_database_stats(database)
            if db_stats:
                self.set_source_database_property(source, database, "stats", db_stats, rebuild=rebuild)

    
    def collect_source_database_collection_stats(self, source, database, collection, source_connection=None, recursive=False, rebuild=False, sample_limit=10):
        
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
                        attr_stats = source_connection.fetch_property_stats(
                            database, collection, entity, attr_name, sample_limit=sample_limit)
                        
                        # Store stats under this attribute
                        self.set_source_database_collection_entity_attribute_property(
                            source, database, collection, entity, attr_name,  "stats", attr_stats, rebuild=rebuild)
                
    
    def sync_all(self, recursive=False):
        # TODO
        pass

    def sync_source(self, source, recursive=False, rebuild=False):
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
            self.update_source(source, description=description, properties=properties, rebuild=rebuild)

            ### this call will be removed once UI supports calling source stats 
            self.collect_source_stats(source, recursive=recursive, rebuild=rebuild)
        
    
            # fetch databases
            fetched_dbs = source_connection.fetch_databases()
            fetched_dbs_set = set(fetched_dbs)

            # get existing databases
            registry_dbs = self.get_source_databases(source)
            registry_dbs_set = set(json_utils.json_query(registry_dbs, '$.name', single=False))

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
            self.update_source_database(source, database, description=description, properties=properties, rebuild=rebuild)

            ### this call will be removed from here, when UI supports callign corresponding API
            self.collect_source_database_stats(source, database, source_connection=source_connection, recursive=recursive, rebuild=rebuild)
         
            # fetch collections
            fetched_collections = source_connection.fetch_database_collections(database)
            fetched_collections_set = set(fetched_collections)

            # get existing collections
            registry_collections = self.get_source_database_collections(source, database)
            registry_collections_set = set(json_utils.json_query(registry_collections, '$.name', single=False))

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

            self.update_source_database_collection(source, database, collection, description=description, properties=properties, rebuild=rebuild)


            entities = source_connection.fetch_database_collection_entities(database, collection)
            relations = source_connection.fetch_database_collection_relations(database, collection)

            
            
            fetched_entities_set = set(entities.keys())
            fetched_relations_set = set(relations.keys())

            ## entities
            registry_entities = self.get_source_database_collection_entities(source, database, collection)
            registry_entities_set = set(json_utils.json_query(registry_entities, '$.name', single=False))

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

                registry_attrs_set = set(registry_attrs.keys())
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
          
            
            
            ### there are separate APIs for these, however still calling from here since UI is not enabled to call those APIs. These calls will be removed from here when UI supports 
            ### corresponding API calling 
            self.collect_source_database_collection_stats(source, database, collection, source_connection=source_connection, recursive=recursive, rebuild=rebuild, sample_limit=10)
            self.collect_source_database_collection_metadata(source, database, collection, recursive=recursive, rebuild=rebuild) 
          
            ## relations
            # get existing schema entities
            registry_relations = self.get_source_database_collection_relations(source, database, collection)
            registry_relations_set = set(json_utils.json_query(registry_relations, '$.name', single=False))

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

                registry_attrs_set = set(registry_attrs.keys())
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