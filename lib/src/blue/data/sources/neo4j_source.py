###### Source specific libs
from blue.utils import neo4j_connection

###### Blue
from blue.data.source import DataSource
from blue.data.schema import DataSchema

APOC_META_NODE_PROPERTIES_QUERY = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE NOT type = "RELATIONSHIP" AND elementType = "node"
WITH label AS label, apoc.coll.sortMaps(collect({property:property, type:type}), 'property') AS properties
RETURN label, properties ORDER BY label
""".strip()

APOC_META_REL_QUERY = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE type = "RELATIONSHIP" AND elementType = "node"
UNWIND other AS other_node
RETURN label as start, property as type, other_node as end ORDER BY type, start, end
""".strip()

APOC_META_REL_PROPERTIES_QUERY = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE NOT type = "RELATIONSHIP" AND elementType = "relationship"
RETURN label AS type, apoc.coll.sortMaps(collect({property:property, type:type}), 'property') AS properties ORDER BY type
""".strip()


###############
### NEO4JSource
#
class NEO4JSource(DataSource):
    def __init__(self, name, properties={}):
        super().__init__(name, properties=properties)
        self._schema_cache = {}

    ###### connection
    def _initialize_connection_properties(self):
        super()._initialize_connection_properties()

        # set host, port, protocol
        self.properties['connection']['host'] = 'localhost'
        self.properties['connection']['port'] = 7687
        self.properties['connection']['protocol'] = 'bolt'

    def _connect(self, **connection):
        host = connection['host']
        port = connection['port']

        user = connection['user']
        pwd = connection['password']

        connection_url = "bolt://" + host + ":" + str(port)

        return neo4j_connection.NEO4J_Connection(connection_url, user, pwd)

    def _disconnect(self):
        # TODO:
        return None

    ######### source
    def fetch_metadata(self):
        """
        Fetch high-level metadata for the Neo4j source.

        Returns:
            dict: Metadata about the source.
            Default implementation returns empty dict.
        """
        return {}

    def fetch_schema(self):
        """
        Fetch the global schema definition from the Neo4j source.

        Returns:
            dict: Schema information including nodes and relationships.
            Default implementation returns empty dict.
        """
        return {}

    ######### database
    def fetch_databases(self):
        """
        Retrieve the list of available databases from the source.

        Returns:
            list[str]: Names of all databases.
        """
        dbs = []
        result = self.connection.run_query("SHOW DATABASES;")

        for record in result:
            dbs.append(record["name"])
        return dbs

    def fetch_database_metadata(self, database):
        """
        Fetch metadata for a specific database.

        Parameters:
            database (str): Name of the database.

        Returns:
            dict: Metadata for the database (default empty).
        """
        return {}

    def fetch_database_schema(self, database):
        """
        Fetch the schema for a specific Neo4j database, including node labels
        and relationship types.

        Parameters:
            database (str): Name of the database.

        Returns:
            dict: Schema information including nodes and relationships.
            Default implementation returns empty dict.
        """
        return {}

    ######### database/collection
    def fetch_database_collections(self, database):
        """
        Retrieve the collections (databases or logical groupings) for a Neo4j database.

        In Neo4j, each database is treated as a single collection.

        Parameters:
            database (str): Name of the database.

        Returns:
            list[str]: List containing the database name as the collection.
        """
        collections = [database]
        return collections

    def fetch_database_collection_metadata(self, database, collection):
        """
        Fetch metadata for a specific collection (database) in Neo4j.

        Parameters:
            database (str): Name of the database.
            collection (str): Name of the collection (usually same as database).

        Returns:
            dict: Metadata for the collection. Default implementation returns empty dict.
        """
        return {}

    def extract_schema(self, nodes_result, relationships_result, rel_properties_result):
        """
        Build a DataSchema object from query results describing nodes, relationships, and relationship properties.

        Parameters:
            nodes_result (list[dict]): List of node definitions with labels and properties.
            relationships_result (list[dict]): List of relationship definitions.
            rel_properties_result (list[dict]): List of relationship property definitions.

        Returns:
            DataSchema: A schema object representing entities and relations.
        """
        schema = DataSchema()

        for node in nodes_result:
            schema.add_entity(node['label'])
            for prop in node['properties']:
                schema.add_entity_property(node['label'], prop['property'], prop['type'])

        rlabel2properties = {r['type']: r['properties'] for r in rel_properties_result}

        for relation in relationships_result:
            key = schema.add_relation(relation['start'], relation['type'], relation['end'])
            for prop in rlabel2properties.get(relation['type'], []):
                schema.add_relation_property(key, prop['property'], prop['type'])

        return schema

    def fetch_database_collection_entities(self, database, collection):
        """
        Fetch all entities (nodes) in a specific Neo4j database collection.

        This method retrieves the database schema and extracts the entities
        (node labels) present in the specified collection.

        Parameters:
            database (str): Name of the database.
            collection (str): Name of the collection (usually same as database).

        Returns:
            list[dict]: A list of entity definitions, each representing a node
            with its properties in the Neo4j database.
        """
        schema = self._fetch_and_extract_schema(database, collection)
        return schema.get_entities()

    def fetch_database_collection_relations(self, database, collection):
        """
        Fetch all relationships (edges) in a specific Neo4j database collection.

        This method retrieves the database schema and extracts the relationships
        between entities present in the specified collection.

        Parameters:
            database (str): Name of the database.
            collection (str): Name of the collection (usually same as database).

        Returns:
            list[dict]: A list of relationship definitions, each representing
            a relationship type along with its source and target nodes.
        """
        schema = self._fetch_and_extract_schema(database, collection)
        return schema.get_relations()

    # Internal helper with lightweight caching per (database, collection)
    def _fetch_and_extract_schema(self, database, collection):
        # Use cache key to avoid duplicate work in the same request cycle
        cache_key = (database, collection)

        if cache_key not in self._schema_cache:
            nodes_result = self.connection.run_query(APOC_META_NODE_PROPERTIES_QUERY)
            relationships_result = self.connection.run_query(APOC_META_REL_QUERY)
            rel_properties_result = self.connection.run_query(APOC_META_REL_PROPERTIES_QUERY)

            schema = self.extract_schema(nodes_result, relationships_result, rel_properties_result)
            self._schema_cache[cache_key] = schema

        return self._schema_cache[cache_key]

    ######### execute query
    def execute_query(self, query, database=None, collection=None):
        """
        Execute a Cypher query against the Neo4j database.

        This method sends the provided Cypher query to the connected Neo4j
        instance and returns the results. It does not limit execution to a
        single transaction or single record.

        Parameters:
            query (str): The Cypher query string to execute.
            database (str, optional): Name of the database to target. Defaults to None.
            collection (str, optional): Name of the collection/schema. Defaults to None.

        Returns:
            list[dict]: A list of dictionaries representing query results,
            where each dictionary corresponds to a record returned by the query.
        """
        result = self.connection.run_query(query, single=False, single_transaction=False)
        return result
