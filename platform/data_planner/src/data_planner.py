###### OS / Systems
from curses import noecho
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/operator/')
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


###### Blue


class DataPlanner():
    def __init__(self, name="DATA_PLANNER", id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):
        
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

        self._start()   ###### initialization

    def _initialize_properties(self):
        super()._initialize_properties()

    def plan(input_data, task, context):
        return None
    
    def optimize(plan, budget):
        return None

    ######
    def _start_connection(self):
        host = self.properties['db.host']
        port = self.properties['db.port']

        self.connection = redis.Redis(host=host, port=port, decode_responses=True)
        
    def _start(self):
        super()._start()

        # logging.info('Starting session {name}'.format(name=self.name))
        self._start_connection()

        logging.info('Started data planner {name}'.format(name=self.name))


#######################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, default='DATA_PLANNER', help='name of the planner')
    parser.add_argument('--id', type=str, default='default', help='id of the planner')
    parser.add_argument('--sid', type=str, help='short id (sid) of the planner')
    parser.add_argument('--cid', type=str, help='canonical id (cid) of the planner')
    parser.add_argument('--prefix', type=str, help='prefix for the canonical id of the planner')
    parser.add_argument('--suffix', type=str, help='suffix for the canonical id of the planner')
    parser.add_argument('--properties', type=str, help='properties in json format')
    parser.add_argument('--loglevel', default="INFO", type=str, help='log level')

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

    # create a planner
    planner = DataPlanner(name=args.name, id=args.id, sid=args.sid, cid=args.cid, prefix=args.prefix, suffix=args.suffix, properties=properties)

  