###### Parsers, Formats, Utils
import pandas as pd
import numpy as np
import json
import copy
import logging


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
        
        return enum_types

        
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

            if enum_types and udt_name in enum_types:
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

    ######### stats

    def fetch_source_stats(self):
            
        stats = {}

        try:
            with self.connection.cursor() as cur:
                cur.execute("SELECT version()")
                stats["version"] = cur.fetchone()[0]

                # Get list of databases
                cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
                databases = [row[0] for row in cur.fetchall()]
                stats["database_count"] = len(databases)
                stats["database_names"] = databases
                
                cur.execute("""
                    SELECT now() - pg_postmaster_start_time() AS uptime;
                """)
                stats["uptime"] = str(cur.fetchone()[0])

        except Exception as e:
            logging.warning(f"Failed to collect source-level stats: {e}")
            stats["error"] = str(e)

        return stats

    def fetch_database_stats(self, database):
            
        conn = self._db_connect(database)
        cur = conn.cursor()
        
        stats = {}
        try:
            # Size of database in bytes
            cur.execute("SELECT pg_database_size(%s);", (database,))
            size = cur.fetchone()
            stats["size_bytes"] = size[0] if size else None

            cur.execute("""
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema');
            """)

            rows = cur.fetchall()

            # Save both schema and table in stats
            stats['tables'] = [
                {'schema': schema, 'table': table}
                for schema, table in rows
            ]

            cur.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema') 
            AND table_type = 'BASE TABLE';
            """)
            
            stats["table_count"] = cur.fetchone()[0]
            
        except Exception as e:
            logging.warning(f"Error fetching database stats for {database}: {e}")
        finally:
            cur.close()

        return stats

    def fetch_collection_stats(self, database, collection_name, schema_json=None, sample_limit=10):
            
        if isinstance(schema_json, str):
            schema_json = json.loads(schema_json)

        stats = {}
        
        for entity, meta in schema_json.get("entities", {}).items():
        
            ent_stats = {}
            ent_stats["stats"] = self.fetch_entity_stats(database, collection_name, entity)

            props = meta.get("properties", {})
            
            ent_stats["properties"] = {}
            for prop in props:
                ent_stats["properties"][prop] = self.fetch_property_stats(database, collection_name, entity, prop, sample_limit=sample_limit)

            stats[entity] = ent_stats

        return stats


    def fetch_entity_stats(self, database, collection, entity):
        
        conn = self._db_connect(database)
        cursor = conn.cursor()

        stats = {}

        try:
            query = f'SELECT COUNT(*) FROM "{collection}"."{entity}";'
            cursor.execute(query)
            stats["row_count"] = cursor.fetchone()[0]

        except psycopg2.Error as e:
            logging.warning(f"Failed to get row count for {collection}.{entity}: {e}")
            stats["row_count"] = None

        finally:
            self._db_disconnect(conn)

        return stats

    def fetch_property_stats(self, database, collection, table, property_name, sample_limit=10):
    
        conn = self._db_connect(database)
        cursor = conn.cursor()

        schema = collection 
  
        column = f'"{property_name}"'  
        
        try:
            cursor.execute("""
                SELECT data_type
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s AND column_name = %s;
            """, (schema, table, property_name))
            type_result = cursor.fetchone()
            column_type = type_result[0] if type_result else None

            # Set flags for whether to compute min/max
            include_min_max = column_type in (
            'integer', 'bigint', 'smallint', 'numeric', 'real', 'double precision',
            'date', 'timestamp without time zone', 'timestamp with time zone',
            'boolean', 'enum'
            )

            # Build query dynamically
            query = f"""
                SELECT
                COUNT({column}) AS non_null_count,
                COUNT(DISTINCT {column}) AS distinct_count,
                COUNT(*) FILTER (WHERE {column} IS NULL) AS null_count,
                ARRAY(
                    SELECT DISTINCT {column}
                    FROM {table}
                    WHERE {column} IS NOT NULL
                    LIMIT {sample_limit}
                )::text[] AS sample_values
            """

            if include_min_max:
                query += f""",
                    MIN({column})::text AS min_value,
                    MAX({column})::text AS max_value
                """
            else:
                query += ", NULL AS min_value, NULL AS max_value"

            query += f" FROM {table};"

            cursor.execute(query)
            row = cursor.fetchone()
            
            stats = {
                "count": row[0],
                "distinct_count": row[1],
                "null_count": row[2],
                "sample_values": row[3],
                "min": row[4],
                "max": row[5],
            }

            # Additional query for most_common_vals from pg_stats
            cursor.execute("""
                SELECT most_common_vals
                FROM pg_stats
                WHERE schemaname = %s AND tablename = %s AND attname = %s;
            """, (schema, table, property_name))

            mc_row = cursor.fetchone()
            
            if mc_row and mc_row[0]:
                stats["most_common_vals"] = mc_row[0]
            else:
                stats["most_common_vals"] = []
                
            return stats

        except Exception as e:
            logging.warning(f"Failed to fetch property stats for {collection}.{table}.{property_name}: {str(e)}")
            return {}
        finally:
            self._db_disconnect(conn)
         