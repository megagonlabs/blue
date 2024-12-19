###### OS / Systems
from curses import noecho
import os
import sys

###### Add lib path
sys.path.append('./lib/')

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

# data source lib
from data_source import DataSource
from schema import Schema

# source specific libs
from pymongo import MongoClient
from bson import ObjectId

#### helper hunctions
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

#### DataSource for MongoDB
class MongoDBSource(DataSource):
    def __init__(self, name, properties={}):
        super().__init__(name, properties=properties)
        

    ###### initialization
    def _initialize_properties(self):
        super()._initialize_properties()

        # source protocol 
        self.properties['protocol'] = "mongodb"

    ###### connection
    def _connect(self, **connection):
        host = connection['host']
        port = connection['port']
        
        connection_url = self.properties['protocol'] + "://" + host + ":" + str(port)    
        return MongoClient(connection_url)

    def _disconnect(self):
        # TODO:
        return None

    ######### source
    def fetch_metadata(self):
        return {}

    def fetch_schema(self):
        return {}

    ######### database
    def fetch_databases(self):
        dbs = self.connection.list_database_names()
        return dbs

    def fetch_database_metadata(self, database):
        return {}

    def fetch_database_schema(self, database):
        return {}



    ######### database/collection
    def fetch_database_collections(self, database):
        collections = self.connection[database].list_collection_names()
        return collections

    def fetch_database_collection_metadata(self, database, collection):
        return {}

    def fetch_database_collection_schema(self, database, collection):
        coll = self.connection[database][collection]
        sample = coll.find_one()

        schema = self.extract_schema(sample)
        return schema.to_json()

    def extract_schema(self, sample, schema=None, source=None):
        if schema is None:
            schema = Schema()

        if source == None:
            source = schema.add_entity("ROOT")

        if type(sample) == dict:
            for key in sample:
                value = sample[key]
                if type(value) == list:
                    target = schema.add_entity(key)
                    # (1)-->(M)
                    schema.add_relation(source, source + ":" + target, target)
                    if len(value) > 0:
                        self.extract_schema(value[0], schema=schema, source=target)
                elif type(value) == dict:
                    target = schema.add_entity(key)
                    # (1)-->(1)
                    schema.add_relation(source, source + ":" + target, target)
                    self.extract_schema(value, schema=schema, source=target)
                else:
                    schema.add_entity_property(source, key, value.__class__.__name__)
                
        return schema


    ######### execute query
    def execute_query(self, query, database=None, collection=None):
        if database is None:
            raise Exception("No database provided")
        
        if collection is None:
            raise Exception("No collection provided")

        db = self.connection[database]
        col = db[collection]

        q = json.loads(query)
        result = col.find(q)
        return result
    
#######################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, default='default', help='name of the data registry')
    parser.add_argument('--properties', type=str, help='properties in json format')
    parser.add_argument('--loglevel', default="INFO", type=str, help='log level')
    parser.add_argument('--list', type=bool, default=False, action=argparse.BooleanOptionalAction, help='list contents')
    parser.add_argument('--metadata', type=bool, default=False, action=argparse.BooleanOptionalAction, help='get metadata')
    parser.add_argument('--schema', type=bool, default=False, action=argparse.BooleanOptionalAction, help='get schema')
    parser.add_argument('--database', type=str, default=None, help='database name')
    parser.add_argument('--collection', type=str, default=None, help='collection name')
    
 
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

    # create a mongodb data source
    source = MongoDBSource(args.name, properties=properties)

    results = {}
    #### LIST
    if args.list:
        results = []
        if args.database:
            results = source.fetch_database_collections(args.database)
        else:
            results = source.fetch_databases()
    
    #### SCHEMA
    elif args.schema:
        if args.database:
            if args.collection:
                results = source.fetch_database_collection_schema(args.database, args.collection)
            else:
                results = source.fetch_database_schema(args.database)
        else:
            results = source.fetch_schema()

    #### METADATA
    elif args.metadata:
        if args.database:
            if args.collection:
                results = source.fetch_database_collection_metadata(args.database, args.collection)
            else:
                results = source.fetch_database_metadata(args.database)
        else:
            results = source.fetch_metadata()

    logging.info(json.dumps(results, indent=4, cls=JSONEncoder))
