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
from utils import json_utils

import itertools
from tqdm import tqdm

###### Blue
from agent import Agent, AgentFactory
from session import Session
from message import Message, MessageType, ContentType, ControlCode


import ast

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


#######################
class RecorderAgent(Agent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "RECORDER"
        super().__init__(**kwargs)

    def _initialize_properties(self):
        super()._initialize_properties()

        # default properties
        listeners = {}
        default_listeners = {}
        listeners["DEFAULT"] = default_listeners

        self.properties['listens'] = listeners
        default_listeners['includes'] = ['JSON']
        default_listeners['excludes'] = [self.name]

        # recorder is an aggregator agent
        self.properties['aggregator'] = True 
        self.properties['aggregator.eos'] = 'NEVER'

        # recorder config
        records = []
        self.properties['records'] = records
        records.append({"variable":"all","query":"$","single":True})


    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        if message.isEOS():
            ## TODO: Verify and remove
            # if worker:
            #     processed = worker.get_data('processed')
            #     if processed:
            #         return 'EOS', None, None
            return None
        elif message.isBOS():
            pass
        elif message.isData():
            # store data value
            data = message.getData()

            # TODO: Record from other data types
            if message.getContentType() == ContentType.JSON:
                if 'records' in self.properties:
                    records = self.properties['records']
                    variables = []
                    for record in records:
                        variable = record['variable']
                        query = record['query']
                        single = False
                        if 'single' in record:
                            single = record['single']

                        # evaluate path on json_data
                        logging.info('Executing query {query}'.format(query=query))
                        result = None
                        try:
                            result = json_utils.json_query(data, query, single=single)
                        except:
                            pass 

                        if result:
                            worker.set_session_data(variable, result)
                            variables.append(variable)
                    
                    if len(variables) > 0:
                        ## TODO: Verify and remove
                        # set processed to true 
                        # worker.set_data('processed', True)

                        # output to stream
                        return variables

    
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="RECORDER", type=str)
    parser.add_argument('--session', type=str)
    parser.add_argument('--properties', type=str)
    parser.add_argument('--loglevel', default="INFO", type=str)
    parser.add_argument('--serve', type=str)
    parser.add_argument('--platform', type=str, default='default')
    parser.add_argument('--registry', type=str, default='default')
 
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
        platform = args.platform
        
        af = AgentFactory(agent_class=RecorderAgent, agent_name=args.serve, agent_registry=args.registry, platform=platform, properties=properties)
        af.wait()
    else:
        a = None
        session = None

        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = RecorderAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = RecorderAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()



