import os

###### Parsers, Formats, Utils
import logging
import copy
import json

###### Backend, Databases
from redis.commands.json.path import Path
from redis.commands.search.field import TextField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

#######
import numpy as np

###### Blue
from blue.connection import PooledConnectionFactory
from blue.utils import json_utils, uuid_utils, log_utils
from blue.constant import Separator


###############
### Registry
#
class Registry:
    SEPARATOR = Separator.ENTITY

    def __init__(self, name="REGISTRY", type=None, id=None, platform_id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):
        """
        Initialize a registry instance with optional identifiers, type, namespace prefix/suffix, and properties.

        Parameters:
            name (str, optional): Registry name (default "REGISTRY").
            type (str, optional): Registry type (default "record").
            id (str, optional): Unique ID for the registry instance. Generated if not provided.
            platform_id (str, optional): Optional platform ID.
            sid (str, optional): Optional unique SID; defaults to name:id.
            cid (str, optional): Optional client ID; derived from SID with prefix/suffix if not provided.
            prefix (str, optional): Optional prefix for the CID.
            suffix (str, optional): Optional suffix for the CID.
            properties (dict, optional): Dictionary of properties (e.g., database connectivity, embeddings model).

        Initializes the registry, properties, logger, and starts a connection to the underlying datastore.
        """

        self.name = name

        if type == None:
            type = "record"
        self.type = type

        if id:
            self.id = id
        else:
            self.id = uuid_utils.create_uuid()

        if sid:
            self.sid = sid
        else:
            self.sid = self.name + ":" + self.id

        self.prefix = prefix
        self.suffix = suffix
        self.cid = cid
        self.platform_id = platform_id

        if self.cid == None:
            self.cid = self.sid

            if self.prefix:
                self.cid = self.prefix + ":" + self.cid
            if self.suffix:
                self.cid = self.cid + ":" + self.suffix

        self._initialize(properties=properties)

        self._start()

    ###### initialization
    def _initialize(self, properties=None):
        """
        Initialize internal state including properties, embeddings, vector dimensions, and logger.

        Parameters:
            properties (dict, optional): Overrides for default registry properties.
        """
        self._initialize_properties()
        self._update_properties(properties=properties)

        self.embeddings_model = None
        self.vector_dimensions = None

        self._initialize_logger()

    def _initialize_properties(self):
        """
        Initialize default properties for the registry, including database host/port
        and default embeddings model.
        """

        self.properties = {}

        # db connectivity
        self.properties['db.host'] = 'localhost'
        self.properties['db.port'] = 6379

        # embeddings model
        self.properties['embeddings_model'] = 'paraphrase-MiniLM-L6-v2'

    def _update_properties(self, properties=None):
        """
        Update registry properties with a given dictionary, overriding defaults.

        Parameters:
            properties (dict, optional): Dictionary of properties to update.
        """

        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def _initialize_logger(self):
        """
        Initialize and configure a custom logger for the registry instance.
        """
        self.logger = log_utils.CustomLogger()
        # customize log
        self.logger.set_config_data(
            "stack",
            "%(call_stack)s",
        )
        self.logger.set_config_data("registry", self.sid, -1)

    ###### database, data, index
    def _start_connection(self):
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()

    def _get_data_namespace(self):
        return self.cid + ':DATA'

    def __get_json_value(self, value, single=True):
        if value is None:
            return None
        if type(value) is list:
            if len(value) == 0:
                return None
            else:
                if single:
                    return value[0]
                else:
                    return value
        else:
            return value

    def _init_registry_namespace(self):
        # create registry-specific registry
        self.connection.json().set(self._get_data_namespace(), '$', {'contents': {}}, nx=True)

    def _set_json(self, name, path, obj):
        result = self.connection.json().set(name, path, obj)
        if result is None:
            reduced_path = ".".join(path.split(".")[:-1])
            result = self.connection.json().set(name, reduced_path, {})
            if result:
                result = self.connection.json().set(name, path, obj, nx=True)
                if result is None:
                    raise Exception("Failed to set: " + str(name) + " " + str(path))

    def _get_index_name(self):
        return self.cid

    def _get_doc_prefix(self):
        return self.cid + ':INDEX'

    def _init_search_index(self):
        """
        Initialize the search index in Redis for the registry.

        This method performs the following steps:
        1. Loads the embeddings model (deferred loading for efficiency).
        2. Determines the index name and document prefix.
        3. Checks if the index already exists in Redis:
        - If it exists, logs the index info.
        - If it does not exist, builds the index schema, creates the index,
            and logs the newly created index info.

        The index is configured with a schema containing textual fields and
        a vector field for embeddings, enabling semantic search.
        """

        # defered loading of model
        global SentenceTransformer
        from sentence_transformers import SentenceTransformer

        # init embeddings model
        self._init_search_embeddings_model()

        index_name = self._get_index_name()
        doc_prefix = self._get_doc_prefix()

        try:
            # check if index exists
            self.logger.info(self.connection.ft(index_name).info())
            self.logger.info('Search index ' + index_name + ' already exists.')
        except:
            self.logger.info('Creating search index...' + index_name)

            # schema
            schema = self._build_index_schema()

            # index definition
            definition = IndexDefinition(prefix=[doc_prefix], index_type=IndexType.HASH)

            # create index
            self.connection.ft(index_name).create_index(fields=schema, definition=definition)

            # report index info
            self.logger.info(self.connection.ft(index_name).info())

    def _build_index_schema(self):
        """
        Build the schema definition for the Redis search index.

        The schema includes:
            - "name": Text field with higher weight for relevance scoring.
            - "type": Text field indicating the type of entity.
            - "scope": Text field for scoping information.
            - "description": Text field containing descriptive text.
            - "vector": Vector field for semantic embeddings, configured with:
                * type FLOAT32
                * dimensionality equal to `self.vector_dimensions`
                * cosine distance metric

        Returns:
            tuple: A tuple of field definitions to be used when creating
                a Redis search index.
        """

        schema = (
            # name
            TextField("name", weight=2.0),
            # type
            TextField("type"),
            # scope
            TextField("scope"),
            # description text
            TextField("description"),
            # values (for attribute example values)
            VectorField(
                "vector",
                "FLAT",
                {
                    "TYPE": "FLOAT32",
                    "DIM": self.vector_dimensions,
                    "DISTANCE_METRIC": "COSINE",
                },
            ),
        )
        return schema

    def build_index(self):
        """
        Build or rebuild the full search index for all records in the registry.

        This method initializes the embeddings model and Redis search index if
        not already set up, retrieves all records recursively, and indexes them
        using a Redis pipeline for efficient bulk updates.

        Returns:
            None
        """

        # deferred initialization
        if self.embeddings_model is None:
            self._init_search_index()

        index_name = self._get_index_name()
        doc_prefix = self._get_doc_prefix()

        records = self.list_records(recursive=True)

        # instantiate a redis pipeline
        pipe = self.connection.pipeline(transaction=False)

        for record in records:
            self._set_index_record(record, recursive=True, pipe=pipe)

        res = pipe.execute()

        # report index info
        self.logger.info(self.connection.ft(index_name).info())

    def _set_index_record(self, record, recursive=False, pipe=None):
        """
        Index a single record (or recursively its nested contents) in the Redis search index.

        Parameters:
            record (dict): The record to index. Must include 'name', 'type', and 'scope'.
                Optionally may contain 'description' and nested 'contents'.
            recursive (bool, optional): If True, recursively index nested records in 'contents'.
            pipe (redis.client.Pipeline, optional): Redis pipeline to batch multiple operations.

        !!! note
            - Deferred initialization of the embeddings model occurs if it has not been loaded.
            - Records missing required fields ('name', 'type', 'scope') are skipped.
            - Nested contents, if present, are indexed recursively when `recursive=True`.
        """

        # deferred initialization
        if self.embeddings_model is None:
            self._init_search_index()

        if 'name' not in record:
            return

        if 'type' not in record:
            return

        if 'scope' not in record:
            return

        name = record['name']
        type = record['type']
        scope = record['scope']
        description = record['description']

        self._create_index_doc(name, type, scope, description, pipe=pipe)

        # index contents
        if recursive:
            contents = record.get('contents', {})
            for type_key in contents:
                contents_by_type = contents[type_key]
                for record_key in contents_by_type:
                    r = contents_by_type[record_key]
                    self._set_index_record(r, recursive=recursive, pipe=pipe)

    def _create_index_doc(self, name, type, scope, description, values=None, pipe=None):
        """
        Create and store a single document in the Redis search index with embedding vector.

        Parameters:
            name (str): Name of the entity.
            type (str): Type of the entity.
            scope (str): Scope or category of the entity.
            description (str): Descriptive text to include in the embedding vector.
            values (list, optional): Additional attribute values to include (currently unused).
            pipe (redis.client.Pipeline, optional): Redis pipeline to batch multiple operations.

        !!! note
            - The method combines `name` and `description` to compute the embedding vector.
            - If a Redis pipeline is provided, the document is added to the pipeline; otherwise,
            a new pipeline is created and executed immediately.
            - Deferred initialization of the embeddings model occurs if it has not been loaded.
        """
        # deferred initialization
        if self.embeddings_model is None:
            self._init_search_index()

        # TODO: Identify the best way to compute embedding vector, for now name + description
        # added values when available
        text = name
        if description:
            text += ' ' + description

        vector = self._compute_embedding_vector(text)

        doc = {'name': name, 'type': type, 'scope': scope, 'description': description, 'vector': vector}

        # define key
        doc_key = self.__doc_key(name, type, scope)

        if pipe:
            pipe.hset(doc_key, mapping=doc)
        else:
            pipe = self.connection.pipeline()
            pipe.hset(doc_key, mapping=doc)
            res = pipe.execute()

    def __doc_key(self, name, type, scope):
        """
        Compute the key for a document in the search index.

        Parameters:
            name (str): Record name.
            type (str): Record type.
            scope (str): Record scope.

        Returns:
            str: Document key.
        """

        index_name = self._get_index_name()
        doc_prefix = self._get_doc_prefix()

        if scope[len(scope) - 1] == '/':
            scope = scope[:-1]

        return doc_prefix + ':' + self._encode(type) + ":" + self._encode(scope) + "/" + self._encode(type) + "/" + self._encode(name)

    def _delete_index_record(self, record, pipe=None):
        """
        Delete a record and all nested records from the search index.

        Parameters:
            record (dict): Record to delete.
            pipe: Optional Redis pipeline for batch deletion.
        """

        name = record['name']
        type = record['type']
        scope = record['scope']
        self._delete_index_doc(name, type, scope, pipe=pipe)

        # recursively delete all under scope
        contents = record['contents']

        for type_key in contents:
            contents_by_type = contents[type_key]
            for record_key in contents_by_type:
                r = contents_by_type[record_key]

                self._delete_index_record(r, pipe=pipe)

    def _delete_index_doc(self, name, type, scope, pipe=None):
        """
        Delete a document from the search index by key.

        Parameters:
            name (str): Record name.
            type (str): Record type.
            scope (str): Record scope.
            pipe: Optional Redis pipeline for batch deletion.
        """
        # deferred initialization
        if self.embeddings_model is None:
            self._init_search_index()

        # define key
        doc_key = self.__doc_key(name, type, scope)

        fields = ["name", "type", "scope", "description", "vector"]

        if pipe:
            for field in fields:
                pipe.hdel(doc_key, field)
        else:
            pipe = self.connection.pipeline()
            for field in fields:
                pipe.hdel(doc_key, field)

            res = pipe.execute()

    def search_records(self, keywords, type=None, scope=None, approximate=False, hybrid=False, page=0, page_size=5, page_limit=10):
        """
        Search indexed records using keyword or vector-based similarity.

        Supports exact keyword matching, approximate vector search, or a hybrid
        combination of both. Optionally filters results by record type and scope.

        Parameters:
            keywords (str): The text or query keywords to search for.
            type (str, optional): Filter by record type (e.g., 'entity', 'collection').
            scope (str, optional): Filter by record scope (e.g., database or source name).
            approximate (bool, optional): If True, performs vector-only similarity search.
            hybrid (bool, optional): If True, combines keyword and vector search for better recall.
            page (int, optional): Page index for pagination (default is 0).
            page_size (int, optional): Number of results per page (default is 5).
            page_limit (int, optional): Total number of results to consider before paging (default is 10).

        Returns:
            list[dict]: A list of search result dictionaries containing
                record fields such as `name`, `type`, `id`, `scope`,
                and optionally `score` when using vector search.
        """

        # deferred initialization
        if self.embeddings_model is None:
            self._init_search_index()

        index_name = self._get_index_name()
        doc_prefix = self._get_doc_prefix()

        q = None

        qs = ""

        if type:
            qs = "(@type: \"" + type + "\" )" + " " + qs
        if scope:
            qs = "(@scope: \"" + scope + "\" )" + " " + qs

        if hybrid:
            q = "( " + qs + " " + " $kw " + " )" + " => [KNN " + str((page_limit) * page_size) + " @vector $v as score]"

            query = Query(q).sort_by("score").return_fields("id", "name", "type", "scope", "score").paging(0, page_limit * page_size).dialect(2)

        else:
            if approximate:
                if qs == "":
                    qs = "*"
                q = "( " + qs + " )" + " => [KNN " + str((page_limit) * page_size) + " @vector $v as score]"
                query = Query(q).sort_by("score").return_fields("id", "name", "type", "scope", "score").paging(0, page_limit * page_size).dialect(2)

            else:
                q = "( " + qs + " " + " $kw " + " )"
                query = Query(q).return_fields("id", "name", "type", "scope").paging(0, page_limit * page_size).dialect(2)

        query_params = {"kw": keywords, "v": self._compute_embedding_vector(keywords)}

        self.logger.info('searching: ' + keywords + ', ' + 'approximate=' + str(approximate) + ', ' + 'hybrid=' + str(hybrid))
        self.logger.info('using search query: ' + q)
        results = self.connection.ft(index_name).search(query, query_params).docs

        # field', 'id', 'name', 'payload', 'score', 'type
        if approximate or hybrid:
            results = [{"name": result['name'], "type": result['type'], "id": result['id'], "scope": result['scope'], "score": result['score']} for result in results]
        else:
            results = [{"name": result['name'], "type": result['type'], "id": result['id'], "scope": result['scope']} for result in results]

        # do paging
        page_results = results[page * page_size : (page + 1) * page_size]
        self.logger.info('results: ' + str(page_results))
        return page_results

    ###### embeddings
    def _init_search_embeddings_model(self):
        """
        Initialize the sentence embeddings model and set vector dimensions.
        """

        embeddings_model = self.properties['embeddings_model']
        self.logger.info('Loading embeddings model: ' + embeddings_model)
        self.embeddings_model = SentenceTransformer(embeddings_model)

        sentence = ['sample']
        embedding = self.embeddings_model.encode(sentence)[0]

        # override vector_dimensions
        self.vector_dimensions = embedding.shape[0]

    def _compute_embedding_vector(self, text):
        """
        Compute the embedding vector for a given text using the embeddings model.

        Parameters:
            text (str): Input text.

        Returns:
            bytes: Flattened float32 embedding vector as bytes.
        """
        sentence = [text]
        embedding = self.embeddings_model.encode(sentence)[0]
        return embedding.astype(np.float32).tobytes()

    ###### registry functions
    def register_record(self, name, type, scope, icon=None, created_by=None, description="", properties={}, rebuild=False):
        """
        Register a new record in the registry namespace.

        Creates and stores a record with basic metadata (name, type, scope, description, etc.).
        Optionally rebuilds the search index for the new record.

        Parameters:
            name (str): The record name.
            type (str): The record type (e.g., 'entity', 'collection').
            scope (str): The scope or parent context (e.g., database name).
            icon (str, optional): Optional icon identifier.
            created_by (str, optional): User or process that created the record.
            description (str, optional): Record description text.
            properties (dict, optional): Additional structured record properties.
            rebuild (bool, optional): Whether to immediately rebuild the index after registration.

        Returns:
            None
        """

        record = {}
        record['name'] = name
        record['type'] = type
        record['scope'] = scope
        record['description'] = description
        record['created_by'] = created_by
        record['properties'] = properties
        record['icon'] = icon

        # default contents
        record['contents'] = {}

        # Encode all values recursively
        encoded_record = self._encode_dict(record)

        ## create a record on the registry name space
        p = self._get_record_path(name, type, scope)

        self._set_json(self._get_data_namespace(), p, encoded_record)

        # rebuild now
        if rebuild:
            self._set_index_record(record)

    def register_record_json(self, record, recursive=True, rebuild=False):
        """
        Register a record and its nested contents from a JSON structure.
        Supports recursive registration of all child records within the JSON object.

        Parameters:
            record (dict): Record definition containing fields like name, type, scope, properties, and contents.
            recursive (bool, optional): Whether to register nested records under 'contents' recursively.
            rebuild (bool, optional): Whether to rebuild the index after registration.

        Returns:
            None
        """

        name = None
        if 'name' in record:
            name = record['name']

        type = "default"
        if 'type' in record:
            type = record['type']

        scope = None
        if 'scope' in record:
            scope = record['scope']

        description = ""
        if 'description' in record:
            description = record['description']

        icon = None
        if 'icon' in record:
            icon = record['icon']

        properties = {}
        if 'properties' in record:
            properties = record['properties']

        created_by = None
        if 'created_by' in record:
            created_by = record['created_by']

        if name and type and scope:
            self.register_record(name, type, scope, created_by=created_by, description=description, icon=icon, properties=properties, rebuild=rebuild)

        if recursive:
            contents = {}
            if 'contents' in record:
                contents = record['contents']

                for type_key in contents:
                    contents_by_type = contents[type_key]
                    for record_key in contents_by_type:
                        r = contents_by_type[record_key]
                        self.register_record_json(r, recursive=recursive, rebuild=rebuild)

    def update_record(self, name, type, scope, description="", icon=None, properties={}, rebuild=False):
        """
        Update an existing record's metadata or properties.

        Constructs a minimal record update payload and delegates the update
        to `update_record_json` for merging with the existing record data.

        Parameters:
            name (str): The record name.
            type (str): The record type.
            scope (str): The record scope.
            description (str, optional): Updated description text.
            icon (str, optional): Updated icon value.
            properties (dict, optional): Updated or merged record properties.
            rebuild (bool, optional): Whether to rebuild the index after update.

        Returns:
            tuple: The original and merged record dictionaries.
        """

        record = {}
        record['name'] = name
        record['type'] = type
        record['scope'] = scope
        record['description'] = description
        record['icon'] = icon
        record['properties'] = properties

        return self.update_record_json(record, rebuild=rebuild)

    def update_record_json(self, record, recursive=True, rebuild=False):
        """
        Update an existing record in JSON form, merging it with the original.

        Fetches the existing record, merges it with new values, and re-registers
        the result. Can optionally apply updates recursively to nested records.

        Parameters:
            record (dict): Partial or complete record update in JSON form.
            recursive (bool, optional): Whether to update nested records recursively.
            rebuild (bool, optional): Whether to rebuild the index after update.

        Returns:
            tuple: The original and merged record dictionaries.
        """

        name = None
        if 'name' in record:
            name = record['name']
        if 'type' in record:
            type = record['type']
        if 'scope' in record:
            scope = record['scope']

        # fetch original
        original_record = self.get_record(name, type, scope)

        # merge
        merged_record = json_utils.merge_json(original_record, record)
        # re-register
        self.register_record_json(merged_record, recursive=recursive, rebuild=rebuild)

        # return original and merged
        return original_record, merged_record

    def parse_path(self, path):
        """
        Parse a JSON path string into a dictionary of keys and values.

        Parameters:
            path (str): JSON path.

        Returns:
            dict: Extracted key-value mapping.
        """

        pa = path.split("/")[1:]
        o = {}
        keys = pa[::2]
        if len(keys) <= 1:
            return o
        values = pa[1:][::2]
        for i, key in enumerate(keys):
            o[key] = values[i]
        return o

    def _extract_shortname(self, name):
        # use name to identify scope, short name
        s = name.split(self.SEPARATOR)
        sn = s[-1]
        return sn

    def _derive_scope_from_name(self, name, full=False):
        hierarchy = name.split(self.SEPARATOR)
        if not full:
            hierarchy = hierarchy[:-1]
        prefix = ""
        scope = ""
        for ei in hierarchy:
            entity_name = prefix + ei
            prefix = entity_name + self.SEPARATOR
            scope += "/" + self.type + "/" + entity_name
        if scope == "":
            scope = "/"
        return scope

    def _get_record_path(self, name, type, scope):
        sp = self._get_scope_path(scope)

        rp = sp + self._encode(type) + "." + self._encode(name)
        return rp

    def _get_scope_path(self, scope, type=None, recursive=False):
        # remove leading and trailing /s
        if len(scope) >= 1 and scope[0] == "/":
            scope = scope[1:]
        if len(scope) >= 1 and scope[len(scope) - 1] == '/':
            scope = scope[:-1]
        # add final /
        scope = scope + "/"
        # compute json path
        sa = scope.split("/")
        p = "$."
        for i, si in enumerate(sa):
            if i % 2 == 0:
                p = p + "contents" + "."
            if len(si) > 0:
                p = p + self._encode(si) + "."

        if type:
            p = p + self._encode(type) + "."

        if recursive:
            p = p + "."

        return p

    def get_record(self, name, type, scope):
        """
        Retrieve a decoded record from the registry by name, type, and scope.

        Returns:
            dict: Record data.
        """

        sp = self._get_record_path(name, type, scope)

        record = self.connection.json().get(self._get_data_namespace(), Path(sp))
        if len(record) == 0:
            return {}
        else:
            record = record[0]

        # decode keys only
        decoded_record = self._decode_dict(record)

        return self.__get_json_value(decoded_record)

    def get_record_data(self, name, type, scope, key, single=True):
        """
        Retrieve a specific field from a record in the registry.

        Returns:
            Any: Decoded value of the field.
        """

        p = self._get_record_path(name, type, scope)
        value = self.connection.json().get(self._get_data_namespace(), Path(p + '.' + key))

        decoded_value = self._decode_dict(value) if value is not None else value

        return self.__get_json_value(decoded_value, single=single)

    def _is_jsonpath_expr(self, key: str) -> bool:
        # treat bracket notation, wildcard, or explicit dot path as expressions -> do not encode whole key
        if not isinstance(key, str):
            return False
        return ("[" in key) or ("*" in key) or ("." in key)

    def set_record_data(self, name, type, scope, key, value, rebuild=False):
        """
        Set or update a specific key-value pair in a registry record.

        This method encodes the key and value for safe JSON storage, updates the
        underlying data in the registry’s datastore, and optionally rebuilds the
        record’s index entry.

        Parameters:
            name (str): Record name.
            type (str): Record type.
            scope (str): Record scope (namespace or hierarchical path).
            key (str): JSON key path or property name to set.
            value (Any): Value to assign at the specified key.
            rebuild (bool, optional): Whether to rebuild the search index entry after update. Defaults to False.

        """

        p = self._get_record_path(name, type, scope)
        encoded_value = self._encode_dict(value)

        if isinstance(key, str) and self._is_jsonpath_expr(key):
            path_key = key
        else:
            path_key = self._encode(key)

        self._set_json(self._get_data_namespace(), p + '.' + path_key, encoded_value)

        # rebuild now
        if rebuild:
            record = self.get_record(name, type, scope)
            self._set_index_record(record)

    def delete_record_data(self, name, type, scope, key, rebuild=False):
        """
        Delete a specific key or field from a registry record.

        This method removes a property or subfield from the JSON structure stored in
        the registry. Optionally, it can rebuild the record’s index entry to reflect
        the deletion.

        Parameters:
            name (str): Record name.
            type (str): Record type.
            scope (str): Record scope.
            key (str): JSON key or path to delete.
            rebuild (bool, optional): Whether to rebuild the search index entry after deletion. Defaults to False.

        """

        p = self._get_record_path(name, type, scope)
        self.connection.json().delete(self._get_data_namespace(), p + '.' + key)

        # rebuild now
        if rebuild:
            record = self.get_record(name, type, scope)
            self._set_index_record(record)

    def get_record_description(self, name, type, scope):
        """
        Retrieve the textual description of a registry record.

        Parameters:
            name (str): Record name.
            type (str): Record type.
            scope (str): Record scope.

        Returns:
            str or None: Description text if present, otherwise None.

        """

        return self.get_record_data(name, type, scope, 'description')

    def set_record_description(self, name, type, scope, description, rebuild=False):
        """
        Set or update the 'description' field of a record in the registry.

        Parameters:
            name (str): Name of the record/entity.
            type (str): Type of the record/entity.
            scope (str): Scope or category of the record/entity.
            description (str): The description text to assign to the record.
            rebuild (bool, optional): If True, rebuild or reindex the record after updating.
                Defaults to False.

        """
        self.set_record_data(name, type, scope, 'description', description, rebuild=rebuild)

    def get_record_properties(self, name, type, scope):
        """
        Retrieve all custom properties of a registry record.

        Parameters:
            name (str): Record name.
            type (str): Record type.
            scope (str): Record scope.

        Returns:
            dict: Dictionary of property key-value pairs.

        """

        return self.get_record_data(name, type, scope, 'properties')

    def get_record_property(self, name, type, scope, key):
        """
        Retrieve a specific property value from a registry record.

        Parameters:
            name (str): Record name.
            type (str): Record type.
            scope (str): Record scope.
            key (str): Property name.

        Returns:
            Any: Value of the property if found, otherwise None.

        """

        encoded_key = self._encode(key)
        escaped_key = '["' + encoded_key + '"]'
        return self.get_record_data(name, type, scope, 'properties' + '.' + escaped_key)

    def set_record_property(self, name, type, scope, key, value, rebuild=False):
        """
        Set or update a specific property for a registry record.

        Parameters:
            name (str): Record name.
            type (str): Record type.
            scope (str): Record scope.
            key (str): Property name.
            value (Any): Property value.
            rebuild (bool, optional): Whether to rebuild the search index after update. Defaults to False.
        """

        encoded_key = self._encode(key)
        escaped_key = '["' + encoded_key + '"]'
        self.set_record_data(name, type, scope, 'properties' + '.' + escaped_key, value, rebuild=rebuild)

    def delete_record_property(self, name, type, scope, key, rebuild=False):
        """
        Delete a specific property from a registry record.

        Parameters:
            name (str): Record name.
            type (str): Record type.
            scope (str): Record scope.
            key (str): Property name to delete.
            rebuild (bool, optional): Whether to rebuild the search index entry after deletion. Defaults to False.
        """

        encoded_key = self._encode(key)
        escaped_key = '["' + encoded_key + '"]'
        self.delete_record_data(name, type, scope, 'properties' + '.' + escaped_key, rebuild=rebuild)

    def get_record_contents(self, name, type, scope):
        """
        Retrieve all nested contents (child elements) of a registry record.

        Parameters:
            name (str): Record name.
            type (str): Record type.
            scope (str): Record scope.

        Returns:
            list[dict]: List of nested content items or an empty list if none exist.
        """

        return self.get_record_data(name, type, scope, 'contents.*', single=False)

    def filter_record_contents(self, name, type, scope, filter_type=None, filter_name=None, single=False):
        """
        Filter the contents of a registry record by type and/or name.

        Parameters:
            name (str): Name of the parent record.
            type (str): Type of the parent record.
            scope (str): Scope of the parent record.
            filter_type (str, optional): Type of child records to filter. Defaults to None.
            filter_name (str, optional): Name of child record to filter. Defaults to None.
            single (bool, optional): If True, return only the first matching record. Defaults to False.

        Returns:
            list or dict: Filtered child records matching the criteria, or a single record if `single=True`.
        """

        query = ""
        if filter_type:
            query = query + '@type=="' + filter_type + '"'
        if filter_name:
            if len(query) > 0:
                query = query + "&&"
                query = query + '@name=="' + filter_name + '"'
        if filter_type or filter_name:
            query = '[?(' + query + ')]'

        return self.get_record_data(name, type, scope, 'contents.*.' + query, single=single)

    def get_contents(self):
        """
        Retrieve the full JSON contents of the registry.

        Returns:
            dict: The complete data stored under the source's data namespace.
                If no data exists, returns an empty dictionary.

        !!! note
            - Uses the underlying JSON connection to fetch all data.
            - Only the top-level object is returned, not individual records.
        """
        data = self.connection.json().get(self._get_data_namespace(), Path('$'))
        if len(data) > 0:
            data = data[0]
        else:
            data = {}
        return data

    def get_records(self):
        """
        Retrieve all individual records from the registry, excluding nested contents.

        Returns:
            list[dict]: A list of record dictionaries. Each dictionary represents a record
                        without its nested 'contents'.

        !!! note
            - Uses JSONPath to extract all records under the 'contents' hierarchy.
            - Deep copies are made to avoid modifying the original data.
        """
        contents = self.get_contents()
        records = []
        r = json_utils.json_query(contents, "$..contents.*", single=False)
        for ri in r:
            # make a copy
            ric = copy.deepcopy(ri)
            del ric['contents']
            records.append(ric)

        return records

    def deregister(self, record, rebuild=False):
        """
        Remove a record (and nested contents) from the registry, optionally updating the index.
        """

        if record is not None:
            name = record['name']
            type = record['type']
            scope = record['scope']

            # get full record so we can recursively delete
            record = self.get_record(name, type, scope)

            p = self._get_record_path(name, type, scope)
            self.connection.json().delete(self._get_data_namespace(), p)

            # rebuild now
            if rebuild:
                self._delete_index_record(record)

    def list_records(self, type=None, scope="/", recursive=False):
        """
        List records in the registry under a given scope, optionally filtered by type.

        Parameters:
            type (str, optional): Type of records to retrieve. If None, all types are returned.
            scope (str, optional): Registry scope/path to search in. Defaults to "/".
            recursive (bool, optional): If True, include records in all nested sub-scopes. Defaults to False.

        Returns:
            list: Decoded records matching the criteria. Returns an empty list if no records are found.
        """

        sp = self._get_scope_path(scope, type=type, recursive=recursive)

        if type:
            sp = sp + '[?(@.type=="' + type + '")]'
        else:
            sp = sp + '*.[?(@.type)]'

        records = self.connection.json().get(self._get_data_namespace(), Path(sp))

        if records:
            return [self._decode_dict(r) for r in records]

        return []

    def filter_records_by_properties(self, type=None, scope="/", properties=None, recursive=False, partial_match=False):
        """
        Filter records by matching their properties against a given set of property criteria.

        Parameters:
            type (str, optional): Type of records to filter (e.g., "collection", "attribute").
                Defaults to None, meaning all types are considered.
            scope (str, optional): Scope to search records within. Defaults to "/".
            properties (dict, optional): Dictionary of properties to match against record properties.
                If None, no filtering is applied. Nested dictionaries are supported.
            recursive (bool, optional): If True, search recursively within sub-scopes.
                Defaults to False.
            partial_match (bool, optional): If True, property values are matched by substring
                containment instead of exact equality. Defaults to False.

        Returns:
            list: A list of records (dicts) whose properties match the given filter criteria.
        """

        def match_props(record_props, filter_props):
            for k, v in filter_props.items():
                if isinstance(v, dict):
                    if k not in record_props or not isinstance(record_props[k], dict):
                        return False
                    if not match_props(record_props[k], v):
                        return False
                else:
                    val = record_props.get(k)
                    if partial_match:
                        if val is None or v not in str(val):
                            return False
                    else:
                        if val != v:
                            return False
            return True

        all_records = self.list_records(type=type, scope=scope, recursive=recursive)
        if not properties:
            return all_records

        filtered = []
        for record in all_records:
            record_props = record.get("properties", {})
            if match_props(record_props, properties):
                filtered.append(record)
        return filtered

    ######
    def _start(self):
        # self.logger.info('Starting session {name}'.format(name=self.name))
        self._start_connection()

        # initialize registry data
        self._init_registry_namespace()

        # defer building search index on registry until first search
        # self._init_search_index()

        self.logger.info('Started registry {name}'.format(name=self.name))

    ###### save/load
    def dumps(self):
        """
        Serialize all records in the registry to a string.

        Returns:
            str: A string representation of all records, including nested contents.
        """
        records = self.list_records(recursive=True)
        return str(records)

    def dump(self, output_file):
        """
        Save all records from the registry to a JSON file.

        Parameters:
            output_file (str): Path to the output file where records will be written.

        !!! note
            - Only writes if the specified file exists.
            - Records include nested contents and all metadata.
        """
        records = self.list_records(recursive=True)
        if os.path.exists(output_file):
            with open(output_file, 'w') as fp:
                json.dump(records, fp)

    def load(self, input_file):
        """
        Load records from a JSON file into the registry.

        Parameters:
            input_file (str): Path to the JSON file containing the records.

        !!! note
            - Only loads if the file exists.
            - Existing records in the registry will be updated/merged.
        """
        if os.path.exists(input_file):
            with open(input_file, 'r') as fp:
                records = json.load(fp)

                self._load_records(records)

    def loads(self, input_string):
        """
        Load records into the registry from a JSON string.

        Parameters:
            input_string (str): JSON string representing a list of records.

        !!! note
            - Existing records in the registry will be updated/merged.
            - Handles nested contents automatically.
        """
        records = json.loads(input_string)

        self._load_records(records)

    def _load_records(self, records):
        for record in records:
            self.register_record_json(record)

        # index registry
        self.build_index()

    # encode/decode keys
    encodings = {".": "__DOT__", "*": "__STAR__", "?": "__Q__"}

    def _encode(self, s):
        for k, v in self.encodings.items():
            s = s.replace(k, v)
        return s

    def _decode(self, s):
        for k, v in self.encodings.items():
            s = s.replace(v, k)
        return s

    def _encode_dict(self, obj):
        """Recursively encode dict keys only (values unchanged)."""
        if isinstance(obj, dict):
            return {self._encode(k): self._encode_dict(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._encode_dict(v) for v in obj]
        else:
            return obj  # leave values untouched

    def _decode_dict(self, obj):
        """Recursively decode dict keys only (values unchanged)."""
        if isinstance(obj, dict):
            return {self._decode(k): self._decode_dict(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._decode_dict(v) for v in obj]
        else:
            return obj  # leave values untouched
