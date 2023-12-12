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

        # index properties
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
            logging.info('Search index ' + self.name + ' already exists.')
        except:
            logging.info('Creating search index...' + index_name)
            # schema
            schema = (
                TextField("name", weight=2.0),
                TextField("description"),
                VectorField("description_vector",                  
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
        doc_prefix = 'doc:'

        agent_records = self.list_agents()

        # instantiate a redis pipeline
        pipe = self.connection.pipeline()
        for k in agent_records:
            agent_record = agent_records[k]
            self._set_index_agent_record(agent_record, pipe=pipe)

        res = pipe.execute()

        # report index info
        logging.info(self.connection.ft(index_name).info())

    def _set_index_agent_record(self, agent_record, pipe=None):

        name = agent_record['name']
        description = agent_record['description']
        description_vector = self._compute_embedding_vector(description)


        doc = {
            'name': name,
            'description': description,
            'description_vector': description_vector
        }

        # define key
        key = f"doc:{name}"
        if pipe:
            pipe.hset(key, mapping=doc)
        else:
            pipe = self.connection.pipeline()
            pipe.hset(key, mapping=doc)
            res = pipe.execute()


    def _delete_index_agent_record(self, name, pipe=None):
        
        # define key
        key = f"doc:{name}"
        if pipe:
            pipe.hdel(key, 1)
        else:
            pipe = self.connection.pipeline()
            pipe.hdel(key, 1)
            res = pipe.execute()


    def search_agents(self, keywords, approximate=False, hybrid=False):
        
        index_name = self.name
        doc_prefix = 'doc:'

        logging.info('searching: ' + keywords + ', ' + 'approximate=' + str(approximate) + ', ' + 'hybrid=' + str(hybrid))
        
        if hybrid:
            query = (
                Query("( $kw ) => [KNN 2 @description_vector $v as score]")
                .sort_by("score")
                .return_fields("id", "name", "score")
                .paging(0, 2)
                .dialect(2)
            )

            query_params = {
                "kw": keywords,
                "v": self._compute_embedding_vector(keywords)
            }

        else:
            if approximate:
                query = (
                    Query(" * => [KNN 2 @description_vector $v as score]")
                    .sort_by("score")
                    .return_fields("id", "name", "score")
                    .paging(0, 2)
                    .dialect(2)
                )

                query_params = {
                    "kw": keywords,
                    "v": self._compute_embedding_vector(keywords)
                }

            else:
                query = (
                    Query("$kw")
                    .return_fields("id", "name")
                    .paging(0, 2)
                    .dialect(2)
                )

                query_params = {
                    "kw": keywords,
                    "v": self._compute_embedding_vector(keywords)
                }

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
    def register_agent(self, name, description="", properties={}, image=None, rebuild=False):
        agent_record = {}
        agent_record['name'] = name
        agent_record['description'] = description
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

        properties = {}
        if 'properties' in agent_record:
            properties = agent_record['properties']

        image = None
        if 'image' in agent_record:
            image = agent_record['image']

        self.register_agent(name, description=description, properties=properties, image=image)


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
    parser.add_argument('--name', type=str, default='default', description='name of the agent registry')
    parser.add_argument('--properties', type=str, description='properties in json format')
    parser.add_argument('--loglevel', default="INFO", type=str, description='log level')
    parser.add_argument('--add', type=str, default=None, description='json array of agents to be add to the registry  (e.g. [{"name": "TitleRecommender", "description": "Recommends next title given a title", "image": "blue-agent-simple_graph:latest"}]')
    parser.add_argument('--remove', type=str, default=None, description='json array of agents names to be removed')
    parser.add_argument('--search', type=str, default=None, description='search registry with keywords')
    parser.add_argument('--list', type=bool, default=False, action=argparse.BooleanOptionalAction, description='list agents in the registry')
    parser.add_argument('--approximate', type=bool, default=False, action=argparse.BooleanOptionalAction, description='use approximate (embeddings) search')
    parser.add_argument('--hybrid', type=bool, default=False, action=argparse.BooleanOptionalAction, description='use hybrid (keyword and approximate) search')
 
    args = parser.parse_args()
   
    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())


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
        results = registry.search_agents(keywords, approximate=args.approximate, hybrid=args.hybrid)
        logging.info(results)

   
   

  
   