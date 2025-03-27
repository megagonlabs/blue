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


class DataSource():
    def __init__(self, name, properties={}):

        self.name = name

        self._initialize(properties=properties)

        self._start()

    ###### initialization
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        self.properties = {}

        # source protocol 
        self.properties['protocol'] = "default"

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

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
        # logging.info('Starting session {name}'.format(name=self.name))
        self._start_connection()
        
        logging.info('Started source {name}'.format(name=self.name))

    def _stop(self):
        self._stop_connection()

        logging.info('Stopped source {name}'.format(name=self.name))

    ######### source
    def fetch_metadata(self):
        return {}

    def fetch_schema(self):
        return {}

    ######### database
    def fetch_databases(self):
        return []

    def fetch_database_metadata(self, database):
        return {}

    def fetch_database_schema(self, database):
        return {}

   ######### database/collection
    def fetch_database_collections(self, database):
        return []

    def fetch_database_collection_metadata(self, database, collection):
        return {}

    def fetch_database_collection_schema(self, database, collection):
        return {}

    def execute_query(self, query, database=None, collection=None):
        return [{}]

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

    # create a data source
    source = DataSource(args.name, properties=properties)

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
                result = source.fetch_database_collection_schema(args.database, args.collection)
            else:
                result = source.fetch_database_schema(args.database)
        else:
            results = source.fetch_schema()

    #### METADATA
    elif args.metadata:
        if args.database:
            if args.collection:
                result = source.fetch_database_collection_metadata(args.database, args.collection)
            else:
                result = source.fetch_database_metadata(args.database)
        else:
            results = source.fetch_metadata()

    logging.info(json.dumps(results, indent=4))
