
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


    def _initialize_properties(self):
        super()._initialize_properties()

        # default properties
        listeners = {}
        self.properties['listens'] = listeners
        listeners['includes'] = ['RECORDER']
        listeners['excludes'] = [self.name]


    def default_processor(self, stream, id, label, data, dtype=None, tags=None, properties=None, worker=None):

        if label == 'EOS':
            return 'EOS', None, None
        elif label == 'BOS':
            pass
        elif label == 'DATA':
            pass
            # check if title is recorded
            variables = json.loads(data)
            variables = set(variables) 

            if 'title' in variables:
                if worker:
                    title = worker.get_session_data('title')[0]

                    recommendations = get_embeddings(title)

                    logging.info("recommended titles: {recommendations}".format(recommendations=recommendations))
                
                    # set top recommendation to stream
                    if len(recommendations) > 0:
                        top_recommendation = recommendations 
                        worker.set_session_data("title_recommendation", recommendations[0])

                    # output to stream
                    json_data = json.dumps({"top_recommended_titles": recommendations})
                    return json_data, "json"
        
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



