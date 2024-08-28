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


class OperatorRegistry(Registry):
    def __init__(self, name="OPERATOR_REGISTRY", id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):
        super().__init__(name=name, id=id, sid=sid, cid=cid, prefix=prefix, suffix=suffix, properties=properties)

    ###### initialization

    def _initialize_properties(self):
        super()._initialize_properties()

    ######### operator
    def add_operator(self, operator, created_by, description="", properties={}, rebuild=False):
        super().register_record(operator, "operator", "/", created_by=created_by, description=description, properties=properties, rebuild=rebuild)

    def update_operator(self, operator, description="", icon=None, properties={}, rebuild=False):
        super().update_record(operator, "operator", "/", description=description, icon=icon, properties=properties, rebuild=rebuild)

    def remove_operator(self, operator, rebuild=False):
        record = self.get_operator(operator)
        super().deregister(record, rebuild=rebuild)

    def get_operator(self, operator):
        return super().get_record(operator, '/')

    def get_operator_description(self, operator):
        return super().get_record_description(operator, '/')

    def set_operator_description(self, operator, description, rebuild=False):
        super().set_record_description(operator, '/', description, rebuild=rebuild)

    # operator properties
    def get_operator_properties(self, operator):
        return super().get_record_properties(operator, '/')

    def get_operator_property(self, operator, key):
        return super().get_record_property(operator, '/', key)

    def set_operator_property(self, operator, key, value, rebuild=False):
        super().set_record_property(operator, '/', key, value, rebuild=rebuild)

    def delete_operator_property(self, operator, key, rebuild=False):
        super().delete_record_property(operator, '/', key, rebuild=rebuild)

    # operator image (part of properties)
    def get_operator_image(self, operator):
        return self.get_operator_property(operator, 'image')

    def set_operator_image(self, operator, image, rebuild=False):
        self.set_operator_property(operator, 'image', image, rebuild=rebuild)


#######################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, default='OPERATOR_REGISTRY', help='name of the registry')
    parser.add_argument('--id', type=str, default='default', help='id of the registry')
    parser.add_argument('--sid', type=str, help='short id (sid) of the registry')
    parser.add_argument('--cid', type=str, help='canonical id (cid) of the registry')
    parser.add_argument('--prefix', type=str, help='prefix for the canonical id of the registry')
    parser.add_argument('--suffix', type=str, help='suffix for the canonical id of the registry')
    parser.add_argument('--properties', type=str, help='properties in json format')
    parser.add_argument('--loglevel', default="INFO", type=str, help='log level')
    parser.add_argument('--add', type=str, default=None, help='json array of operators to be add to the registry')
    parser.add_argument('--update', type=str, default=None, help='json array of operators to be updated in the registry')
    parser.add_argument('--remove', type=str, default=None, help='json array of operators names to be removed')
    parser.add_argument('--search', type=str, default=None, help='search registry with keywords')
    parser.add_argument('--type', type=str, default=None, help='search registry limited to operator metadata type [operator, input, output]')
    parser.add_argument('--scope', type=str, default=None, help='limit to scope')
    parser.add_argument('--page', type=int, default=0, help='search result page, default 0')
    parser.add_argument('--page_size', type=int, default=5, help='search result page size, default 5')
    parser.add_argument('--list', type=bool, default=False, action=argparse.BooleanOptionalAction, help='list operators in the registry')
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
    registry = OperatorRegistry(name=args.name, id=args.id, sid=args.sid, cid=args.cid, prefix=args.prefix, suffix=args.suffix, properties=properties)

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
        results = registry.search_records(keywords, type=args.type, scope=args.scope, approximate=args.approximate, hybrid=args.hybrid, page=args.page, page_size=args.page_size)

        logging.info(json.dumps(results, indent=4))
