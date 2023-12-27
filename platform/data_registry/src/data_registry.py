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


class DataRegistry(Registry):
    def __init__(self, name, properties={}):

        self.name = name

        self._initialize(properties=properties)

        self._start()

    ###### initialization


    def _initialize_properties(self):
        super()._initialize_properties()

        # registry type
        self.properties['type'] = "data"

    ######### source
    def get_source(self, source):
        return super().get_record(source, '/')

    def get_source_description(self, source):
        return super().get_record_description(source, '/')

    def set_source_description(self, source, description, rebuild=False):
        super().set_record_description(source, '/', description, rebuild=rebuild)

    # source properties
    def get_source_properties(self, source):
        return super().get_record_properties(source, '/')

    def get_source_property(self, source, key):
        return super().get_record_property(source, '/', key)

    def set_source_property(self, source, key, value, rebuild=False):
        super().set_record_property(source, '/', key, value, rebuild=rebuild)

    # source connection (part of properties)
    def get_source_connection(self, source):
        return self.get_source_property(source, 'connection')

    def set_source_connection(self, source, connection, rebuild=False):
        self.set_source_property(source, 'connection', connection, rebuild=rebuild)


    ######### source/database
    def get_source_databases(self, source):
        super().get_record_contents(source, '/', type='database')

    def get_source_database(self, source, database):
        return super().get_record_content(source, '/', database, type='database')


    def set_source_database(self, source, database, description, properties={}, rebuild=False):
        super().register_record(self, database, 'database', '/'+source, description=description, properties=properties, rebuild=rebuild)

    def del_source_database(self, source, database, rebuild=False):
        record = self.get_source_database(source, database)
        super().deregister(self, record, rebuild=rebuild)


   ######### source/database/collection
    def get_source_database_collections(self, source, database):
        super().get_record_contents(database, '/'+source, type='collection')

    def get_source_database_collection(self, source, database, collection):
        return super().get_record_content(database, '/'+source, collection, type='collection')


    def set_source_database_collection(self, source, database, collection, description, properties={}, rebuild=False):
        super().register_record(self, collection, 'collection', '/'+source+'/'+database, description=description, properties=properties, rebuild=rebuild)

    def del_source_database_collecion(self, source, database, collection, rebuild=False):
        record = self.get_source_database_collection(source, database, collection)
        super().deregister(self, record, rebuild=rebuild)


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
    parser.add_argument('--type', type=str, default=None, help='search registry limited to agent metadata type [source, database, collection]')
    parser.add_argument('--scope', type=str, default=None, help='limit to scope')
    parser.add_argument('--page', type=int, default=0, help='search result page, default 0')
    parser.add_argument('--page_size', type=int, default=5, help='search result page size, default 5')
    parser.add_argument('--list', type=bool, default=False, action=argparse.BooleanOptionalAction, help='list data elements in the registry')
    parser.add_argument('--approximate', type=bool, default=False, action=argparse.BooleanOptionalAction, help='use approximate (embeddings) search')
    parser.add_argument('--hybrid', type=bool, default=False, action=argparse.BooleanOptionalAction, help='use hybrid (keyword and approximate) search')
 
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
