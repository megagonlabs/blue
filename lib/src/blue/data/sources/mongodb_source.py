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
        self._schema_cache = {}

    ###### connection
    def _initialize_connection_properties(self):
        super()._initialize_connection_properties()

        # set host, port, protocol
        self.properties['connection']['host'] = 'localhost'
        self.properties['connection']['port'] = 27017
        self.properties['connection']['protocol'] = 'mongodb'

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
        """
        Fetch metadata for the MongoDB source.

        Returns:
            dict: General metadata about the MongoDB source.
                Currently returns an empty dictionary.
        """
        return {}

    def fetch_schema(self):
        """
        Fetch schema for the MongoDB source.

        Returns:
            dict: Schema information for the entire MongoDB source.
                Currently returns an empty dictionary.
        """
        return {}

    ######### database
    def fetch_databases(self):
        """
        List all databases in the MongoDB source.

        Returns:
            list[str]: Names of all available databases.
        """
        dbs = self.connection.list_database_names()
        return dbs

    def fetch_database_metadata(self, database):
        """
        Fetch metadata for a specific database.

        Parameters:
            database (str): Database name.

        Returns:
            dict: Database-level metadata (default empty).
        """
        return {}

    def fetch_database_schema(self, database):
        """
        Fetch schema information for a specific database.

        Parameters:
            database (str): Database name.

        Returns:
            dict: Schema definition for all collections in the database.
                Currently returns an empty dictionary.
        """
        return {}

    ######### database/collection
    def fetch_database_collections(self, database):
        """
        List all collections within a database.

        Parameters:
            database (str): Database name.

        Returns:
            list[str]: Names of collections.
        """
        collections = self.connection[database].list_collection_names()
        return collections

    def fetch_database_collection_metadata(self, database, collection):
        """
        Fetch metadata for a specific collection within a database.

        Parameters:
            database (str): Name of the database.
            collection (str): Name of the collection.

        Returns:
            dict: Metadata for the collection (default empty).
        """
        return {}

    def _get_collection_schema(self, database, collection):
        """
        Internal helper: return cached schema object for a collection.
        """
        cache_key = (database, collection)
        if cache_key in self._schema_cache:
            return self._schema_cache[cache_key]

        coll = self.connection[database][collection]
        sample = coll.find_one()

        schema = self.extract_schema(sample)

        self._schema_cache[cache_key] = schema
        return schema

    def fetch_database_collection_entities(self, database, collection):
        """
        Fetch entities (document structures) for a collection.

        Parameters:
            database (str): Database name.
            collection (str): Collection name.

        Returns:
            list[str]: Entity names in the collection schema.
        """
        schema = self._get_collection_schema(database, collection)
        return schema.get_entities()

    def fetch_database_collection_relations(self, database, collection):
        """
        Fetch relations (document nesting relationships) for a collection.

        Parameters:
            database (str): Database name.
            collection (str): Collection name.

        Returns:
            list[str]: Relations between entities.
        """
        schema = self._get_collection_schema(database, collection)
        return schema.get_relations()

    def extract_schema(self, sample, schema=None, source=None):
        """
        Recursively infer schema structure from a sample MongoDB document.

        Parameters:
            sample (dict): Sample document for inference.
            schema (DataSchema, optional): Existing schema object to update.
            source (str, optional): Current entity source node.

        Returns:
            DataSchema: Inferred or updated schema object.
        """
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
    def execute_query(self, query, database=None, collection=None, optional_properties={}):
        """
        Execute a MongoDB query on a specific collection.

        Parameters:
            query (str): JSON-formatted MongoDB query string.
            database (str, optional): Target database name.
            collection (str, optional): Target collection name.
            optional_properties (dict, optional): Extra query parameters.

        Returns:
            list[dict]: List of documents matching the query, with `_id` as string.

        Raises:
            Exception: If `database` or `collection` is not provided.
        """
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
