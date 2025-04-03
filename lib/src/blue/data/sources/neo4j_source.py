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

    ###### initialization
    def _initialize_properties(self):
        super()._initialize_properties()

        # source protocol 
        self.properties['protocol'] = "bolt"

    ###### connection
    def _connect(self, **connection):
        host = connection['host']
        port = connection['port']

        user = connection['user']
        pwd = connection['password']
        connection_url = self.properties['protocol'] + "://" + host + ":" + str(port)

        return neo4j_connection.NEO4J_Connection(connection_url, user, pwd)

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
        dbs = []
        result = self.connection.run_query("SHOW DATABASES;")

        for record in result:
            dbs.append(record["name"])
        return dbs

    def fetch_database_metadata(self, database):
        return {}

    def fetch_database_schema(self, database):
        return {}

    ######### database/collection
    def fetch_database_collections(self, database):
        collections = [database]
        return collections

    def fetch_database_collection_metadata(self, database, collection):
        return {}

    def fetch_database_collection_schema(self, database, collection):
        nodes_result = self.connection.run_query(APOC_META_NODE_PROPERTIES_QUERY)
        relationships_result = self.connection.run_query(APOC_META_REL_QUERY)
        rel_properties_result = self.connection.run_query(APOC_META_REL_PROPERTIES_QUERY)

        schema = self.extract_schema(nodes_result, relationships_result, rel_properties_result)
        return schema.to_json()

    def extract_schema(self, nodes_result, relationships_result, rel_properties_result):
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

    ######### execute query
    def execute_query(self, query, database=None, collection=None):
        result = self.connection.run_query(query, single=False, single_transaction=False)
        return result
