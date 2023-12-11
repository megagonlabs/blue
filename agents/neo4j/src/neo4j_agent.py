###### OS / Systems
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
from utils import json_utils

import itertools
from tqdm import tqdm

###### Communication
import asyncio
from websockets.sync.client import connect


###### Blue
from agent import Agent
from api_agent import APIAgent
from session import Session

###### Agent Specific


# set log level
logging.getLogger().setLevel(logging.INFO)

class NEO4JAgent(APIAgent):
    def __init__(self, session=None, input_stream=None, processor=None, properties={}):
        super().__init__("NEO4J", session=session, input_stream=input_stream, processor=processor, properties=properties)

    def _initialize_properties(self):
        super()._initialize_properties()

        # default properties
        self.properties['neo4j.service'] = "ws://localhost:8005"

        self.properties['neo4j.host'] = 'bolt://localhost'
        self.properties['neo4j.port'] = 7687
        self.properties['input_json'] = None 
        self.properties['input_context'] = None 
        self.properties['input_context_field'] = None 
        self.properties['input_field'] = 'query'
        self.properties['output_path'] = '$.results'

        listeners = {}
        self.properties['listens'] = listeners
        listeners['includes'] = ['CYPHER']
        listeners['excludes'] = [self.name]

        ### default tags to tag output streams
        tags = []
        self.properties['tags'] = ['JSON']

   
    def validate_input(self, input_data):
        # TODO
        isValid = True
            
        return isValid


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--session', type=str)
    parser.add_argument('--input_stream', type=str)
    parser.add_argument('--properties', type=str)
    parser.add_argument('--loglevel', default="INFO", type=str)
 
    args = parser.parse_args()

     # set logging
    logging.getLogger().setLevel(args.loglevel.upper())

    session = None
    a = None

    # set properties
    properties = {}
    p = args.properties


    if p:
        # decode json
        properties = json.loads(p)
    
    if args.session:
        # join an existing session
        session = Session(args.session)
        a = NEO4JAgent(session=session, properties=properties)
    elif args.input_stream:
        # no session, work on a single input stream
        a = NEO4JAgent(input_stream=args.input_stream, properties=properties)
    else:
        # create a new session
        a = NEO4JAgent(properties=properties)
        a.start_session()

    # wait for session
    session.wait()