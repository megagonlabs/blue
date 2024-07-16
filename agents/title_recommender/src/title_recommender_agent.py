
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
from agent import Agent, AgentFactory
from session import Session


# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


#######################
class TitleRecommenderAgent(Agent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "TITLERECOMMENDER"
        super().__init__(**kwargs)

    def _initialize_properties(self):
        super()._initialize_properties()

        # default properties
        listeners = {}
        default_listeners = {}
        listeners["DEFAULT"] = default_listeners
        self.properties['listens'] = listeners
        default_listeners['includes'] = ['RECORDER']
        default_listeners['excludes'] = [self.name]

        ### default tags to tag output streams
        tags = {}
        default_tags = ['JSON']
        tags["DEFAULT"] = default_tags
        self.properties['tags'] = tags


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
    parser.add_argument('--name', default="TITLERECOMMENDER", type=str)
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
        
        af = AgentFactory(agent_class=TitleRecommenderAgent, agent_name=args.serve, agent_registry=args.registry, platform=platform, properties=properties)
        af.wait()
    else:
        a = None
        session = None

        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = TitleRecommenderAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = TitleRecommenderAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()



