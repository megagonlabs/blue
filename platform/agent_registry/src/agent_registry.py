###### OS / Systems
from curses import noecho
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/agent/')


###### 
import time
import argparse
import logging
import time
import uuid
import random

###### Parsers, Formats, Utils
import re
import csv
import json


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

###### Blue
from agent import Agent

r = redis.Redis(host="localhost", port=6379)

INDEX_NAME = "index"                              # Vector Index Name
DOC_PREFIX = "doc:"     

class AgentRegistry():
    def __init__(self, name, properties={}):

        self.name = name

        self._initialize(properties=properties)

        self._start()

    ###### initialization
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)


    def _initialize_properties(self):
        self.properties = {}

        # db connectivity
        self.properties['host'] = 'localhost'
        self.properties['port'] = 6379

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
        host = self.properties['host']
        port = self.properties['port']

        self.connection = redis.Redis(host=host, port=port, decode_responses=True)

    def _get_data_namespace(self):
        return "AGENT_REGISTRY" + ":" + self.name + ':DATA'

    def __get_json_value(self, value):
        if value is None:
            return None
        if type(value) is list:
            if len(value) == 0:
                return None
            else:
                return(value[0])
        else:
            return value

    def _init_agent_registry_namespace(self):
        # create registry-specific registry
        self.connection.json().set(self._get_data_namespace(), '$', {'agents':{}}, nx=True)


    def _init_search_index(self):

        # init embeddings model
        self._init_search_embeddings_model()

        index_name = self.name
        doc_prefix = 'doc:'

        vector_dimensions = self.properties['vector_dimensions']

        try:
            # check if index exists
            logging.info(self.connection.ft(index_name).info())
            logging.info('Search index ' + index_name + ' already exists.')
        except:
            logging.info('Creating search index...' + index_name)
            # schema
            schema = (
                # agent name
                TextField("name", weight=2.0),
                # description, input, output 
                TextField("type"), 
                # name of the field
                TextField("field"),
                # value of the field (text)
                TextField("value"),
                # embedding of the field value
                VectorField("vector",                  
                    "FLAT", {                          
                        "TYPE": "FLOAT32",             
                        "DIM": vector_dimensions,      
                        "DISTANCE_METRIC": "COSINE",   
                    }
                ),
            )

            # index definition
            definition = IndexDefinition(prefix=[doc_prefix], index_type=IndexType.HASH)

            # create index
            self.connection.ft(index_name).create_index(fields=schema, definition=definition)

            # report index info
            logging.info(self.connection.ft(index_name).info())

    def build_index(self):

        index_name = self.name 

        agent_records = self.list_agents()

        # instantiate a redis pipeline
        pipe = self.connection.pipeline()
        for name in agent_records:
            agent_record = agent_records[name]
            self._set_index_agent_record(agent_record, pipe=pipe)

        res = pipe.execute()

        # report index info
        logging.info(self.connection.ft(index_name).info())

    def _set_index_agent_record(self, agent_record, pipe=None):

        name = agent_record['name']

        # index description
        self._create_index_doc(name, 'description', 'description', agent_record['description'], pipe=pipe)

        # index input parameters
        inputs = agent_record['inputs']
        for param in inputs:
            self._create_index_doc(name, 'input', param, inputs[param], pipe=pipe)
        # index output parameters
        outputs = agent_record['outputs']
        for param in outputs:
            self._create_index_doc(name, 'input', param, outputs[param], pipe=pipe)

           
    def _create_index_doc(self, name, type, field, value, pipe=None):

        index_name = self.name 
        doc_prefix = 'doc:' 
 
        vector = self._compute_embedding_vector(value)

        doc = {
            'name': name,
            'type': type,
            'field': field,
            'value': value,
            'vector': vector
        }

        # define key
        doc_key = doc_prefix + ':' + name + ":" + type + ':' + field
        if pipe:
            pipe.hset(doc_key, mapping=doc)
        else:
            pipe = self.connection.pipeline()
            pipe.hset(doc_key, mapping=doc)
            res = pipe.execute()

    def _delete_index_agent_record(self, name, pipe=None):
        
        agent_record = self.get_agent(name)

         # delete description
        self._delete_index_doc(name, 'description', 'description', pipe=pipe)

        # delete input parameters
        inputs = agent_record['inputs']
        for param in inputs:
            self._delete_index_doc(name, 'input', param, pipe=pipe)
        # delete output parameters
        outputs = agent_record['outputs']
        for param in outputs:
            self._delete_index_doc(name, 'input', param, pipe=pipe)


    def _delete_index_doc(self, name, type, field, pipe=None):
        index_name = self.name 
        doc_prefix = 'doc:' 

        # define key
        doc_key = doc_prefix + ':' + name + ":" + type + ':' + field
        if pipe:
            pipe.hdel(doc_key, 1)
        else:
            pipe = self.connection.pipeline()
            pipe.hdel(doc_key, 1)
            res = pipe.execute()


    def search_agents(self, keywords, type=None, approximate=False, hybrid=False, page=0, page_size=5):
        
        index_name = self.name
        doc_prefix = 'doc:'

        q = None
        
        if hybrid:
            if type:
                q = "( (@type: " + type + ") $kw ) => [KNN " + str((page+1) * page_size) + " @vector $v as score]"
            else:
                q = "( $kw ) => [KNN " + str((page+1) * page_size) + " @vector $v as score]"
            
            query = (
                Query(q)
                .sort_by("score")
                .return_fields("id", "name", "type", "field", "score")
                .paging(page, page_size)
                .dialect(2)
            )

        else:
            if approximate:
                if type:
                    q = "( (@type: " + type + ") ) => [KNN " + str((page+1) * page_size) + " @vector $v as score]"
                else:
                    q = "( * ) => [KNN " + str((page+1) * page_size) + " @vector $v as score]"
                query = (
                    Query(q)
                    .sort_by("score")
                    .return_fields("id", "name", "type", "field", "score")
                    .paging(page, page_size)
                    .dialect(2)
                )

            else:
                if type:
                    q = "( (@type: " + type + ") $kw )"
                else:
                    q = "( $kw )"
                query = (
                    Query("$kw")
                    .return_fields("id", "name", "type", "field")
                    .paging(page, page_size)
                    .dialect(2)
                )

        

        query_params = {
            "kw": keywords,
            "v": self._compute_embedding_vector(keywords)
        }

        logging.info('searching: ' + keywords + ', ' + 'approximate=' + str(approximate) + ', ' + 'hybrid=' + str(hybrid))
        logging.info('using search query: ' + q)
        results = self.connection.ft(index_name).search(query, query_params).docs

        return results

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
        
        sentence = [ text ]
        embedding = self.embeddings_model.encode(sentence)[0]
        return embedding.astype(np.float32).tobytes()
    
    ###### registry functions
    def register_agent(self, name, description="", inputs={}, outputs={}, properties={}, image=None, rebuild=False):
        agent_record = {}
        agent_record['name'] = name
        agent_record['description'] = description
        agent_record['inputs'] = inputs
        agent_record['outputs'] = outputs

        agent_record['properties'] = properties
        
        agent_record['image'] = image

        # create agent record on the registry name space
        self.connection.json().set(self._get_data_namespace(), '$.agents.' + name, agent_record)

        # rebuild now
        if rebuild:
            self._set_index_agent_record(agent_record)

    def register_agent_json(self, agent_record):
        name = None
        if 'name' in agent_record:
            name = agent_record['name']

        description = ""
        if 'description' in agent_record:
            description = agent_record['description']

        inputs = {}
        if 'inputs' in agent_record:
            inputs = agent_record['inputs']

        outputs = {}
        if 'outputs' in agent_record:
            outputs = agent_record['outputs']

        properties = {}
        if 'properties' in agent_record:
            properties = agent_record['properties']

        image = None
        if 'image' in agent_record:
            image = agent_record['image']

        self.register_agent(name, description=description, inputs=inputs, outputs=outputs, properties=properties, image=image)


    def get_agent(self, name):
        agent_record =  self.connection.json().get(self._get_data_namespace(), Path('$.agents.' + name))
        return self.__get_json_value(agent_record)
    
    def get_agent_data(self, name, key):
        value =  self.connection.json().get(self._get_data_namespace(), Path('$.agents.' + name + '.' + key))
        return self.__get_json_value(value)

    def set_agent_data(self, name, key, value, rebuild=False):
        self.connection.json().set(self._get_data_namespace(), '$.agents.' + name + '.' + key, value)

        # rebuild now
        if rebuild:
            agent_record = self.get_agent_data(name)
            self._set_index_agent_record(agent_record)

    def get_agent_description(self, name):
        return self.get_agent_data(name, 'description')

    def set_agent_description(self, name, description, rebuild=False):
        self.set_agent_data(name, 'description', description, rebuild=rebuild)


    def get_agent_inputs(self, name):
        return self.get_agent_data(name, 'inputs')

    def get_agent_input(self, name, parameter):
        return self.get_agent_data(name, 'inputs' + '.' + parameter)

    def set_agent_inputs(self, name, inputs, rebuild=False):
        self.set_agent_data(name, 'inputs', inputs, rebuild=rebuild)

    def set_agent_input(self, name, parameter, description, rebuild=False):
        self.set_agent_data(name, 'inputs' + '.' + parameter, description, rebuild=rebuild)

    def get_agent_outputs(self, name):
        return self.get_agent_data(name, 'outputs')

    def get_agent_output(self, name, parameter):
        return self.get_agent_data(name, 'outputs' + '.' + parameter)

    def set_agent_outputs(self, name, outputs, rebuild=False):
        self.set_agent_data(name, 'outputs', outputs, rebuild=rebuild)

    def set_agent_output(self, name, parameter, description, rebuild=False):
        self.set_agent_data(name, 'outputs' + '.' + parameter, description, rebuild=rebuild)


    def get_agent_properties(self, name):
        return self.get_agent_data(name, 'properties')

    def get_agent_property(self, name, key):
        return self.get_agent_data(name, 'properties' + '.' + key)

    def set_agent_property(self, name, key, value, rebuild=False):
        self.set_agent_data(name, 'properties' + '.' + key, value, rebuild=rebuild)


    def get_agent_image(self, name):
        return self.get_agent_data(name, 'image')

    def set_agent_image(self, name, image, rebuild=False):
        self.set_agent_data(name, 'image', image, rebuild=rebuild)
    
   

    def deregister(self, name, rebuild=False):
        self.connection.json().delete(self._get_data_namespace(), '$.agents.' + name)

        # rebuild now
        if rebuild:
            self._delete_index_agent_record(name)

    def list_agents(self):
        agent_records =  self.connection.json().get(self._get_data_namespace(), Path('$.agents'))
        return self.__get_json_value(agent_records)

    ######
    def _start(self):
        # logging.info('Starting session {name}'.format(name=self.name))
        self._start_connection()
        
         # initialize registry data
        self._init_agent_registry_namespace()

        # build search index on agent registry
        self._init_search_index()

        logging.info('Started agent registry {name}'.format(name=self.name))




#######################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, default='default', help='name of the agent registry')
    parser.add_argument('--properties', type=str, help='properties in json format')
    parser.add_argument('--loglevel', default="INFO", type=str, help='log level')
    parser.add_argument('--add', type=str, default=None, help='json array of agents to be add to the registry')
    parser.add_argument('--remove', type=str, default=None, help='json array of agents names to be removed')
    parser.add_argument('--search', type=str, default=None, help='search registry with keywords')
    parser.add_argument('--type', type=str, default=None, help='search registry limited to agent metadata type [description, input, output]')
    parser.add_argument('--page', type=int, default=0, help='search result page, default 0')
    parser.add_argument('--page_size', type=int, default=5, help='search result page size, default 5')
    parser.add_argument('--list', type=bool, default=False, action=argparse.BooleanOptionalAction, help='list agents in the registry')
    parser.add_argument('--approximate', type=bool, default=False, action=argparse.BooleanOptionalAction, help='use approximate (embeddings) search')
    parser.add_argument('--hybrid', type=bool, default=False, action=argparse.BooleanOptionalAction, help='use hybrid (keyword and approximate) search')
 
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

    # create an agent registry
    registry = AgentRegistry(args.name, properties=properties)

    #### LIST
    if args.list:
        # list the agent registry
        results = registry.list_agents()
        logging.info(results)

    #### ADD
    if args.add:
        agents = json.loads(args.add)
        print(agents)
        for agent in agents:
            # register agents
            # example: {'name': 'TitleRecommender', 'description': 'Recommends next title given a title', 'image': 'blue-agent-simple_graph:latest'}
            registry.register_agent_json(agent)
    
        # index registry
        registry.build_index()

        # list the agent registry
        results = registry.list_agents()
        logging.info(results)

    #### REMOVE
    if args.remove:
        agents = json.loads(args.remove)
        print(agents)
        for agent in agents:
            # deregister
            registry.deregister(agent)

        # index registry
        registry.build_index()

        # list the agent registry
        results = registry.list_agents()
        logging.info(results)


    #### SEARCH
    if args.search:
        keywords = args.search

        # search the registry
        results = registry.search_agents(keywords, type=args.type, approximate=args.approximate, hybrid=args.hybrid, page=args.page, page_size=args.page_size)
        logging.info(results)

   
   

  
   