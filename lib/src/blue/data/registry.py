###### Parsers, Formats, Utils
import argparse
import logging
import json


###### Blue
from blue.utils import json_utils
from blue.registry import Registry

###### Supported Data Sources
from blue.data.sources.mongodb_source import MongoDBSource
from blue.data.sources.neo4j_source import NEO4JSource
from blue.data.sources.postgres_source import PostgresDBSource
from blue.data.sources.mysql_source import MySQLDBSource

###############
### DataRegistry
#
class DataRegistry(Registry):
    def __init__(self, name="DATA_REGISTRY", id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):
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
        return super().get_record(source, 'source')

    # description
    def get_source_description(self, source):
        return super().get_record_description(source, '/')

    def set_source_description(self, source, description, rebuild=False):
        super().set_record_description(source, '/', description, rebuild=rebuild)

    # properties
    def get_source_properties(self, source):
        return super().get_record_properties(source, '/')

    def get_source_property(self, source, key):
        return super().get_record_property(source, '/', key)

    def set_source_property(self, source, key, value, rebuild=False):
        super().set_record_property(source, '/', key, value, rebuild=rebuild)

    def delete_source_property(self, source, key, rebuild=False):
        super().delete_record_property(source, '/', key, rebuild=rebuild)

    ######### source/database
    def register_source_database(self, source, database, description="", properties={}, rebuild=False):
        super().register_record(database, 'database', '/' + source, description=description, properties=properties, rebuild=rebuild)

    def update_source_database(self, source, database, description=None, properties=None, rebuild=False):
        super().update_record(database, 'database', '/' + source, description=description, properties=properties, rebuild=rebuild)

    def deregister_source_database(self, source, database, rebuild=False):
        record = self.get_source_database(source, database)
        super().deregister(record, rebuild=rebuild)

    def get_source_databases(self, source):
        return super().get_record_contents(source, '/', type='database')

    def get_source_database(self, source, database):
        return super().get_record_content(source, '/', database, type='database')

    # description
    def get_source_database_description(self, source, database):
        return super().get_record_description(database, '/' + source)

    def set_source_database_description(self, source, database, description, rebuild=False):
        super().set_record_description(database, '/' + source, description, rebuild=rebuild)

    # properties
    def get_source_database_properties(self, source, database):
        return super().get_record_properties(database, '/' + source)

    def get_source_database_property(self, source, database, key):
        return super().get_record_property(database, '/' + source, key)

    def set_source_database_property(self, source, database, key, value, rebuild=False):
        super().set_record_property(database, '/' + source, key, value, rebuild=rebuild)

    ######### source/database/collection
    def register_source_database_collection(self, source, database, collection, description="", properties={}, rebuild=False):
        super().register_record(collection, 'collection', '/' + source + '/' + database, description=description, properties=properties, rebuild=rebuild)

    def update_source_database_collection(self, source, database, collection, description=None, properties=None, rebuild=False):
        original_record, merged_record = super().update_record(collection, 'collection', '/' + source + '/' + database, description=description, properties=properties, rebuild=rebuild)
        return original_record, merged_record

    def deregister_source_database_collection(self, source, database, collection, rebuild=False):
        record = self.get_source_database_collection(source, database, collection)
        super().deregister(record, rebuild=rebuild)

    def get_source_database_collections(self, source, database):
        return super().get_record_contents(database, '/' + source, type='collection')

    def get_source_database_collection(self, source, database, collection):
        return super().get_record_content(database, '/' + source, collection, type='collection')

    # description
    def get_source_database_collection_description(self, source, database, collection):
        return super().get_record_description(collection, '/' + source + '/' + database)

    def set_source_database_collection_description(self, source, database, collection, description, rebuild=False):
        super().set_record_description(collection, '/' + source + '/' + database, description, rebuild=rebuild)

    # properties
    def get_source_database_collection_properties(self, source, database, collection):
        return super().get_record_properties(collection, '/' + source + '/' + database)

    def get_source_database_collection_property(self, source, database, collection, key):
        return super().get_record_property(collection, '/' + source + '/' + database, key)

    def set_source_database_collection_property(self, source, database, collection, key, value, rebuild=False):
        super().set_record_property(collection, '/' + source + '/' + database, key, value, rebuild=rebuild)

    ######### source/database/collection/entity
    def register_source_database_collection_entity(self, source, database, collection, entity, description="", properties={}, rebuild=False):
        super().register_record(entity, 'entity', '/' + source + '/' + database + '/' + collection, description=description, properties=properties, rebuild=rebuild)

    def update_source_database_collection_entity(self, source, database, collection, entity, description=None, properties=None, rebuild=False):
        original_record, merged_record = super().update_record(entity, 'entity', '/' + source + '/' + database + '/' + collection, description=description, properties=properties, rebuild=rebuild)
        return original_record, merged_record

    def deregister_source_database_collection_entity(self, source, database, collection, entity, rebuild=False):
        record = self.get_source_database_collection_entity(source, database, collection, entity)
        super().deregister(record, rebuild=rebuild)

    def get_source_database_collection_entities(self, source, database, collection):
        return super().get_record_contents(collection, '/' + source + '/' + database, type='entity')

    def get_source_database_collection_entity(self, source, database, collection, entity):
        return super().get_record_content(collection, '/' + source + '/' + database, entity, type='entity')

    # description
    def get_source_database_collection_entity_description(self, source, database, collection, entity):
        return super().get_record_description(entity, '/' + source + '/' + database + '/' + collection)

    def set_source_database_collection_entity_description(self, source, database, collection, entity, description, rebuild=False):
        super().set_record_description(entity, '/' + source + '/' + database + '/' + collection, description, rebuild=rebuild)

    # properties
    def get_source_database_collection_entity_properties(self, source, database, collection, entity):
        return super().get_record_properties(entity, '/' + source + '/' + database + '/' + collection)

    def get_source_database_collection_entity_property(self, source, database, collection, entity, key):
        return super().get_record_property(entity, '/' + source + '/' + database + '/' + collection, key)

    def set_source_database_collection_entity_property(self, source, database, collection, entity, key, value, rebuild=False):
        super().set_record_property(entity, '/' + source + '/' + database + '/' + collection, key, value, rebuild=rebuild)

    ######### source/database/collection/relation
    def register_source_database_collection_relation(self, source, database, collection, relation, description="", properties={}, rebuild=False):
        super().register_record(relation, 'relation', '/' + source + '/' + database + '/' + collection, description=description, properties=properties, rebuild=rebuild)

    def update_source_database_collection_relation(self, source, database, collection, relation, description=None, properties=None, rebuild=False):
        original_record, merged_record = super().update_record(relation, 'relation', '/' + source + '/' + database + '/' + collection, description=description, properties=properties, rebuild=rebuild)
        return original_record, merged_record

    def deregister_source_database_collection_relation(self, source, database, collection, relation, rebuild=False):
        record = self.get_source_database_collection_relation(source, database, collection, relation)
        super().deregister(record, rebuild=rebuild)

    def get_source_database_collection_relations(self, source, database, collection):
        return super().get_record_contents(collection, '/' + source + '/' + database, type='relation')

    def get_source_database_collection_relation(self, source, database, collection, relation):
        return super().get_record_content(collection, '/' + source + '/' + database, relation, type='relation')

    # description
    def get_source_database_collection_relation_description(self, source, database, collection, relation):
        return super().get_record_description(relation, '/' + source + '/' + database + '/' + collection)

    def set_source_database_collection_relation_description(self, source, database, collection, relation, description, rebuild=False):
        super().set_record_description(relation, '/' + source + '/' + database + '/' + collection, description, rebuild=rebuild)

    # properties
    def get_source_database_collection_relation_properties(self, source, database, collection, relation):
        return super().get_record_properties(relation, '/' + source + '/' + database + '/' + collection)

    def get_source_database_collection_relation_property(self, source, database, collection, relation, key):
        return super().get_record_property(relation, '/' + source + '/' + database + '/' + collection, key)

    def set_source_database_collection_relation_property(self, source, database, collection, relation, key, value, rebuild=False):
        super().set_record_property(relation, '/' + source + '/' + database + '/' + collection, key, value, rebuild=rebuild)

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

        return source_connection

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

            #### fetch collection schema
            schema = source_connection.fetch_database_collection_schema(database, collection)

            entities = schema['entities']
            relations = schema['relations']

            fetched_entities_set = set(entities.keys())
            fetched_relations_set = set(relations.keys())

            ## entities
            # get existing schema entities
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
                self.register_source_database_collection_entity(source, database, collection, entity, description="", properties=entities[entity], rebuild=rebuild)

            # remove
            for entity in removes:
                self.deregister_source_database_collection_entity(source, database, collection, entity)

            # update
            for collection in merges:
                self.update_source_database_collection_entity(source, database, collection, entity, description="", properties=entities[entity], rebuild=rebuild)

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