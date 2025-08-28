# os
import os

###### Parsers, Formats, Utils
import pandas as pd
import numpy as np
import json
import copy
import logging


###### Source specific libs
import sqlite3

###### Blue
from blue.data.source import DataSource
from blue.data.schema import DataSchema


###############
### SQLiteDBSource
#
class SQLiteDBSource(DataSource):
    def __init__(self, name, properties={}):
        super().__init__(name, properties=properties)

    ###### connection
    def _initialize_connection_properties(self):
        super()._initialize_connection_properties()

        # set host, port, protocol
        self.properties['connection']['host'] = 'localhost'
        self.properties['connection']['port'] = 5432
        self.properties['connection']['protocol'] = 'sqlite'
        self.properties['connection']['database_directory'] = '.'

    def _connect(self, **connection):
        c = copy.deepcopy(connection)
        if 'protocol' in c:
            del c['protocol']

        if 'database' in connection:
            database = connection['database']
            return sqlite3.connect(self._get_database_path(database))
        else:
            # only database specific connection
            return {}

    def _disconnect(self):
        # TODO:
        return None

    # database  path
    def _get_database_directory(self):
        connection_properties = self.properties['connection']
        database_directory = connection_properties['database_directory']

        absolute_database_directory = os.path.abspath(database_directory)
        # make sure it exists, create if not
        os.makedirs(absolute_database_directory, exist_ok=True)
        return absolute_database_directory

    def _get_database_path(self, database):
        database_directory = self._get_database_directory()
        return os.path.join(database_directory, database + ".db")

    ######### source
    def fetch_metadata(self):
        return {}

    def fetch_schema(self):
        return {}

    ######### database
    def fetch_databases(self):
        # get list of dbs from data directory
        ls = os.listdir(self._get_database_directory())
        # return only .db files
        dbs = []
        for d in ls:
            db = d[:-3]
            suffix = d[-3:]
            if suffix == '.db':
                dbs.append(db)

        return dbs

    def fetch_database_metadata(self, database):
        return {}

    
    def create_database(self, database, properties={}):
        # connect and close
        db_connection = self._db_connect(database)
        self._db_disconnect(db_connection)

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
        if connection:
            connection.close()
        return None

    ######### database/collection
    def fetch_database_collections(self, database):
        ## for sqlite, collection is the database, so we ignore the database parameter here 
        databases = self.fetch_databases()
        return databases


    def fetch_database_collection_metadata(self, database, collection):
        return {}

    def fetch_enum_types(self, db_connection):
        # TODO
        return []

    
    def fetch_database_collection_entities(self, database, collection, max_distinct=50, max_ratio=0.1, max_length=100):
        ## for sqlite, database and collection is same     
        """
        For SQLite: since database == collection, we ignore `collection`.
        Returns tables and their column metadata.
        """
        db_connection =  self._db_connect(database)
        cursor = db_connection.cursor()

        # 1. Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        
        result = []
        schema = DataSchema()
          
        for table in tables:
            # 2. Get all columns for this table
        
            if not schema.has_entity(table):
                schema.add_entity(table)

            cursor.execute(f"PRAGMA table_info({table});")
            columns = cursor.fetchall()

            for col in columns:
                # columns schema: (cid, name, type, notnull, dflt_value, pk)
                data_type = col[2]
                column_name = col[1]
                property_def = {"type": data_type}
                
                # TODO: add enum, values to property_def
                property_def["values"] = []
                schema.add_entity_property(table, column_name, property_def)
    
        self._db_disconnect(db_connection)


    
    def fetch_database_collection_relations(self, database, collection):
        return {}
    

    def create_database_collection(self, database, collection, properties={}):
        return {}

    ######### source/database/collection/entity
    def create_database_collection_entity(self, database, collection, entity, properties={}):
        query = "CREATE TABLE IF NOT EXISTS "
        query += entity

        # entity properties
        entity_properties_str = ""
        entity_properties = properties['properties']
        for i, entity_property in enumerate(entity_properties):
            entity_properties_str += " " + entity_property['name']
            if 'type' in entity_property:
                entity_properties_str += " " + entity_property['type']
            if 'misc' in entity_property:
                entity_properties_str += " " + entity_property['misc']
            if i < len(entity_properties) - 1:
                entity_properties_str += ","

        query += "( " + entity_properties_str + " )"
        self.execute_query(query, database=database, optional_properties={"commit": True})

    ######### source/database/collection/relation
    def create_database_collection_relation(self, database, collection, relation, properties={}):
        return {}

    ######### execute query
    def execute_query(self, query, database=None, collection=None, optional_properties={}):
        if database is None:
            raise Exception("No database provided")

        # create connection to db
        db_connection = self._db_connect(database)

        cursor = db_connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()

        # transform to json
        result = {}
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(data, columns=columns)
            df.fillna(value=np.nan, inplace=True)
            result = json.loads(df.to_json(orient='records'))

        # commit
        if 'commit' in optional_properties and optional_properties['commit']:
            db_connection.commit()

        # disconnect
        self._db_disconnect(db_connection)

        return result

    ######### stats

    def fetch_source_stats(self):
        # TODO:
        stats = {}
        return stats

    def fetch_database_stats(self, database):
        # TODO:
        stats = {}
        return stats

    def fetch_collection_stats(self, database, collection_name, schema_json=None, sample_limit=10):
        # TODO:
        stats = {}
        return stats

    def fetch_entity_stats(self, database, collection, entity):
        # TODO:
        stats = {}
        return stats

    def fetch_property_stats(self, database, collection, table, property_name, sample_limit=10):
        # TODO:
        stats = {}
        return stats
