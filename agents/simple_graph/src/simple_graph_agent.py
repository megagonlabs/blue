
import sentence_transformers 
import embeddings 
from embeddings import * 


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

# set log level
logging.getLogger().setLevel(logging.INFO)

#######################
class GraphAgent(Agent):
    def __init__(self, session=None, input_stream=None, processor=None, properties={}):
        super().__init__("GRAPH", session=session, input_stream=input_stream, processor=processor, properties=properties)


    def _initialize_properties(self):
        super()._initialize_properties()

        # default properties
        listeners = {}
        self.properties['listens'] = listeners
        listeners['includes'] = ['RECORDER']
        listeners['excludes'] = [self.name]

        ### default tags to tag output streams
        tags = []
        self.properties['tags'] = ['JSON']


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
            # check if title is recorded
            variables = data
            variables = set(variables) 

            if 'title' in variables:
                if worker:
                    title = worker.get_session_data('title')

                    recommendations = get_embeddings(title)

                    logging.info("recommended titles: {recommendations}".format(recommendations=recommendations))
                
                    # set processed to true
                    worker.set_data('processed', True)
                    
                    # output to stream
                    return "DATA", { "title_recommendations": recommendations }, "json", True
        
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
        a = GraphAgent(session=session, properties=properties)
    elif args.input_stream:
        # no session, work on a single input stream
        a = GraphAgent(input_stream=args.input_stream,properties=properties)
    else:
        # create a new session
        a = GraphAgent(properties=properties)
        a.start_session()

    # wait for session
    session.wait()



