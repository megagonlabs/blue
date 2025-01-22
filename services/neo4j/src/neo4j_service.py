###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/service/')
sys.path.append('./lib/platform/')
sys.path.append('./lib/utils/')

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
from utils import string_utils
import copy

import itertools
from tqdm import tqdm

###### Communication
import asyncio
from websockets.sync.client import connect


###### Blue
from service import Service

##### Agent specifc
from neo4j_connection import NEO4J_Connection

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")

class NEO4JService(Service):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "NEO4J"
        super().__init__(**kwargs)

    def default_handler(self, message, properties=None, websocket=None):
        query = message['query']

        # Connect to database 
        host = message['host']
        user = message['user']
        pwd = message['password']
        connection = NEO4J_Connection(host, user, pwd)

        # Execute query, fetch all data
        data = connection.run_query(query)

        # get results
        results = data

        logging.info(results)
        
        response = {}
        response['results'] = results

        return response

if __name__ == "__main__":
    logging.info('starting....')
 

    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str, default="NEO4J")
    parser.add_argument("--properties", type=str)
    parser.add_argument("--loglevel", default="INFO", type=str)
    parser.add_argument("--platform", type=str, default="default")

    args = parser.parse_args()

    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())

    # set properties
    properties = {}
    p = args.properties

    print(args)
    if p:
        # decode json
        properties = json.loads(p)
        print("properties:")
        print(json.dumps(properties, indent=3))
        print("---")

    # create service
    prefix = "PLATFORM:" + args.platform + ":SERVICE"
    s = NEO4JService(name=args.name, prefix=prefix, properties=properties)

    # run
    asyncio.run(s.start_listening_socket())
    