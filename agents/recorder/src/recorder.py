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


    def default_processor(self, stream, id, event, value, tags=None, properties=None, worker=None):
        if event == 'EOS':
            # compute stream data
            l = 0
            if worker:
                data = worker.get_data(stream)[0]

                json_data = None

                if not json_data:
                    try:
                        json_data = json.loads(" ".join(data))
                        logging.info('Procecssing data {data}'.format(data=str(" ".join(data))))
                    except:
                        pass 

                if not json_data:
                    try:
                        json_data = ast.literal_eval(" ".join(data))
                        logging.info('Procecssing data {data}'.format(data=str(" ".join(data))))
                    except:
                        pass 

                if json_data:
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
                            result = json_utils.json_query(json_data, query, single=single)
                            worker.set_session_data(variable, result)

                            variables.append(variable)
                        
                        return variables, 'json', 'DATA'
                else:
                    logging.info('Unable to process data {data}'.format(data=str(" ".join(data))))

                
    
        elif event == 'BOS':
            # init stream to empty array
            if worker:
                worker.set_data(stream,[])
            pass
        elif event == 'DATA':
            # store data value
            logging.info(value)
            
            if worker:
                worker.append_data(stream, value)
    
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



