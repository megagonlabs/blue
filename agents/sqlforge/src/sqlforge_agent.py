###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/agent/')
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

import itertools
from tqdm import tqdm

###### Blue
from agent import Agent
from session import Session
from rpc import RPCServer

# set log level
logging.getLogger().setLevel(logging.INFO)

#######################
class SQLForgeAgent(Agent):
    def __init__(self, name="SQLFORGE", session=None, input_stream=None, processor=None, properties={}):
        super().__init__(name, session=session, input_stream=input_stream, processor=processor, properties=properties)


    def default_processor(self, stream, id, label, data, dtype=None, tags=None, properties=None, worker=None):
        if label == 'EOS':
            # compute stream data
            text_query = ""
            if worker:
                text_query = " ".join(worker.get_data('text_query'))

            logging.info("Translating text query: " + text_query)
            #TODO: Do SQL translation here
            sql_query = self.compute_sql_query(text_query)

            # output to stream
            return sql_query
        elif label == 'BOS':
            # init stream to empty array
            if worker:
                worker.set_data('text_query',[])
            pass
        elif label == 'DATA':
            # store data value
            logging.info(data)
            
            if worker:
                worker.append_data('text_query', data)
    
        return None

    def compute_sql_query(self, text_query):
        # TODO: Do SQL translation here
        return "SELECT * FROM CITY"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--session', type=str)
    parser.add_argument('--input_stream', type=str)
    parser.add_argument('--properties', type=str)
    parser.add_argument('--loglevel', default="INFO", type=str)
 
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
            agent = SQLForgeAgent(*args, **kwargs)
            session = agent.start_session()
            logging.info("Started session: " + session.name)
            logging.info("Launched.")
            return session.name

        # launch agent with parameters, join session in keyword args (session=)
        def join(*args, **kwargs):
            logging.info("Launching UserAgent...")
            logging.info(kwargs)
            agent = SQLForgeAgent(*args, **kwargs)
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
            a = SQLForgeAgent(name=args.name, session=session, properties=properties)
        elif args.input_stream:
            # no session, work on a single input stream
            a = SQLForgeAgent(name=args.name, input_stream=args.input_stream, properties=properties)
        else:
            # create a new session
            a = SQLForgeAgent(name=args.name, properties=properties)
            session = a.start_session()

        # wait for session
        if session:
            session.wait()



