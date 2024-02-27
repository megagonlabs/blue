###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/agent/')
sys.path.append('./lib/apicaller/')
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

import itertools
from tqdm import tqdm

###### Communication
import asyncio
from websockets.sync.client import connect


###### Blue
from agent import Agent
from api_agent import APIAgent
from session import Session
from rpc import RPCServer

###### Agent Specific
import sqlvalidator


# set log level
logging.getLogger().setLevel(logging.INFO)

class PostgresAgent(APIAgent):
    def __init__(self, name="POSTGRES", session=None, input_stream=None, processor=None, properties={}):
        super().__init__(name, session=session, input_stream=input_stream, processor=processor, properties=properties)

    def _initialize_properties(self):
        super()._initialize_properties()

        # default properties
        self.properties['postgres.service'] = "ws://localhost:8004"

        self.properties['postgres.host'] = 'localhost'
        self.properties['postgres.port'] = 5432
        self.properties['postgres.database'] = 'default'
        self.properties['input_json'] = None 
        self.properties['input_context'] = None 
        self.properties['input_context_field'] = None 
        self.properties['input_field'] = 'query'
        self.properties['input_template'] = 'select row_to_json(row) from ({input}) row;'
        self.properties['output_path'] = '$.results'
   
    def validate_input(self, input_data):
        isValid = False
        try:
            sql_query = sqlvalidator.parse(input_data)
            isValid = sql_query.is_valid()
        except:
            logging.info('Error validating SQL query :{query}'.format(query=input_data))
            
        return isValid


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="POSTGRES", type=str)
    parser.add_argument('--session', type=str)
    parser.add_argument('--input_stream', type=str)
    parser.add_argument('--properties', type=str)
    parser.add_argument('--loglevel', default="INFO", type=str)
    parser.add_argument('--serve', default=False, action=argparse.BooleanOptionalAction)
 
    args = parser.parse_args()
   
    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())

    # set properties
    properties = {}
    p = args.properties
    if p:
        # decode json
        properties = json.loads(p)
    
    if args.serve:
        # launch agent with parameters, start session
        def launch(*args, **kwargs):
            logging.info("Launching UserAgent...")
            logging.info(kwargs)
            agent = PostgresAgent(*args, **kwargs)
            session = agent.start_session()
            logging.info("Started session: " + session.name)
            logging.info("Launched.")
            return session.name

        # launch agent with parameters, join session in keyword args (session=)
        def join(*args, **kwargs):
            logging.info("Launching UserAgent...")
            logging.info(kwargs)
            agent = PostgresAgent(*args, **kwargs)
            logging.info("Joined session: " + kwargs['session'])
            logging.info("Launched.")
            return kwargs['session']

        # run rpc server
        rpc = RPCServer(args.name, properties=properties)
        rpc.register(launch)
        rpc.register(join)
        rpc.run()
    else:
        a = None
        session = None
        if args.session:
            # join an existing session
            session = Session(args.session)
            a = PostgresAgent(name=args.name, session=session, properties=properties)
        elif args.input_stream:
            # no session, work on a single input stream
            a = PostgresAgent(name=args.name, input_stream=args.input_stream, properties=properties)
        else:
            # create a new session
            a = PostgresAgent(name=args.name, properties=properties)
            session = a.start_session()

        # wait for session
        if session:
            session.wait()