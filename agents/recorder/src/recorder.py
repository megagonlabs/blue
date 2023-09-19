###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/shared/')

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
from agent import Agent
from session import Session

import ast

# set log level
logging.getLogger().setLevel(logging.INFO)

#######################
class RecorderAgent(Agent):
    def __init__(self, session=None, input_stream=None, processor=None, properties={}):
        super().__init__("RECORDER", session=session, input_stream=input_stream, processor=processor, properties=properties)

    def _initialize_properties(self):
        super()._initialize_properties()

        # default properties
        listeners = {}
        self.properties['listens'] = listeners
        listeners['includes'] = ['JSON']
        listeners['excludes'] = [self.name]

        # recorder config
        records = []
        self.properties['records'] = records
        records.append({"variable":"all","query":"$","single":True})


    def default_processor(self, stream, id, label, data, dtype=None, tags=None, properties=None, worker=None):
        if label == 'EOS':
            if worker:
                processed = worker.get_data('processed')
                if processed:
                    return 'EOS', None, None
            return None
        elif label == 'BOS':
            pass
        elif label == 'DATA':
            # store data value
            logging.info(data)
            logging.info(type(data))
            logging.info(dtype)
            
            # TODO: Record from other data types
            if dtype == 'json':
            
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
                        # set processed to true 
                        worker.set_data('processed', True)

                        # output to stream
                        return 'DATA', variables, 'json'

    
        return None

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
        a = RecorderAgent(session=session, properties=properties)
    elif args.input_stream:
        # no session, work on a single input stream
        a = RecorderAgent(input_stream=args.input_stream, properties=properties)
    else:
        # create a new session
        a = RecorderAgent(properties=properties)
        a.start_session()

    # wait for session
    session.wait()



