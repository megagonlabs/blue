###### OS / Systems
from curses import noecho
import os
import sys

###### Add lib path
sys.path.append('./lib/')


######
import time
import argparse
import logging
import time
import uuid
import random
import copy

###### Parsers, Formats, Utils
import re
import csv
import json
from utils import json_utils

import itertools
from tqdm import tqdm

###### Backend, Databases
import redis
from redis.commands.json.path import Path
from redis.commands.search.field import TextField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

#######
import numpy as np
from sentence_transformers import SentenceTransformer


class Registry:
    def __init__(self, name="REGISTRY", id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):

        self.name = name
        if id:
            self.id = id
        else:
            self.id = str(hex(uuid.uuid4().fields[0]))[2:]

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

    def _initialize_properties(self):
        self.properties = {}

        # db connectivity
        self.properties['db.host'] = 'localhost'
        self.properties['db.port'] = 6379

        # embeddings
        self.properties['vector_dimensions'] = 4
        # embeddings model
        self.properties['embeddings_model'] = 'paraphrase-MiniLM-L6-v2'

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    ###### database, data, index
    def _start_connection(self):
        host = self.properties['db.host']
        port = self.properties['db.port']

        self.connection = redis.Redis(host=host, port=port, decode_responses=True)

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

    def _get_index_name(self):
        return self.cid

    def _get_doc_prefix(self):
        return self.cid + ':INDEX'

    def _init_search_index(self):

        # init embeddings model
        self._init_search_embeddings_model()

        index_name = self._get_index_name()
        doc_prefix = self._get_doc_prefix()

        try:
            # check if index exists
            logging.info(self.connection.ft(index_name).info())
            logging.info('Search index ' + index_name + ' already exists.')
        except:
            logging.info('Creating search index...' + index_name)

            # schema
            schema = self._build_index_schema()

            # index definition
            definition = IndexDefinition(prefix=[doc_prefix], index_type=IndexType.HASH)

            # create index
            self.connection.ft(index_name).create_index(fields=schema, definition=definition)

            # report index info
            logging.info(self.connection.ft(index_name).info())

    def _build_index_schema(self):
        vector_dimensions = self.properties['vector_dimensions']

        schema = (
            # name
            TextField("name", weight=2.0),
            # type
            TextField("type"),
            # scope
            TextField("scope"),
            # description text
            TextField("description"),
            # description embedding
            VectorField(
                "vector",
                "FLAT",
                {
                    "TYPE": "FLOAT32",
                    "DIM": vector_dimensions,
                    "DISTANCE_METRIC": "COSINE",
                },
            ),
        )
        return schema

    def build_index(self):

        index_name = self._get_index_name()
        doc_prefix = self._get_doc_prefix()

        records = self.list_records()

        # instantiate a redis pipeline
        pipe = self.connection.pipeline()

        for name in records:
            record = records[name]
            self._set_index_record(record, recursive=True, pipe=pipe)

        res = pipe.execute()

        # report index info
        logging.info(self.connection.ft(index_name).info())

    def _set_index_record(self, record, recursive=False, pipe=None):

        name = record['name']
        type = record['type']
        scope = record['scope']
        description = record['description']

        # index description
        self._create_index_doc(name, type, scope, description, pipe=pipe)

        # index contents
        if recursive:
            contents = record['contents']
            for key in contents:
                r = contents[key]
                self._set_index_record(r, recursive=recursive, pipe=pipe)

    def _create_index_doc(self, name, type, scope, description, pipe=None):

        # TODO: Identify the best way to compute embedding vector, for now name + description
        vector = self._compute_embedding_vector(name + " " + description)

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

        for key in contents:
            r = contents[key]

            self._delete_index_record(r, pipe=pipe)

    def _delete_index_doc(self, name, type, scope, pipe=None):

        # define key
        doc_key = self.__doc_key(name, type, scope)
        print('delete: ' + doc_key)

        if pipe:
            pipe.hdel(doc_key, 1)
        else:
            pipe = self.connection.pipeline()
            for field in ["name", "type", "scope", "description", "vector"]:
                pipe.hdel(doc_key, field)
            res = pipe.execute()
            print(res)

    def search_records(
        self, keywords, type=None, scope=None, approximate=False, hybrid=False, page=0, page_size=5, page_limit=10
    ):

        index_name = self._get_index_name()
        doc_prefix = self._get_doc_prefix()

        q = None

        qs = ""

        if type:
            qs = "(@type: " + type + " )" + " " + qs
        if scope:
            qs = "(@scope: " + scope + " )" + " " + qs

        if hybrid:
            q = "( " + qs + " " + " $kw " + " )" + " => [KNN " + str((page_limit) * page_size) + " @vector $v as score]"

            query = (
                Query(q)
                .sort_by("score")
                .return_fields("id", "name", "type", "scope", "score")
                .paging(0, page_limit * page_size)
                .dialect(2)
            )

        else:
            if approximate:
                if qs == "":
                    qs = "*"
                q = "( " + qs + " )" + " => [KNN " + str((page_limit) * page_size) + " @vector $v as score]"
                query = (
                    Query(q)
                    .sort_by("score")
                    .return_fields("id", "name", "type", "scope", "score")
                    .paging(0, page_limit * page_size)
                    .dialect(2)
                )

            else:
                q = "( " + qs + " " + " $kw " + " )"
                query = (
                    Query(q).return_fields("id", "name", "type", "scope").paging(0, page_limit * page_size).dialect(2)
                )

        query_params = {"kw": keywords, "v": self._compute_embedding_vector(keywords)}

        logging.info(
            'searching: ' + keywords + ', ' + 'approximate=' + str(approximate) + ', ' + 'hybrid=' + str(hybrid)
        )
        logging.info('using search query: ' + q)
        results = self.connection.ft(index_name).search(query, query_params).docs

        # field', 'id', 'name', 'payload', 'score', 'type
        if approximate or hybrid:
            results = [
                {
                    "name": result['name'],
                    "type": result['type'],
                    "id": result['id'],
                    "scope": result['scope'],
                    "score": result['score'],
                }
                for result in results
            ]
        else:
            results = [
                {"name": result['name'], "type": result['type'], "id": result['id'], "scope": result['scope']}
                for result in results
            ]

        # do paging
        print(len(results))
        page_results = results[page * page_size : (page + 1) * page_size]
        return page_results

    ###### embeddings
    def _init_search_embeddings_model(self):

        embeddings_model = self.properties['embeddings_model']
        logging.info('Loading embeddings model: ' + embeddings_model)
        self.embeddings_model = SentenceTransformer(embeddings_model)

        sentence = ['sample']
        embedding = self.embeddings_model.encode(sentence)[0]

        # override vector_dimensions
        vector_dimensions = embedding.shape[0]
        self.properties['vector_dimensions'] = vector_dimensions

    def _compute_embedding_vector(self, text):

        sentence = [text]
        embedding = self.embeddings_model.encode(sentence)[0]
        return embedding.astype(np.float32).tobytes()

    ###### registry functions
    def register_record(self, name, type, scope, description="", properties={}, rebuild=False):
        record = {}
        record['name'] = name
        record['type'] = type
        record['scope'] = scope
        record['description'] = description

        record['properties'] = properties

        # default contents
        record['contents'] = {}

        ## create a record on the registry name space
        p = self._get_record_path(name, scope)

        self.connection.json().set(self._get_data_namespace(), p, record)

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

        properties = {}
        if 'properties' in record:
            properties = record['properties']

        self.register_record(name, type, scope, description=description, properties=properties, rebuild=rebuild)

        if recursive:
            contents = {}
            if 'contents' in record:
                contents = record['contents']
            for key in contents:
                content = contents[key]
                self.register_record_json(content, recursive=recursive, rebuild=rebuild)

    def update_record(self, name, type, scope, description="", properties={}, rebuild=False):
        record = {}
        record['name'] = name
        record['type'] = type
        record['scope'] = scope
        record['description'] = description

        record['properties'] = properties

        return self.update_record_json(record, rebuild=rebuild)

    def update_record_json(self, record, recursive=True, rebuild=False):
        name = None
        if 'name' in record:
            name = record['name']
        if 'scope' in record:
            scope = record['scope']

        # fetch original
        original_record = self.get_record(name, scope)

        # merge
        merged_record = json_utils.merge_json(original_record, record)

        # re-register
        self.register_record_json(merged_record, recursive=recursive, rebuild=rebuild)

        # return original and merged
        return original_record, merged_record

    def _get_record_path(self, name, scope):
        sp = self._get_scope_path(scope)
        p = sp + "." + name
        return p

    def _get_scope_path(self, scope):
        if scope[len(scope) - 1] == '/':
            scope = scope[:-1]

        # compute json path given prefix, scope, and name
        sa = scope.split("/")
        p = "$" + ".contents.".join(sa) + ".contents"
        return p

    def get_record(self, name, scope):
        p = self._get_record_path(name, scope)
        record = self.connection.json().get(self._get_data_namespace(), Path(p))
        if len(record) == 0:
            return {}
        else:
            record = record[0]
        return self.__get_json_value(record)

    def get_record_data(self, name, scope, key, single=True):
        p = self._get_record_path(name, scope)
        value = self.connection.json().get(self._get_data_namespace(), Path(p + '.' + key))
        return self.__get_json_value(value, single=single)

    def set_record_data(self, name, scope, key, value, rebuild=False):
        p = self._get_record_path(name, scope)
        self.connection.json().set(self._get_data_namespace(), p + '.' + key, value)

        # rebuild now
        if rebuild:
            record = self.get_record(name, scope)
            self._set_index_record(record)

    def delete_record_data(self, name, scope, key, rebuild=False):
        p = self._get_record_path(name, scope)
        self.connection.json().delete(self._get_data_namespace(), p + '.' + key)

        # rebuild now
        if rebuild:
            record = self.get_record(name, scope)
            self._set_index_record(record)

    def get_record_description(self, scope, name):
        return self.get_record_data(name, scope, 'description')

    def set_record_description(self, name, scope, description, rebuild=False):
        self.set_record_data(name, scope, 'description', description, rebuild=rebuild)

    def get_record_properties(self, name, scope):
        return self.get_record_data(name, scope, 'properties')

    def get_record_property(self, name, scope, key):
        escaped_key = '["' + key + '"]'
        return self.get_record_data(name, scope, 'properties' + '.' + escaped_key)

    def set_record_property(self, name, scope, key, value, rebuild=False):
        escaped_key = '["' + key + '"]'
        self.set_record_data(name, scope, 'properties' + '.' + escaped_key, value, rebuild=rebuild)

    def delete_record_property(self, name, scope, key, rebuild=False):
        escaped_key = '["' + key + '"]'
        self.delete_record_data(name, scope, 'properties' + '.' + escaped_key, rebuild=rebuild)

    def get_record_contents(self, name, scope, type=None):
        contents = {}
        if type:
            contents = self.get_record_data(name, scope, 'contents[?(@type=="' + type + '")]', single=False)
        else:
            contents = self.get_record_data(name, scope, 'contents', single=False)
        return contents

    def get_record_content(self, name, scope, key, type=None):
        data = {}
        if type:
            data = self.get_record_data(name, scope, 'contents[?(@type=="' + type + '"&&@name=="' + key + '")]')
        else:
            data = self.get_record_data(name, scope, 'contents' + '.' + key)
        return data

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
        r = json_utils.json_query(contents, "$..contents", single=False)
        for ri in r:
            rs = list(ri.values())
            for rsi in rs:
                rsic = copy.deepcopy(rsi)
                del rsic['contents']
                records.append(rsic)

        return records

    def deregister(self, record, rebuild=False):

        name = record['name']
        scope = record['scope']

        # get full record so we can recursively delete
        record = self.get_record(name, scope)
        type = record['type']

        p = self._get_record_path(name, scope)
        self.connection.json().delete(self._get_data_namespace(), p)

        # rebuild now
        if rebuild:
            self._delete_index_record(record)

    def list_records(self, type=None, scope="/"):
        sp = self._get_scope_path(scope)

        records = self.connection.json().get(self._get_data_namespace(), Path(sp))[0]

        if type:
            filtered_records = {}
            for key in records:
                record = records[key]
                if record['type'] == type:
                    filtered_records[key] = record
            records = filtered_records

        return records

    ######
    def _start(self):
        # logging.info('Starting session {name}'.format(name=self.name))
        self._start_connection()

        # initialize registry data
        self._init_registry_namespace()

        # build search index on registry
        self._init_search_index()

        logging.info('Started registry {name}'.format(name=self.name))

    ###### save/load
    def dumps(self, output_string):
        records = self.get_records()
        return str(records)

    def dump(self, output_file):
        records = self.get_records()
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
        print(records)
        for record in records:
            self.register_record_json(record)

        # index registry
        self.build_index()


#######################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, default='REGISTRY', help='name of the registry')
    parser.add_argument('--id', type=str, default='default', help='id of the registry')
    parser.add_argument('--sid', type=str, help='short id (sid) of the registry')
    parser.add_argument('--cid', type=str, help='canonical id (cid) of the registry')
    parser.add_argument('--prefix', type=str, help='prefix for the canonical id of the registry')
    parser.add_argument('--suffix', type=str, help='suffix for the canonical id of the registry')
    parser.add_argument('--properties', type=str, help='properties in json format')
    parser.add_argument('--loglevel', default="INFO", type=str, help='log level')
    parser.add_argument('--add', type=str, default=None, help='json array of records to be add to the registry')
    parser.add_argument('--update', type=str, default=None, help='json array of records to be updated in the registry')
    parser.add_argument('--remove', type=str, default=None, help='json array of records names to be removed')
    parser.add_argument('--search', type=str, default=None, help='search registry with keywords')
    parser.add_argument('--type', type=str, default=None, help='limit to record type')
    parser.add_argument('--scope', type=str, default=None, help='limit to record scope')
    parser.add_argument('--page', type=int, default=0, help='search result page, default 0')
    parser.add_argument('--page_size', type=int, default=5, help='search result page size, default 5')
    parser.add_argument(
        '--list', type=bool, default=False, action=argparse.BooleanOptionalAction, help='list records in the registry'
    )
    parser.add_argument(
        '--approximate',
        type=bool,
        default=False,
        action=argparse.BooleanOptionalAction,
        help='use approximate (embeddings) search',
    )
    parser.add_argument(
        '--hybrid',
        type=bool,
        default=False,
        action=argparse.BooleanOptionalAction,
        help='use hybrid (keyword and approximate) search',
    )

    args = parser.parse_args()

    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())

    print(args)
    # set properties
    properties = {}
    p = args.properties
    if p:
        # decode json
        properties = json.loads(p)

    # create a registry
    registry = Registry(
        name=args.name,
        id=args.id,
        sid=args.sid,
        cid=args.cid,
        prefix=args.prefix,
        suffix=args.suffix,
        properties=properties,
    )

    #### LIST
    if args.list:
        # list the records in registry
        results = registry.list_records()
        logging.info(results)

    #### ADD
    if args.add:
        registry.loads(args.add)

        # list the registryrecords = json
        results = registry.list_records()
        logging.info(results)
        logging.info(registry.get_contents())

    #### UPDATE
    if args.update:
        records = json.loads(args.update)
        print(records)
        for record in records:
            registry.update_record_json(record)

        # index registry
        registry.build_index()

        # list the registry
        results = registry.list_records()
        logging.info(results)

    #### REMOVE
    if args.remove:
        records = json.loads(args.remove)
        print(records)
        for record in records:
            # deregister
            registry.deregister(record, rebuild=True)

        # list the registry
        results = registry.list_records()
        logging.info(results)

    #### SEARCH
    if args.search:
        keywords = args.search

        # search the registry
        results = registry.search_records(
            keywords,
            type=args.type,
            scope=args.scope,
            approximate=args.approximate,
            hybrid=args.hybrid,
            page=args.page,
            page_size=args.page_size,
        )

        logging.info(json.dumps(results, indent=4))
