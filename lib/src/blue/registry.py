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
from blue.metadata import MetaData


###############
### Registry
#
class Registry:
    SEPARATOR = Separator.ENTITY

    def __init__(self, name="REGISTRY", type=None, id=None, platform_id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):

        self.name = name
        self.metadata = MetaData(platform_id=platform_id)
        

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
        self._initialize_properties()
        self._update_properties(properties=properties)

        self.embeddings_model = None
        self.vector_dimensions = None

        self._initialize_logger()

    def _initialize_properties(self):
        self.properties = {}

        # db connectivity
        self.properties['db.host'] = 'localhost'
        self.properties['db.port'] = 6379

        # embeddings model
        self.properties['embeddings_model'] = 'paraphrase-MiniLM-L6-v2'

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def _initialize_logger(self):
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
            TextField("values"),
            # description embedding
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

        # deferred initialization
        if self.embeddings_model is None:
            self._init_search_index()

        if 'name' not in record:
            return

        name = record['name']
        type = record['type']
        scope = record['scope']
        description = record['description']

        if type == "attribute":
            props = record.get("properties", {})
            info = props.get("info", {})
            values = info.get("values", [])
            if isinstance(values, list) and values:
                self._create_index_doc(name, type, scope, description, values, pipe=pipe)
            else:
                 self._create_index_doc(name, type, scope, description, pipe=pipe)
        else:
                self._create_index_doc(name, type, scope, description, pipe=pipe)
        

        # index contents
        if recursive:
            contents = record['contents']
            for type_key in contents:
                contents_by_type = contents[type_key]
                for record_key in contents_by_type:
                    r = contents_by_type[record_key]
                    self._set_index_record(r, recursive=recursive, pipe=pipe)

    def _create_index_doc(self, name, type, scope, description, values=None, pipe=None):

        # deferred initialization
        if self.embeddings_model is None:
            self._init_search_index()

        # TODO: Identify the best way to compute embedding vector, for now name + description
        # added values when available
        text = name
        if description:
            text += ' ' + description

        values_str = None

        if values:
            text += " " + " ".join(map(str, values))
            values_str = json.dumps(values, ensure_ascii=False)
        
        vector = self._compute_embedding_vector(text)

        doc = {'name': name, 'type': type, 'scope': scope, 'description': description, 'vector': vector}

        if values_str:
            doc["values"] = values_str

        # define key
        doc_key = self.__doc_key(name, type, scope)

        if pipe:
            pipe.hset(doc_key, mapping=doc)
        else:
            pipe = self.connection.pipeline()
            pipe.hset(doc_key, mapping=doc)
            res = pipe.execute()

    def __doc_key(self, name, type, scope):
        index_name = self._get_index_name()
        doc_prefix = self._get_doc_prefix()

        if scope[len(scope) - 1] == '/':
            scope = scope[:-1]

        return doc_prefix + ':' + type + ":" + scope + "/" + name

    def _delete_index_record(self, record, pipe=None):
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

        # deferred initialization
        if self.embeddings_model is None:
            self._init_search_index()

        # define key
        doc_key = self.__doc_key(name, type, scope)

        fields = ["name", "type", "scope", "description", "values", "vector"]


        if pipe:
            for field in fields:
                pipe.hdel(doc_key, field)
        else:
            pipe = self.connection.pipeline()
            for field in fields:
                pipe.hdel(doc_key, field)
            
            res = pipe.execute()

    def search_records(self, keywords, type=None, scope=None, approximate=False, hybrid=False, page=0, page_size=5, page_limit=10):

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

        embeddings_model = self.properties['embeddings_model']
        self.logger.info('Loading embeddings model: ' + embeddings_model)
        self.embeddings_model = SentenceTransformer(embeddings_model)

        sentence = ['sample']
        embedding = self.embeddings_model.encode(sentence)[0]

        # override vector_dimensions
        self.vector_dimensions = embedding.shape[0]

    def _compute_embedding_vector(self, text):

        sentence = [text]
        embedding = self.embeddings_model.encode(sentence)[0]
        return embedding.astype(np.float32).tobytes()

    ###### registry functions
    def register_record(self, name, type, scope, icon=None, created_by=None, description="", properties={}, rebuild=False):
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

        ## create a record on the registry name space
        p = self._get_record_path(name, type, scope)

        self._set_json(self._get_data_namespace(), p, record)

        # rebuild now
        if rebuild:
            self._set_index_record(record)

    def register_record_json(self, record, recursive=True, rebuild=False):
        name = None
        if 'name' in record:
            name = record['name']

        type = "default"
        if 'type' in record:
            type = record['type']

        scope = "/"
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
        record = {}
        record['name'] = name
        record['type'] = type
        record['scope'] = scope
        record['description'] = description
        record['icon'] = icon
        record['properties'] = properties

        return self.update_record_json(record, rebuild=rebuild)

    def update_record_json(self, record, recursive=True, rebuild=False):
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
        pa = path.split("/")[1:]
        o = {}
        keys = pa[::2]
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

        rp = sp + type + "." + name
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
                p = p + si + "."

        if type:
            p = p + type + "."

        if recursive:
            p = p + "."

        return p

    def get_record(self, name, type, scope):
        sp = self._get_record_path(name, type, scope)

        record = self.connection.json().get(self._get_data_namespace(), Path(sp))
        if len(record) == 0:
            return {}
        else:
            record = record[0]
        return self.__get_json_value(record)

    def get_record_data(self, name, type, scope, key, single=True):
        p = self._get_record_path(name, type, scope)
        value = self.connection.json().get(self._get_data_namespace(), Path(p + '.' + key))
        return self.__get_json_value(value, single=single)

    def set_record_data(self, name, type, scope, key, value, rebuild=False):
        p = self._get_record_path(name, type, scope)
        self._set_json(self._get_data_namespace(), p + '.' + key, value)

        # rebuild now
        if rebuild:
            record = self.get_record(name, type, scope)
            self._set_index_record(record)

    def delete_record_data(self, name, type, scope, key, rebuild=False):
        p = self._get_record_path(name, type, scope)
        self.connection.json().delete(self._get_data_namespace(), p + '.' + key)

        # rebuild now
        if rebuild:
            record = self.get_record(name, type, scope)
            self._set_index_record(record)

    def get_record_description(self, name, type, scope):
        return self.get_record_data(name, type, scope, 'description')

    def set_record_description(self, name, type, scope, description, rebuild=False):
        self.set_record_data(name, type, scope, 'description', description, rebuild=rebuild)

    def get_record_properties(self, name, type, scope):
        return self.get_record_data(name, type, scope, 'properties')

    def get_record_property(self, name, type, scope, key):
        escaped_key = '["' + key + '"]'
        return self.get_record_data(name, type, scope, 'properties' + '.' + escaped_key)

    def set_record_property(self, name, type, scope, key, value, rebuild=False):
        escaped_key = '["' + key + '"]'
        self.set_record_data(name, type, scope, 'properties' + '.' + escaped_key, value, rebuild=rebuild)

    def delete_record_property(self, name, type, scope, key, rebuild=False):
        escaped_key = '["' + key + '"]'
        self.delete_record_data(name, type, scope, 'properties' + '.' + escaped_key, rebuild=rebuild)

    def get_record_contents(self, name, type, scope):
        return self.get_record_data(name, type, scope, 'contents.*', single=False)

    def filter_record_contents(self, name, type, scope, filter_type=None, filter_name=None, single=False):
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
        data = self.connection.json().get(self._get_data_namespace(), Path('$'))
        if len(data) > 0:
            data = data[0]
        else:
            data = {}
        return data

    def get_records(self):
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
        sp = self._get_scope_path(scope, type=type, recursive=recursive)

        if type:
            sp = sp + '[?(@.type=="' + type + '")]'
        else:
            sp = sp + '*.[?(@.type)]'

        records = self.connection.json().get(self._get_data_namespace(), Path(sp))

        return records

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
        records = self.list_records(recursive=True)
        return str(records)

    def dump(self, output_file):
        records = self.list_records(recursive=True)
        if os.path.exists(output_file):
            with open(output_file, 'w') as fp:
                json.dump(records, fp)

    def load(self, input_file):
        if os.path.exists(input_file):
            with open(input_file, 'r') as fp:
                records = json.load(fp)

                self._load_records(records)

    def loads(self, input_string):
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
        for k, v in encodings.items():
            s = s.replace(k, v)
        return s

    def _decode(self, s):
        for k, v in encodings.items():
            s = s.replace(v, k)
        return s
