# os
import os

###### Parsers, Formats, Utils
import pandas as pd
import numpy as np
import json
import copy


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

    
    def create_database(self, database, properties={}, overwrite=False):
        """Create a new SQLite database file."""
        # Check if database file already exists
        db_path = self._get_database_path(database)
        if os.path.exists(db_path):
            if overwrite:
                self.logger.info(f"Overwriting existing database file '{db_path}'")
                os.remove(db_path)
            else:
                self.logger.info(f"Database file '{db_path}' already exists, skipping creation")
                return {"status": "skipped"}
        
        db_connection = self._db_connect(database)
        self._db_disconnect(db_connection)
        self.logger.info(f"Successfully created SQLite database '{database}' at '{db_path}'")
        return {"status": "success"}

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
        ## for sqlite, there is no collection actually. We are returning "public" to have data registry entry
        collections = []
        collections.append("public")
        return collections 
        
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
        return schema.get_entities()

    
    def fetch_database_collection_relations(self, database, collection):
        return {}
    

    def create_database_collection(self, database, collection, properties={}, overwrite=False):
        """The SQLite collection is the database. NOP - only registry update needed"""
        return {"status": "registry_only"}

    ######### source/database/collection/entity
    def create_database_collection_entity(self, database, collection, entity, properties={}, overwrite=False):
        """Create a new SQLite table (entity)."""
        # Check if table already exists
        db_connection = self._db_connect(database)
        cursor = db_connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (entity,))
        table_exists = cursor.fetchone() is not None
        self._db_disconnect(db_connection)
        
        if table_exists:
            if overwrite:
                self.logger.info(f"Overwriting existing table '{entity}'")
                drop_query = f"DROP TABLE IF EXISTS \"{entity}\""
                self.execute_query(drop_query, database=database, optional_properties={"commit": True})
            else:
                self.logger.info(f"Table '{entity}' already exists, skipping creation")
                return {"status": "skipped"}

        query = "CREATE TABLE " + f"\"{entity}\""

        # column definitions
        column_definitions_str = ""
        column_definitions = properties['cols_definition']
        for i, column_def in enumerate(column_definitions):
            if i > 0:
                column_definitions_str += ", "
            column_definitions_str += column_def['name']
            if 'type' in column_def:
                column_definitions_str += " " + column_def['type']
            if 'misc' in column_def:
                column_definitions_str += " " + column_def['misc']

        # add primary key constraint if provided
        primary_key = properties.get('primary_key', [])
        if primary_key:
            pk_cols = ', '.join([f'"{col}"' for col in primary_key])
            pk_clause = f", PRIMARY KEY ({pk_cols})"
            column_definitions_str += pk_clause

        # add foreign key constraints if provided
        foreign_keys = properties.get('foreign_keys', [])
        if foreign_keys:
            for fk in foreign_keys:
                source_cols = ', '.join([f'"{col}"' for col in fk['foreign_keys_source_columns']])
                target_cols = ', '.join([f'"{col}"' for col in fk['foreign_keys_target_columns']])
                fk_clause = f", FOREIGN KEY ({source_cols}) REFERENCES \"{fk['foreign_keys_target_table']}\" ({target_cols})"
                column_definitions_str += fk_clause

        query += "( " + column_definitions_str + " )"
        self.logger.info(f"Generated SQL query: {query}")
        self.execute_query(query, database=database, optional_properties={"commit": True})
        self.logger.info(f"Successfully created table '{entity}' in collection '{collection}' of database '{database}' in SQLite")
        return {"status": "success"}

    ######### source/database/collection/relation
    def create_database_collection_relation(self, database, collection, relation, properties={}, overwrite=False):
        """SQLite doesn't support adding foreign keys after table creation.
        We only support adding foreign keys when creating tables (see create_database_collection_entity).
        """
        return {"status": "skipped"}

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
        """
        Fetch basic stats for an SQLite database file.
        """
        stats = {}
       
        db_path = self._get_database_path(database)
        
        if not os.path.exists(db_path):
            self.logger.warning(f"Database file {db_path} does not exist")
            return stats

        try:
            # Size in bytes
            stats["size_bytes"] = os.path.getsize(db_path)
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()

            # Number of tables
            cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            stats["table_count"] = cur.fetchone()[0]

            conn.close()
            
        except Exception as e:
            self.logger.warning(f"Error fetching SQLite database stats: {e}")
        
        return stats


    def fetch_collection_stats(self, database, collection_name, entities, relations):
        
        stats = {}
        num_entities = len(entities)
        num_relations = len(relations)
        
        stats["num_entities"] = num_entities
        stats["num_relations"] = num_relations
    
        return stats


    def fetch_entity_stats(self, database, collection, entity):
        """
        Fetch stats for a single SQLite table (entity).
        Returns:
            row_count: number of rows in the table
        """
        ### collection is ignored, 
        stats = {}
        table_name = entity
        db_path = self._get_database_path(database)

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            query = f'SELECT COUNT(*) FROM "{table_name}";'
            cursor.execute(query)
            stats["row_count"] = cursor.fetchone()[0]

            conn.close()

        except sqlite3.Error as e:
            stats["row_count"] = None

        return stats

    def fetch_property_stats(self, database, collection, table, property_name, sample_limit=10):
        """
        SQLite version of property stats.
        collection is ignored (no schemas in SQLite).
        """
        db_path = self._get_database_path(database)
        
        stats = {}

        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cursor = conn.cursor()

            # Find column type from PRAGMA
            cursor.execute(f"PRAGMA table_info({table});")
            
            columns = cursor.fetchall()
            column_type = None
            
            for col in columns:
                if col[1] == property_name:  # col[1] = column name, col[2] = type
                    column_type = col[2]
                    break

            column = f'"{property_name}"'

            # Basic counts
            cursor.execute(f"""
                SELECT 
                    COUNT({column}) AS non_null_count,
                    COUNT(DISTINCT {column}) AS distinct_count,
                    SUM(CASE WHEN {column} IS NULL THEN 1 ELSE 0 END) AS null_count
                FROM {table};
            """)
            row = cursor.fetchone()
            stats["count"] = row[0]
            stats["distinct_count"] = row[1]
            stats["null_count"] = row[2]

            # Sample values
            cursor.execute(f"""
                SELECT {column}
                FROM {table}
                WHERE {column} IS NOT NULL
                LIMIT {sample_limit};
            """)


            stats["sample_values"] = [r[0] for r in cursor.fetchall()]

            # Min / Max (only if numeric or date-ish type)
            include_min_max = column_type and any(
                t in column_type.upper() for t in ["INT", "REAL", "NUM", "DATE", "TIME"]
            )
            if include_min_max:
                cursor.execute(f"SELECT MIN({column}), MAX({column}) FROM {table};")
                min_val, max_val = cursor.fetchone()
                stats["min"] = min_val
                stats["max"] = max_val
            else:
                stats["min"] = None
                stats["max"] = None

            # No equivalent of pg_stats.most_common_vals in SQLite
            stats["most_common_vals"] = []
            return stats

        except Exception as e:
            self.logger.warning(f"Failed to fetch property stats for {table}.{property_name}: {str(e)}")
            return {}
        finally:
            self._db_disconnect(conn)
