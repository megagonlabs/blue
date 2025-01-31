###### Source specific libs
from blue.utils import neo4j_connection

###### Blue
from blue.data.source import DataSource
from blue.data.schema import DataSchema



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
        
        result = self.connection.run_query("CALL db.schema.visualization",single=True, single_transaction=False)

        schema = self.extract_schema(result[0])
        return schema.to_json()

    def extract_schema(self, result):
        schema = DataSchema()

        nodes = result['nodes']
        relationships = result['relationships']

        for node in nodes:
            schema.add_entity(node['type'])

        for relation in relationships:
            schema.add_relation(relation['from']['type'],relation['type'],relation['to']['type'])
        return schema

    ######### execute query
    def execute_query(self, query, database=None, collection=None):
        result = self.connection.run_query(query, single=False, single_transaction=False)
        return result
