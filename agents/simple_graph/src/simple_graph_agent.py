
import sentence_transformers 
import embeddings 
from embeddings import * 


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


    def default_processor(self, id, event, value, properties=None, worker=None):
        if event == 'EOS':
            # compute stream data
            l = 0
            if worker:
                stream_data = worker.get_data('stream')
                stream_data = stream_data[0]
                #l = worker.get_data_len('stream') # TODO 
                l = get_embeddings (stream_data)
            time.sleep(4)
            
            # output to stream
            #l = l[0]
            return l
        elif event == 'BOS':
            # init stream to empty array
            if worker:
                worker.set_data('stream',[])
            pass
        elif event == 'DATA':
            # store data value
            logging.info(value)
            
            if worker:
                worker.append_data('stream', value)
    
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--session', type=str)
    parser.add_argument('--input_stream', type=str)
    parser.add_argument('--properties', type=str)
    
    args = parser.parse_args()

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



