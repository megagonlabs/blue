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

    ###### connection
    def _initialize_connection_properties(self):
        super()._initialize_connection_properties()

        # set host, port, protocol
        self.properties['connection']['host'] = 'localhost'
        self.properties['connection']['port'] = 5432
        self.properties['connection']['protocol'] = 'postgres'

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
        """
        Fetch source-level metadata for the PostgreSQL server.

        Returns:
            dict: Currently returns an empty dictionary. Can be extended to include server info, version, etc.
        """
        return {}

    def fetch_schema(self):
        """
        Fetch global schema metadata for the PostgreSQL source.

        Returns:
            dict: Currently returns an empty dictionary. Can be extended to include schema definitions.
        """
        return {}

    ######### database
    def fetch_databases(self):
        """
        Retrieve a list of available databases from the PostgreSQL server.

        This method queries the system catalog `pg_database` to list all databases
        on the connected PostgreSQL instance, excluding template databases such as
        `template0` and `template1`.

        Returns:
            list[str]:
                A list of database names available on the server.

        """
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
        """
        Fetch high-level metadata for a specific PostgreSQL database.

        Parameters:
            database (str):
                The name of the database for which to fetch metadata.

        Returns:
            dict:
                Currently returns an empty dictionary.
        """
        return {}

    def fetch_database_schema(self, database):
        """
        Fetch schema definitions for a specific PostgreSQL database.

        Parameters:
            database (str): Database name.

        Returns:
            dict: Currently returns an empty dictionary. Can be extended to return table and column definitions.
        """
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
        """
        Retrieve a list of collections (schemas) within a PostgreSQL database.

        This method connects to a specific database and queries the
        `information_schema.tables` system catalog to find all distinct schemas
        that contain tables, excluding system schemas such as
        `'pg_catalog'` and `'information_schema'`.

        Parameters:
            database (str):
                The name of the database to inspect.

        Returns:
            list[str]:
                A list of schema (collection) names within the specified database.
        """
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
        """
        Fetch metadata for a specific schema (collection) in a PostgreSQL database.

        Parameters:
            database (str):
                Name of the database to connect to.
            collection (str):
                Name of the schema (collection) whose metadata should be retrieved.

        Returns:
            dict:
                Currently returns an empty dictionary.
        """
        return {}

    def fetch_enum_types(self, db_connection):
        """
        Fetch all PostgreSQL ENUM types and their possible values.

        This method queries the system catalog tables (`pg_type`, `pg_enum`,
        and `pg_namespace`) to collect all user-defined ENUM types and
        their corresponding labels (values). It excludes system schemas
        such as `pg_catalog` and `information_schema`.

        Parameters:
            db_connection:
                A live PostgreSQL database connection object (e.g., from psycopg2).

        Returns:
            dict[str, list[str]]:
                A mapping of enum type names (qualified by schema) to their list of values.
        """

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

    def fetch_database_collection_entities(self, database, collection, max_distinct=50, max_ratio=0.1, max_length=100):
        """
        Collect entity (table) and property (column) metadata for a given schema in a PostgreSQL database.

        This method retrieves table and column definitions from the `information_schema.columns`
        view for a specific schema (`collection`). It identifies ENUM-backed columns, gathers
        column-level statistics (distinct counts, average text lengths), and optionally collects
        representative sample values for categorical string columns.

        The method is designed to populate a `DataSchema` object that models entities and their
        properties, useful for metadata inspection, schema inference, or automated documentation.

        Parameters:
            database (str):
                The logical name or connection identifier for the target PostgreSQL database.
            collection (str):
                The schema name within the database to inspect (e.g., "public").
            max_distinct (int, optional):
                The maximum number of distinct values to allow for a text column before
                it is considered non-categorical. Defaults to 50.
            max_ratio (float, optional):
                The maximum allowed ratio of distinct values to total rows for a column to
                be considered categorical. Defaults to 0.1.
            max_length (int, optional):
                The maximum average string length allowed for categorical columns. Defaults to 100.

        Returns:
            dict:
                A dictionary representation of entities (tables) and their properties (columns),
                as produced by `DataSchema.get_entities()`.

        Raises:
            psycopg2.Error:
                If any SQL execution or database interaction fails.

        """
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

            property_def = {"type": data_type}

            if enum_types and udt_name in enum_types:
                property_def["enum"] = enum_types[udt_name]

            if data_type.lower() in ("character varying", "varchar", "character", "text", "name"):

                cursor.execute(
                    f"""
                  SELECT COUNT(DISTINCT "{column_name}"), COUNT(*) 
                  FROM "{collection}"."{table_name}"
                  WHERE "{column_name}" IS NOT NULL
                 """
                )

                distinct_count, total_count = cursor.fetchone()

                cursor.execute(
                    f'''
                    SELECT AVG(LENGTH("{column_name}"))
                    FROM "{collection}"."{table_name}"
                    WHERE "{column_name}" IS NOT NULL
                '''
                )
                avg_length = cursor.fetchone()[0] or 0

                if distinct_count <= max_distinct and (total_count == 0 or distinct_count / total_count <= max_ratio) and avg_length <= max_length:
                    cursor.execute(
                        f"""
                        SELECT DISTINCT "{column_name}"
                        FROM "{collection}"."{table_name}"
                        WHERE "{column_name}" IS NOT NULL
                        LIMIT {max_distinct};
                    """
                    )
                    values = [row[0] for row in cursor.fetchall()]
                    property_def["values"] = values

            schema.add_entity_property(table_name, column_name, property_def)

        self._db_disconnect(db_connection)
        return schema.get_entities()

    ### TODO
    def fetch_database_collection_relations(self, database, collection):
        """
        Retrieve relationships (foreign key constraints) between tables in a given schema.

        Currently a placeholder method. Intended to extract relational metadata
        such as foreign key relationships, joins, and dependencies between tables
        in the specified database and schema/collection.

        Parameters:
            database (str): The database name to inspect.
            collection (str): The schema name within the database.

        Returns:
            dict: A dictionary representing table relationships.
                Currently returns an empty dictionary.
        """
        return {}

    ######### execute query
    def execute_query(self, query, database=None, collection=None, optional_properties={}):
        """
        Execute a SQL query on a specific PostgreSQL database and return results as JSON.

        This method connects to the specified database, executes the provided
        SQL query, fetches all results, converts them to a pandas DataFrame,
        and finally serializes the DataFrame into a JSON array.

        Parameters:
            query (str): The SQL query string to execute.
            database (str): Name of the database to connect to.
            collection (str, optional): Not used for PostgreSQL, kept for interface consistency.
            optional_properties (dict, optional): Additional options. Supported keys:
                - 'commit' (bool): If True, commits the transaction after execution.

        Raises:
            Exception: If `database` is not provided.

        Returns:
            list[dict]: Query results serialized as a list of dictionaries (JSON objects),
                        where each dictionary corresponds to a row in the query result.
        """
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
        """
        Collect high-level statistics about the PostgreSQL source connection.

        Retrieves general metadata such as:
        - PostgreSQL version
        - Number of non-template databases
        - Server uptime since postmaster start

        Returns:
            dict: Dictionary containing source-level statistics like version,
            database count, uptime, or an error message if collection fails.
        """

        stats = {}

        try:
            with self.connection.cursor() as cur:
                cur.execute("SELECT version()")
                stats["version"] = cur.fetchone()[0]

                # Get list of databases
                cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
                databases = [row[0] for row in cur.fetchall()]
                stats["database_count"] = len(databases)

                cur.execute(
                    """
                    SELECT now() - pg_postmaster_start_time() AS uptime;
                """
                )
                stats["uptime"] = str(cur.fetchone()[0])

        except Exception as e:
            logging.warning(f"Failed to collect source-level stats: {e}")
            stats["error"] = str(e)

        return stats

    def fetch_database_stats(self, database):
        """
        Collect size and table-level statistics for a specific PostgreSQL database.

        Connects to the given database to retrieve:
        - Total database size in bytes
        - Total number of user tables (excluding system schemas)

        Parameters:
            database (str): Name of the database to analyze.

        Returns:
            dict: Dictionary containing database-level stats such as size (bytes)
            and table count.
        """

        conn = self._db_connect(database)
        cur = conn.cursor()

        stats = {}
        try:
            # Size of database in bytes
            cur.execute("SELECT pg_database_size(%s);", (database,))
            size = cur.fetchone()
            stats["size_bytes"] = size[0] if size else None

            cur.execute(
                """
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema') 
            AND table_type = 'BASE TABLE';
            """
            )

            stats["table_count"] = cur.fetchone()[0]

        except Exception as e:
            logging.warning(f"Error fetching database stats for {database}: {e}")
        finally:
            cur.close()

        return stats

    def fetch_collection_stats(self, database, collection_name, entities, relations):
        """
        Collect summary statistics for a collection within a PostgreSQL database.

        Computes basic counts of entities (tables) and relations to provide
        high-level structural metadata for the data registry.

        Parameters:
            database (str): Name of the database the collection belongs to.
            collection_name (str): Name of the collection or schema.
            entities (list): List of entities (tables) in the collection.
            relations (list): List of relationships among entities.

        Returns:
            dict: Dictionary with counts of entities and relations.
        """

        stats = {}
        num_entities = len(entities)
        num_relations = len(relations)

        stats["num_entities"] = num_entities
        stats["num_relations"] = num_relations

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
        """
        Fetch statistics for a specific column (property) in a PostgreSQL table.

        This method queries both `information_schema.columns` and `pg_stats` to
        gather metadata about the column, including counts, distinct values,
        nulls, sample values, min/max values (when applicable), and most common values.

        Parameters:
            database (str): The database name to connect to.
            collection (str): The schema name (PostgreSQL schema) of the table.
            table (str): The table name containing the property.
            property_name (str): The column name (property) to analyze.
            sample_limit (int, optional): Maximum number of distinct sample values
                to return. Defaults to 10.

        Returns:
            dict: A dictionary containing the following keys:
                - count (int): Number of non-null values in the column.
                - distinct_count (int): Number of distinct non-null values.
                - null_count (int): Number of null values.
                - sample_values (list of str): Up to `sample_limit` distinct sample values.
                - min (str or None): Minimum value (if column type supports it), else None.
                - max (str or None): Maximum value (if column type supports it), else None.
                - most_common_vals (list): List of most common values from `pg_stats`.

        Notes:
            - Min/max values are only computed for numeric, date, timestamp,
            boolean, and enum-like column types.
            - If an error occurs (e.g., invalid table or column), an empty dict is returned.
        """

        conn = self._db_connect(database)
        cursor = conn.cursor()

        schema = collection

        column = f'"{property_name}"'

        try:
            cursor.execute(
                """
                SELECT data_type
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s AND column_name = %s;
            """,
                (schema, table, property_name),
            )
            type_result = cursor.fetchone()
            column_type = type_result[0] if type_result else None

            # Set flags for whether to compute min/max
            include_min_max = column_type in (
                'integer',
                'bigint',
                'smallint',
                'numeric',
                'real',
                'double precision',
                'date',
                'timestamp without time zone',
                'timestamp with time zone',
                'boolean',
                'enum',
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
            cursor.execute(
                """
                SELECT most_common_vals
                FROM pg_stats
                WHERE schemaname = %s AND tablename = %s AND attname = %s;
            """,
                (schema, table, property_name),
            )

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
