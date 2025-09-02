###### Parsers, Formats, Utils
import pandas as pd
import numpy as np
import json
import copy
import re

###### Source specific libs
import mysql.connector as cpy


###### Blue
from blue.data.source import DataSource
from blue.data.schema import DataSchema

from blue.utils import json_utils


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
        
        query = "SELECT table_name, column_name, data_type, column_type " \
        "FROM information_schema.columns " \
        "WHERE table_schema = '{}'".format(database)

        cursor = db_connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        schema = DataSchema()

        for table_name, column_name, data_type, column_type in data:
            if not schema.has_entity(table_name):
                schema.add_entity(table_name)
            property_def = {"type": data_type}

            if data_type.lower() == "enum":
                enum_values = re.findall(r"'(.*?)'", column_type)
                property_def["enum"] = enum_values
            

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

    ######### stats

    def fetch_source_stats(self):
            
        stats = {}

        try:
            with self.connection.cursor() as cur:
                cur.execute("SELECT version()")
                stats["version"] = cur.fetchone()[0]
         
        except Exception as e:
            logging.warning(f"Failed to collect source-level stats: {e}")
            stats["error"] = str(e)

        return stats

    def fetch_database_stats(self, database):
            
        conn = self._db_connect(database)
        cur = conn.cursor()
        
        stats = {}
        
        try:
            # Size of database in bytes (summing all tables)
            cur.execute("""
                SELECT IFNULL(SUM(data_length + index_length), 0) AS size_bytes
                FROM information_schema.tables
                WHERE table_schema = %s;
            """, (database,))
            size = cur.fetchone()
            stats["size_bytes"] = size[0] if size else None

        except Exception as e:
            logging.warning(f"Error fetching database stats for {database}: {e}")
        finally:
            cur.close()

        return json_utils.json_safe(stats)

    
    def fetch_collection_stats(self, database, collection_name, entities, relations):
            
        stats = {}
        num_entities = len(entities)
        num_relations = len(relations)
    
        stats["num_entities"] = num_entities
        stats["num_relations"] = num_relations
    
        return stats

    
    def fetch_entity_stats(self, database, collection, entity):
        """
        For MySQL:
        - `database` is the schema (selected when connecting)
        - `collection` can be ignored 
        - `entity` is the table
        """
        
        conn = self._db_connect(database)
        cursor = conn.cursor()

        stats = {}

        try:
            query = f"SELECT COUNT(*) FROM `{entity}`;"
            cursor.execute(query)
            stats["row_count"] = cursor.fetchone()[0]

        except mysql.connector.Error as e:
            logging.warning(f"Failed to get row count for {entity}: {e}")
            stats["row_count"] = None

        finally:
            self._db_disconnect(conn)

        return json_utils.json_safe(stats)

    def fetch_property_stats(self, database, collection, table, property_name, sample_limit=10):
    
        conn = self._db_connect(database)
        cursor = conn.cursor()

        schema = collection 
  
        column = f"`{property_name}`"  
        
        try:
            # 1. Get column data type
            cursor.execute("""
                SELECT DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s;
            """, (schema, table, property_name))

            type_result = cursor.fetchone()
            column_type = type_result[0] if type_result else None

            # Set flags for whether to compute min/max
            include_min_max = column_type in (
            'integer', 'bigint', 'smallint', 'numeric', 'real', 'double precision',
            'date', 'timestamp without time zone', 'timestamp with time zone',
            'boolean', 'enum'
            )

            # 2. Build the main query
            query = f"""
                SELECT
                    COUNT({column}) AS non_null_count,
                    COUNT(DISTINCT {column}) AS distinct_count,
                    SUM(CASE WHEN {column} IS NULL THEN 1 ELSE 0 END) AS null_count
                FROM `{schema}`.`{table}`;
            """

            cursor.execute(query)
            row = cursor.fetchone()

            stats = {
                "count": row[0],
                "distinct_count": row[1],
                "null_count": row[2],
            }   

            # 3. Sample values
            cursor.execute(f"""
                SELECT {column}
                FROM `{schema}`.`{table}`
                WHERE {column} IS NOT NULL
                LIMIT {sample_limit};
            """)

            stats["sample_values"] = [r[0] for r in cursor.fetchall()]

            # 4. Min/Max if numeric/date type
            if include_min_max:
                cursor.execute(f"""
                    SELECT MIN({column}), MAX({column})
                    FROM `{schema}`.`{table}`;
                """)
                min_max = cursor.fetchone()
                stats["min"] = min_max[0]
                stats["max"] = min_max[1]
            else:
                stats["min"] = None
                stats["max"] = None

            # 5. MySQL does not have pg_stats, but we can approximate "most common values"
            cursor.execute(f"""
                SELECT {column}, COUNT(*) AS freq
                FROM `{schema}`.`{table}`
                WHERE {column} IS NOT NULL
                GROUP BY {column}
                ORDER BY freq DESC
                LIMIT 5;
            """)
            stats["most_common_vals"] = [r[0] for r in cursor.fetchall()]


            return json_utils.json_safe(stats)

        except Exception as e:
            logging.warning(f"Failed to fetch property stats for {collection}.{table}.{property_name}: {str(e)}")
            return {}
        finally:
            self._db_disconnect(conn)
          
    
