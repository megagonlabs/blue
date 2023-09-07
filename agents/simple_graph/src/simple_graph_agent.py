
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


    def default_processor(self, sream, id, event, value, tags=None, properties=None, worker=None):
        if event == 'EOS':
            # compute stream data
            l = None
            if worker:
                stream_data = worker.get_data('stream')
                stream_data = stream_data[0]
                stream_data = " ".join(stream_data)
                l = get_embeddings (stream_data)
            time.sleep(4)
            
            # output to stream
            return_object = json.dumps({"top_recommended_jobs": l })
            print ("~~~~", return_object)
            return return_object
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



