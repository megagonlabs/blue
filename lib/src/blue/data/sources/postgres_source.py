###### Parsers, Formats, Utils
import pandas as pd
import numpy as np
import json
import copy


###### Source specific libs
import psycopg2

###### Blue
from blue.data.source import DataSource
from blue.data.schema import DataSchema



###############
### PostgresDBSource
#
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
            if db.find("template") == 0:
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

        # exclude 'pg_catalog', 'information_schema'
        query = "SELECT DISTINCT table_schema FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog', 'information_schema');"
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

    
    def fetch_enum_types(self, db_connection):
        query = """
        SELECT
          n.nspname AS schema,
          t.typname AS type_name,
          e.enumlabel AS enum_value
        FROM
          pg_type t
        JOIN
          pg_enum e ON t.oid = e.enumtypid
        JOIN
          pg_catalog.pg_namespace n ON n.oid = t.typnamespace
        WHERE
          n.nspname NOT IN ('pg_catalog', 'information_schema')
        ORDER BY
          t.typname, e.enumsortorder;
        """
        cursor = db_connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()

        enum_types = {}  

        for schema, type_name, enum_value in data:
            if type_name not in enum_types:
                enum_types[type_name] = []
            enum_types[type_name].append(enum_value)

        
    def fetch_database_collection_schema(self, database, collection):
        db_connection = self._db_connect(database)

        query = """
        SELECT table_name, column_name, data_type, udt_name
        FROM information_schema.columns
        WHERE table_schema = %s
        """
        cursor = db_connection.cursor()
        cursor.execute(query, (collection,))
        data = cursor.fetchall()

        enum_types = self.fetch_enum_types(db_connection)
        schema = DataSchema()

        for table_name, column_name, data_type, udt_name in data:
            if not schema.has_entity(table_name):
                schema.add_entity(table_name)

            if udt_name in enum_types:
                schema.add_entity_property(table_name, column_name, {
                    "type": data_type,
                    "enum": enum_types[udt_name]
                })
            else:
                schema.add_entity_property(table_name, column_name, data_type)

        self._db_disconnect(db_connection)

        return schema.to_json()

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