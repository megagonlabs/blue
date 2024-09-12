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
import copy

import itertools
from tqdm import tqdm

# data source lib
from data_source import DataSource
from schema import Schema

# source specific libs
import psycopg2

#### Helper Functions
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        return json.JSONEncoder.default(self, o)

#### DataSource for Postgres
class PostgresDBSource(DataSource):
    def __init__(self, name, properties={}):
        super().__init__(name, properties=properties)
        

    ###### initialization
    def _initialize_properties(self):
        super()._initialize_properties()

        # source protocol 
        self.properties['protocol'] = "postgres"

    ###### connection
    def _connect(self, **connection):
        c = copy.deepcopy(connection)
        if 'protocol' in c:
            del c['protocol']

        return psycopg2.connect(**c)

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
        query = "SELECT datname FROM pg_database;"
        cursor = self.connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        dbs = []
        for datum in data:
            db = datum[0]
            # ignore template<d> databases
            if  db.find("template") == 0:
                continue
            dbs.append(db)
        return dbs

    def fetch_database_metadata(self, database):
        return {}

    def fetch_database_schema(self, database):
        return {}

    ######### database/collection
    def _db_connect(self, database):
        # connect to database
        c = copy.deepcopy(self.properties['connection'])
        if 'protocol' in c:
            del c['protocol']
        # override database
        c['database'] = database 

        db_connection = self._connect(**c)
        return db_connection

    def _db_disconnect(self, connection):
        # TODO:
        return None
    
    def fetch_database_collections(self, database):
        # connect to specific database (not source directly)
        db_connection = self._db_connect(database)

        query = "SELECT DISTINCT table_name from information_schema.columns WHERE table_schema NOT IN ('pg_catalog', 'information_schema')"
        cursor = db_connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        collections = []
        for datum in data:
            collections.append(datum[0])

        # disconnect
        self._db_disconnect(db_connection)
        return collections

    def fetch_database_collection_metadata(self, database, collection):
        return {}

    def fetch_database_collection_schema(self, database, collection):
        # connect to specific database (not source directly)
        db_connection = self._db_connect(database)

        # TODO: Do better ER extraction from tables, columns, exploiting column semantics, foreign keys, etc.
        query = "SELECT table_name, column_name  from information_schema.columns WHERE table_schema NOT IN ('pg_catalog', 'information_schema') AND table_name = '" + collection + "';"
        cursor = db_connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()

        schema = Schema()
        
        for datum in data:
            t = datum[0]
            c = datum[1]
            if not schema.has_entity(t):
                schema.add_entity(t)
            if not schema.has_entity(c):
                schema.add_entity(c)
            schema.add_relation(t, t + ":" + c, c)
        
        # disconnect
        self._db_disconnect(db_connection)

        return schema.to_json()


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
    source = PostgresDBSource(args.name, properties=properties)

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
