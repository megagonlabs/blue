###### Parsers, Formats, Utils
import json

###### Source specific libs
from pymongo import MongoClient


###### Blue
from blue.data.source import DataSource
from blue.data.schema import DataSchema


###############
### MongoDBSource
#
class MongoDBSource(DataSource):
    def __init__(self, name, properties={}):
        super().__init__(name, properties=properties)
        

    ###### initialization
    def _initialize_properties(self):
        super()._initialize_properties()

        # source protocol 
        self.properties['protocol'] = "mongodb"

    ###### connection
    def _connect(self, **connection):
        host = connection['host']
        port = connection['port']
        
        connection_url = self.properties['protocol'] + "://" + host + ":" + str(port)    
        return MongoClient(connection_url)

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
        dbs = self.connection.list_database_names()
        return dbs

    def fetch_database_metadata(self, database):
        return {}

    def fetch_database_schema(self, database):
        return {}



    ######### database/collection
    def fetch_database_collections(self, database):
        collections = self.connection[database].list_collection_names()
        return collections

    def fetch_database_collection_metadata(self, database, collection):
        return {}

    def fetch_database_collection_schema(self, database, collection):
        coll = self.connection[database][collection]
        sample = coll.find_one()

        schema = self.extract_schema(sample)
        return schema.to_json()

    def extract_schema(self, sample, schema=None, source=None):
        if schema is None:
            schema = DataSchema()

        if source == None:
            source = schema.add_entity("ROOT")

        if type(sample) == dict:
            for key in sample:
                value = sample[key]
                if type(value) == list:
                    target = schema.add_entity(key)
                    # (1)-->(M)
                    schema.add_relation(source, source + ":" + target, target)
                    if len(value) > 0:
                        self.extract_schema(value[0], schema=schema, source=target)
                elif type(value) == dict:
                    target = schema.add_entity(key)
                    # (1)-->(1)
                    schema.add_relation(source, source + ":" + target, target)
                    self.extract_schema(value, schema=schema, source=target)
                else:
                    schema.add_entity_property(source, key, value.__class__.__name__)
                
        return schema


    ######### execute query
    def execute_query(self, query, database=None, collection=None):
        if database is None:
            raise Exception("No database provided")
        
        if collection is None:
            raise Exception("No collection provided")

        db = self.connection[database]
        col = db[collection]

        q = json.loads(query)
        result = col.find(q)

        # Convert cursor to a list of dictionaries and handle ObjectId safely
        result_list = []
        for doc in result:
            if '_id' in doc:  # Check if '_id' exists
                doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
            result_list.append(doc)

        return result_list
    