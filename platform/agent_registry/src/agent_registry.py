###### OS / Systems
from curses import noecho
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/platform/')


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

###### Blue
from registry import Registry


class AgentRegistry(Registry):
    def __init__(self, name, properties={}):
        super().__init__(name, properties=properties)
       

    ###### initialization


    def _initialize_properties(self):
        super()._initialize_properties()

        # registry type
        self.properties['type'] = "agent"

    ######### agent
    def add_agent(self, agent, description="", properties={}, rebuild=False):
        super().register_record(agent, "agent", "/", description=description, properties=properties, rebuild=rebuild)

    def update_agent(self, agent, description="", properties={}, rebuild=False):
        super().update_record(agent, "agent", "/", description=description, properties=properties, rebuild=rebuild)

    def remove_agent(self, agent, rebuild=False):
        record = self.get_agent(agent)
        super().deregister(record, rebuild=rebuild)

    def get_agent(self, agent):
        return super().get_record(agent, '/')

    def get_agent_description(self, agent):
        return super().get_record_description(agent, '/')

    def set_agent_description(self, agent, description, rebuild=False):
        super().set_record_description(agent, '/', description, rebuild=rebuild)

    # agent properties
    def get_agent_properties(self, agent):
        return super().get_record_properties(agent, '/')

    def get_agent_property(self, agent, key):
        return super().get_record_property(agent, '/', key)

    def set_agent_property(self, agent, key, value, rebuild=False):
        super().set_record_property(agent, '/', key, value, rebuild=rebuild)

    def delete_agent_property(self, agent, key, rebuild=False):
        super().delete_record_property(agent, '/', key, rebuild=rebuild)

    # agent image (part of properties)
    def get_agent_image(self, agent):
        return self.get_agent_property(agent, 'image')

    def set_agent_image(self, agent, image, rebuild=False):
        self.set_agent_property(agent, 'image', image, rebuild=rebuild)


    ######### agent input and output parameters
    def add_agent_input(self, agent, parameter, description="", properties={}, rebuild=False):
        super().register_record(parameter, "input", "/"+agent, description=description, properties=properties, rebuild=rebuild)

    def update_agent_input(self, agent, parameter, description="", properties={}, rebuild=False):
        super().update_record(parameter, "input", "/"+agent, description=description, properties=properties, rebuild=rebuild)

    def remove_agent_input(self, agent, parameter, rebuild=False):
        record = self.get_agent_input(agent, parameter)
        super().deregister(record, rebuild=rebuild)

    def get_agent_inputs(self, agent):
        super().get_record_contents(agent, '/', type='input')

    def get_agent_input(self, agent, parameter):
        return super().get_record_content(agent, '/', parameter, type='input')


    def set_agent_input(self, agent, parameter, description, properties={}, rebuild=False):
        super().register_record(parameter, 'input', '/'+agent, description=description, properties=properties, rebuild=rebuild)

    def del_agent_input(self, agent, parameter, rebuild=False):
        record = self.get_agent_input(agent, parameter)
        super().deregister(record, rebuild=rebuild)


    def add_agent_output(self, agent, parameter, description="", properties={}, rebuild=False):
        super().register_record(parameter, "output", "/"+agent, description=description, properties=properties, rebuild=rebuild)

    def update_agent_output(self, agent, parameter, description="", properties={}, rebuild=False):
        super().update_record(parameter, "output", "/"+agent, description=description, properties=properties, rebuild=rebuild)

    def remove_agent_output(self, agent, parameter, rebuild=False):
        record = self.get_agent_output(agent, parameter)
        super().deregister(record, rebuild=rebuild)

    def get_agent_outputs(self, agent):
        super().get_record_contents(agent, '/', type='output')

    def get_agent_output(self, agent, parameter):
        return super().get_record_content(agent, '/', parameter, type='output')


    def set_agent_output(self, agent, parameter, description, rebuild=False):
        super().register_record(parameter, 'output', '/'+agent, description=description, properties=properties, rebuild=rebuild)

    def del_agent_output(self, agent, parameter, rebuild=False):
        record = self.get_agent_output(agent, parameter)
        super().deregister(self, record, rebuild=rebuild)

 
#######################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, default='default', help='name of the agent registry')
    parser.add_argument('--properties', type=str, help='properties in json format')
    parser.add_argument('--loglevel', default="INFO", type=str, help='log level')
    parser.add_argument('--add', type=str, default=None, help='json array of agents to be add to the registry')
    parser.add_argument('--update', type=str, default=None, help='json array of agents to be updated in the registry')
    parser.add_argument('--remove', type=str, default=None, help='json array of agents names to be removed')
    parser.add_argument('--search', type=str, default=None, help='search registry with keywords')
    parser.add_argument('--type', type=str, default=None, help='search registry limited to agent metadata type [agent, input, output]')
    parser.add_argument('--scope', type=str, default=None, help='limit to scope')
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

    # create a registry
    registry = AgentRegistry(args.name, properties=properties)

    #### LIST
    if args.list:
        # list the records in registry
        results = registry.list_records()
        logging.info(results)

    #### ADD
    if args.add:
        records = json.loads(args.add)
        print(records)
        for record in records:
            registry.register_record_json(record)
    
        # index registry
        registry.build_index()

        # list the registry
        results = registry.list_records()
        logging.info(results)

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
        results = registry.search_records(keywords, type=args.type, scope=args.scope, approximate=args.approximate, hybrid=args.hybrid, page=args.page, page_size=args.page_size)
    
        logging.info(json.dumps(results, indent=4))
