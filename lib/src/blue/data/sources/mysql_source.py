###### Parsers, Formats, Utils
import pandas as pd
import numpy as np
import json
import copy

###### Source specific libs
import mysql.connector as cpy


###### Blue
from blue.data.source import DataSource
from blue.data.schema import DataSchema


###############
### MySQLDBSource
#
class MySQLDBSource(DataSource):
    def __init__(self, name, properties={}):
        super().__init__(name, properties=properties)

    ###### connection
    def _initialize_connection_properties(self):
        super()._initialize_connection_properties()

        # set host, port, protocol
        self.properties['connection']['host'] = 'localhost'
        self.properties['connection']['port'] = 3306
        self.properties['connection']['protocol'] = 'mysql'

    def _connect(self, **connection):
        c = copy.deepcopy(connection)
        if 'protocol' in c:
            del c['protocol']

        return cpy.connect(**c)

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
        query = "SHOW DATABASES;"
        cursor = self.connection.cursor(buffered=True)
        cursor.execute(query)
        data = cursor.fetchall()
        dbs = []
        for datum in data:
            db = datum[0]
            if db in ('information_schema', 'performance_schema', 'sys', 'mysql'):
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
        ## for mysql, collection is the database, so we ignore the database parameter here 
        databases = self.fetch_databases()
        return databases

    def fetch_database_collection_metadata(self, database, collection):
        return {}

    def fetch_database_collection_entities(self, database, collection):
        # connect to specific database (not source directly)
        db_connection = self._db_connect(database)

        # TODO: Do better ER extraction from tables, columns, exploiting column semantics, foreign keys, etc.
        query = "SELECT table_name, column_name, data_type  from information_schema.columns WHERE table_schema = '{}'".format(database)
        cursor = db_connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        schema = DataSchema()

        for table_name, column_name, data_type in data:
            if not schema.has_entity(table_name):
                schema.add_entity(table_name)
            property_def = {"type": data_type}

            schema.add_entity_property(table_name, column_name, property_def)

        # disconnect
        self._db_disconnect(db_connection)

        return schema.get_entities()

    def fetch_database_collection_relations(self, database, collection):
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
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(data, columns=columns)
        df.fillna(value=np.nan, inplace=True)
        result = json.loads(df.to_json(orient='records'))

        # disconnect
        self._db_disconnect(db_connection)

        return result
