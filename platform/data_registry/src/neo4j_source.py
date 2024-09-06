###### OS / Systems
from curses import noecho
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/utils')

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
import neo4j
from utils import neo4j_connection

#### Helper Functions
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        return json.JSONEncoder.default(self, o)

#### DataSource for NEO4J
class NEO4JSource(DataSource):
    def __init__(self, name, properties={}):
        super().__init__(name, properties=properties)
        

    ###### initialization
    def _initialize_properties(self):
        super()._initialize_properties()

        # source protocol 
        self.properties['protocol'] = "bolt"

    ###### connection
    def _connect(self, **connection):
        host = connection['host']
        port = connection['port']

        user = connection['user'] 
        pwd = connection['password'] 
        connection_url = self.properties['protocol'] + "://" + host + ":" + str(port)    
       
        return neo4j_connection.NEO4J_Connection(connection_url, user, pwd)

    ######### source
    def fetch_metadata(self):
        return {}

    def fetch_schema(self):
        return {}

    ######### database
    def fetch_databases(self):
        dbs = []
        result = self.connection.run_query("SHOW DATABASES;")

        for record in result:
            dbs.append(record["name"])
        return dbs

    def fetch_database_metadata(self, database):
        return {}

    def fetch_database_schema(self, database):
        return {}

   ######### database/collection
    def fetch_database_collections(self, database):
        collections = [database]
        return collections

    def fetch_database_collection_metadata(self, database, collection):
        return {}

    def fetch_database_collection_schema(self, database, collection):
        
        result = self.connection.run_query("CALL db.schema.visualization",single=True, single_transaction=False)

        schema = self.extract_schema(result[0])
        return schema.to_json()

    def extract_schema(self, result):
        schema = Schema()

        nodes = result['nodes']
        relationships = result['relationships']

        for node in nodes:
            schema.add_entity(node['type'])

        for relation in relationships:
            schema.add_relation(relation['from']['type'],relation['type'],relation['to']['type'])
        return schema


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

    # create a neo4j data source
    source = NEO4JSource(args.name, properties=properties)

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
