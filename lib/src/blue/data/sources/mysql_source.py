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
        """
        Fetch high-level metadata for the MySQL source connection.

        Currently a placeholder method.
        Returns:
            dict: Currently returns an empty dictionary.
        """
        return {}

    def fetch_schema(self):
        """
        Retrieve global schema metadata for the MySQL source.

        Returns:
            dict: Currently returns an empty dictionary.
        """
        return {}

    ######### database
    def fetch_databases(self):
        """
        Retrieve a list of available MySQL databases, excluding system schemas.

        Executes `SHOW DATABASES` and filters out MySQL system databases like
        `information_schema`, `performance_schema`, `sys`, and `mysql`.

        Returns:
            list[str]: List of user-defined databases.
        """
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
        """
        Fetch high-level metadata for a specific MySQL database.

        Parameters:
            database (str): Name of the database.

        Returns:
            dict: currently empty.
        """
        return {}

    def fetch_database_schema(self, database):
        """
        Retrieve schema definition for a MySQL database.

        Parameters:
            database (str): Name of the database.

        Returns:
            dict: Schema definition, currently empty.
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
        Return a default 'public' collection for MySQL databases.

        Since MySQL does not use named schemas (collections) like PostgreSQL,
        this method returns a single collection called 'public' for registry consistency.

        Parameters:
            database (str): Name of the database.

        Returns:
            list[str]: Always returns ['public'].
        """
        ## for mysql, there is no collection. We return "public" to create data registry entry
        collections = []
        collections.append("public")
        return collections

    def fetch_database_collection_metadata(self, database, collection):
        """
        Placeholder for future collection-level metadata extraction in MySQL.

        Parameters:
            database (str): Name of the database.
            collection (str): The placeholder collection name ("public").

        Returns:
            dict: Currently empty.
        """
        return {}

    def fetch_database_collection_entities(self, database, collection):
        """
        Extract entity (table) and property (column) metadata from a MySQL database.

        Queries `information_schema.columns` to gather table and column structure,
        including enumeration values for `ENUM` data types.

        Parameters:
            database (str): Name of the database.
            collection (str): Collection name (always 'public' for MySQL).

        Returns:
            dict: Mapping of entities (tables) to their properties and types.
        """
        # connect to specific database (not source directly)
        db_connection = self._db_connect(database)

        # TODO: Do better ER extraction from tables, columns, exploiting column semantics, foreign keys, etc.

        query = "SELECT table_name, column_name, data_type, column_type " "FROM information_schema.columns " "WHERE table_schema = '{}'".format(database)

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
        """
        Placeholder for relationship extraction between MySQL tables.

        Parameters:
            database (str): Database name.
            collection (str): Collection name (always 'public').

        Returns:
            dict: Currently empty.
        """
        return {}

    ######### execute query
    def execute_query(self, query, database=None, collection=None, optional_properties={}):
        """
        Execute a SQL query on a MySQL database and return the result as JSON.

        Parameters:
            query (str): SQL query to execute.
            database (str, optional): Name of the database to execute against.
            collection (str, optional): Placeholder argument for consistency.
            optional_properties (dict, optional): Optional flags such as commit.

        Returns:
            list[dict]: Query results as a list of JSON-compatible dictionaries.
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
        Collect high-level metadata about the MySQL source connection.

        Executes a simple query (e.g., `SELECT version()`) to verify connectivity
        and retrieve basic version information.

        Returns:
            dict: A dictionary containing source-level statistics such as version
            or error details if collection fails.
        """

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
        """
        Collect size-related statistics for a given MySQL database.

        Computes the total size (data + index) of all tables in the specified schema
        using the `information_schema.tables` system view.

        Parameters:
            database (str): Name of the database (schema) to inspect.

        Returns:
            dict: A JSON-safe dictionary containing database-level statistics such
            as total size in bytes.
        """

        conn = self._db_connect(database)
        cur = conn.cursor()

        stats = {}

        try:
            # Size of database in bytes (summing all tables)
            cur.execute(
                """
                SELECT IFNULL(SUM(data_length + index_length), 0) AS size_bytes
                FROM information_schema.tables
                WHERE table_schema = %s;
            """,
                (database,),
            )
            size = cur.fetchone()
            stats["size_bytes"] = size[0] if size else None

        except Exception as e:
            logging.warning(f"Error fetching database stats for {database}: {e}")
        finally:
            cur.close()

        return json_utils.json_safe(stats)

    def fetch_collection_stats(self, database, collection_name, entities, relations):
        """
        Collect basic statistics for a database collection (schema grouping).

        Computes counts of entities (tables) and relations within the given
        collection for reporting or registry enrichment.

        Parameters:
            database (str): Name of the database the collection belongs to.
            collection_name (str): Name of the collection.
            entities (list): List of entity definitions (e.g., tables).
            relations (list): List of relationships between entities.

        Returns:
            dict: Dictionary containing counts of entities and relations.
        """

        stats = {}
        num_entities = len(entities)
        num_relations = len(relations)

        stats["num_entities"] = num_entities
        stats["num_relations"] = num_relations

        return stats

    def fetch_entity_stats(self, database, collection, entity):
        """
        Collect basic statistics for a single entity (table) in a MySQL database.

        Executes a `COUNT(*)` query to determine the total number of rows.
        The `collection` argument is ignored for MySQL sources.

        Parameters:
            database (str): Name of the database (schema) containing the entity.
            collection (str): Unused for MySQL but included for interface consistency.
            entity (str): Name of the table to analyze.

        Returns:
            dict: A JSON-safe dictionary containing entity-level stats, such as
            row count.
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
        """
        Fetch basic statistics for a specific column (property) in a MySQL table.

        This method queries `INFORMATION_SCHEMA.COLUMNS` and the target table to
        compute statistics such as counts, distinct values, nulls, sample values,
        min/max (for numeric/date types), and most common values.

        Parameters:
            database (str): Name of the database to connect to.
            collection (str): Schema name in MySQL (equivalent to database namespace).
            table (str): The table name containing the property.
            property_name (str): The column (property) name to analyze.
            sample_limit (int, optional): Maximum number of sample non-null values
                to retrieve. Defaults to 10.

        Returns:
            dict: A dictionary containing the following statistics:
                - count (int): Number of non-null values in the column.
                - distinct_count (int): Number of distinct non-null values.
                - null_count (int): Number of null values.
                - sample_values (list): Up to `sample_limit` example non-null values.
                - min (Any or None): Minimum value (if supported by the column type).
                - max (Any or None): Maximum value (if supported by the column type).
                - most_common_vals (list): Up to 5 most frequent values.

        Notes:
            - Min/max are computed only for numeric, date, timestamp, boolean, and enum types.
            - "Most common values" are computed by grouping and counting occurrences,
            since MySQL does not expose statistics like PostgreSQL's `pg_stats`.
            - Returns an empty dict if the query fails.
        """

        conn = self._db_connect(database)
        cursor = conn.cursor()

        schema = collection

        column = f"`{property_name}`"

        try:
            # 1. Get column data type
            cursor.execute(
                """
                SELECT DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s;
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
            cursor.execute(
                f"""
                SELECT {column}
                FROM `{schema}`.`{table}`
                WHERE {column} IS NOT NULL
                LIMIT {sample_limit};
            """
            )

            stats["sample_values"] = [r[0] for r in cursor.fetchall()]

            # 4. Min/Max if numeric/date type
            if include_min_max:
                cursor.execute(
                    f"""
                    SELECT MIN({column}), MAX({column})
                    FROM `{schema}`.`{table}`;
                """
                )
                min_max = cursor.fetchone()
                stats["min"] = min_max[0]
                stats["max"] = min_max[1]
            else:
                stats["min"] = None
                stats["max"] = None

            # 5. MySQL does not have pg_stats, but we can approximate "most common values"
            cursor.execute(
                f"""
                SELECT {column}, COUNT(*) AS freq
                FROM `{schema}`.`{table}`
                WHERE {column} IS NOT NULL
                GROUP BY {column}
                ORDER BY freq DESC
                LIMIT 5;
            """
            )
            stats["most_common_vals"] = [r[0] for r in cursor.fetchall()]

            return json_utils.json_safe(stats)

        except Exception as e:
            logging.warning(f"Failed to fetch property stats for {collection}.{table}.{property_name}: {str(e)}")
            return {}
        finally:
            self._db_disconnect(conn)
