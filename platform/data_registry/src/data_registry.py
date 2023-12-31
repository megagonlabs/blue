###### OS / Systems
from curses import noecho
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/agent/')
sys.path.append('./lib/platform/')


###### 
import time
import argparse
import logging
import time
import uuid
import random

###### Parsers, Formats, Utils
import re
import csv
import json
from utils import json_utils

import itertools
from tqdm import tqdm

###### Backend, Databases
import redis
from redis.commands.json.path import Path
from redis.commands.search.field import TextField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

#######
import numpy as np
from sentence_transformers import SentenceTransformer

###### Blue
from agent import Agent
from registry import Registry

###### Supported Data Sources
from mongodb_source import MongoDBSource
from neo4j_source import NEO4JSource

class DataRegistry(Registry):
    def __init__(self, name, properties={}):
        super().__init__(name, properties=properties)
        

    ###### initialization
    def _initialize_properties(self):
        super()._initialize_properties()

        # registry type
        self.properties['type'] = "data"

    ######### source
    def register_source(self, source, description="", properties={}, rebuild=False):
        self.register_record(source, 'source', '/', description=description, properties=properties, rebuild=rebuild)

    def update_source(self, source, description=None, properties=None, rebuild=False):
        self.update_record(source, 'source', '/', description=description, properties=properties, rebuild=rebuild)

    def deregister_source(self, source, rebuild=False):
        record = self.get_record(source, '/')
        self.deregister(record, rebuild=rebuild)

    def get_source(self, source):
        return super().get_record(source, '/')

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


    ######### source/database
    def register_source_database(self, source, database, description="", properties={}, rebuild=False):
        self.register_record(database, 'database', '/'+source, description=description, properties=properties, rebuild=rebuild)

    def update_source_database(self, source, database, description=None, properties=None, rebuild=False):
        self.update_record(database, 'database', '/'+source, description=description, properties=properties, rebuild=rebuild)

    def deregister_source_database(self, source, database, rebuild=False):
        record = self.get_record(database, '/'+source)
        self.deregister(record, rebuild=rebuild)

    def get_source_databases(self, source):
        return super().get_record_contents(source, '/', type='database')

    def get_source_database(self, source, database):
        return super().get_record_content(source, '/', database, type='database')


    def register_source_database(self, source, database, description, properties={}, rebuild=False):
        super().register_record(self, database, 'database', '/'+source, description=description, properties=properties, rebuild=rebuild)

    def deregister_source_database(self, source, database, rebuild=False):
        record = self.get_source_database(source, database)
        super().deregister(record, rebuild=rebuild)

    # description
    def get_source_database_description(self, source, database):
        return super().get_record_description(database, '/'+source)

    def set_source_database_description(self, source, database, description, rebuild=False):
        super().set_record_description(database, '/'+source, description, rebuild=rebuild)

    # properties
    def get_source_database_properties(self, source, database):
        return super().get_record_properties(database, '/'+source)

    def get_source_database_property(self, source, database, key):
        return super().get_record_property(database, '/'+source, key)

    def set_source_database_property(self, source, database, key, value, rebuild=False):
        super().set_record_property(database, '/'+source, key, value, rebuild=rebuild)


   ######### source/database/collection
    def register_source_database_collection(self, source, database, collection, description="", properties={}, rebuild=False):
        self.register_record(collection, 'collection', '/'+source+'/'+database, description=description, properties=properties, rebuild=rebuild)

    def update_source_database_collection(self, source, database, collection, description=None, properties=None, rebuild=False):
        self.update_record(collection, 'collection', '/'+source+'/'+database, description=description, properties=properties, rebuild=rebuild)

    def deregister_source_database_collection(self, source, database, collection, rebuild=False):
        record = self.get_record(collection, '/'+source+'/'+database)
        self.deregister(record, rebuild=rebuild)

    def get_source_database_collections(self, source, database):
        return super().get_record_contents(database, '/'+source, type='collection')

    def get_source_database_collection(self, source, database, collection):
        return super().get_record_content(database, '/'+source, collection, type='collection')


    # description
    def get_source_database_collection_description(self, source, database, collection):
        return super().get_record_description(collection, '/'+source+'/'+database)

    def set_source_database_collection_description(self, source, database, collection, description, rebuild=False):
        super().set_record_description(collection, '/'+source+'/'+database, description, rebuild=rebuild)

    # properties
    def get_source_database_collection_properties(self, source, database, collection):
        return super().get_record_properties(collection, '/'+source+'/'+database)

    def get_source_database_collection_property(self, source, database, collection, key):
        return super().get_record_property(collection, '/'+source+'/'+database, key)

    def set_source_database_collection_property(self, source, database, collection, key, value, rebuild=False):
        super().set_record_property(collection, '/'+source+'/'+database, key, value, rebuild=rebuild)


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

        return source_connection

    def sync_all(self, recursive=False):
        # TODO
        pass

    def sync_source(self, source, recursive=False, rebuild=False):
        source_connection = self.connect_source(source)
        if source_connection:
            # fetch source metadata
            metadata = source_connection.fetch_metadata()

            # fetch source schema
            schema = source_connection.fetch_schema()

            # update source properties
            properties = {}
            properties['metadata'] = metadata 
            properties['schema'] = schema
            description = ""
            if 'description' in metadata:
                description = metadata['description']
            self.update_source(source, description=description, properties=properties, rebuild=rebuild)

            # fetch databases
            fetched_dbs = source_connection.fetch_databases()
            fetched_dbs_set = set(fetched_dbs)

            # get existing databases
            registry_dbs = self.get_source_databases(source)
            registry_dbs_set = set(json_utils.json_query(registry_dbs,'$.name', single=False))

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

            # fetch database schema
            schema = source_connection.fetch_database_schema(database)

            # update source database properties
            properties = {}
            properties['metadata'] = metadata 
            properties['schema'] = schema
            description = ""
            if 'description' in metadata:
                description = metadata['description']
            self.update_source_database(source, database, description=description, properties=properties, rebuild=rebuild)


            # fetch collections
            fetched_collections = source_connection.fetch_database_collections(database)
            fetched_collections_set = set(fetched_collections)

            # get existing collections
            registry_collections = self.get_source_database_collections(source, database)
            registry_collections_set = set(json_utils.json_query(registry_collections,'$.name', single=False))

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
            print("REMOVES:")
            print(removes)
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

            # fetch collection schema
            schema = source_connection.fetch_database_collection_schema(database, collection)
            
            # update source database collection properties
            properties = {}
            properties['metadata'] = metadata 
            properties['schema'] = schema
            description = ""
            if 'description' in metadata:
                description = metadata['description']
            self.update_source_database_collection(source, database, collection, description=description, properties=properties, rebuild=rebuild)
   

    ######
    def _start(self):
        super()._start()

        # logging.info('Starting session {name}'.format(name=self.name))
        self._start_connection()
        
         # initialize registry data
        self._init_registry_namespace()

        # build search index on registry
        self._init_search_index()

        logging.info('Started registry {name}'.format(name=self.name))

#######################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, default='default', help='name of the data registry')
    parser.add_argument('--properties', type=str, help='properties in json format')
    parser.add_argument('--loglevel', default="INFO", type=str, help='log level')
    parser.add_argument('--add', type=str, default=None, help='json array of data elements to be add to the registry')
    parser.add_argument('--update', type=str, default=None, help='json array of data elements to be updated in the registry')
    parser.add_argument('--remove', type=str, default=None, help='json array of data elements names to be removed')
    parser.add_argument('--search', type=str, default=None, help='search registry with keywords')
    parser.add_argument('--type', type=str, default=None, help='search registry limited to data metadata type [source, database, collection]')
    parser.add_argument('--scope', type=str, default=None, help='limit to scope')
    parser.add_argument('--page', type=int, default=0, help='search result page, default 0')
    parser.add_argument('--page_size', type=int, default=5, help='search result page size, default 5')
    parser.add_argument('--list', type=bool, default=False, action=argparse.BooleanOptionalAction, help='list data elements in the registry')
    parser.add_argument('--approximate', type=bool, default=False, action=argparse.BooleanOptionalAction, help='use approximate (embeddings) search')
    parser.add_argument('--hybrid', type=bool, default=False, action=argparse.BooleanOptionalAction, help='use hybrid (keyword and approximate) search')
    parser.add_argument('--sync', type=bool, default=False, action=argparse.BooleanOptionalAction, help='sync registry contents')
    parser.add_argument('--recursive', type=bool, default=False, action=argparse.BooleanOptionalAction, help='sync recursively')
    parser.add_argument('--source', type=str, default=None, help='data source')
    parser.add_argument('--database', type=str, default=None, help='database')
    parser.add_argument('--collection', type=str, default=None, help='collection')
 
    args = parser.parse_args()
   
    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())

    print(args)
    # set properties
    properties = {}
    p = args.properties
    if p:
        # decode json
        properties = json.loads(p)

    # create a registry
    registry = DataRegistry(args.name, properties=properties)

    #### LIST
    if args.list:
        # list the records in registry
        results = registry.list_records()
        logging.info(results)

    #### ADD
    if args.add:
        records = json.loads(args.add)
        print(records)
        for record in records:
            registry.register_record_json(record)
    
        # index registry
        registry.build_index()

        # list the registry
        results = registry.list_records()
        logging.info(results)

    #### UPDATE
    if args.update:
        records = json.loads(args.update)
        print(records)
        for record in records:
            registry.update_record_json(record)
    
        # index registry
        registry.build_index()

        # list the registry
        results = registry.list_records()
        logging.info(results)

    #### REMOVE
    if args.remove:
        records = json.loads(args.remove)
        print(records)
        for record in records:
            # deregister
            registry.deregister(record, rebuild=True)

        # list the registry
        results = registry.list_records()
        logging.info(results)


    #### SEARCH
    if args.search:
        keywords = args.search

        # search the registry
        results = registry.search_records(keywords, type=args.type, scope=args.scope, approximate=args.approximate, hybrid=args.hybrid, page=args.page, page_size=args.page_size)
    
        logging.info(json.dumps(results, indent=4))

    #### SYNC
    if args.sync:
        if args.source:
            if args.database:
                if args.collection:
                    registry.sync_source_database_collection(args.source, args.database, args.collection)
                else:
                    registry.sync_source_database(args.source, args.database, recursive=args.recursive)
            else:
                registry.sync_source(args.source, recursive=args.recursive)
            
        else:
            registry.sync_all(recursive=args.recursive)

        # index registry
        registry.build_index()
