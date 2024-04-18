
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
from rpc import RPCServer

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


#######################
class TitleRecommenderAgent(Agent):
    def __init__(self, name="TITLERECOMMENDER", session=None, input_stream=None, processor=None, properties={}):
        super().__init__(name, session=session, input_stream=input_stream, processor=processor, properties=properties)


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
    parser.add_argument('--name', default="TITLERECOMMENDER", type=str)
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
            logging.info("Launching TitleRecommenderAgent...")
            logging.info(kwargs)
            agent = TitleRecommenderAgent(*args, **kwargs)
            session = agent.start_session()
            logging.info("Started session: " + session.name)
            logging.info("Launched.")
            return session.name

        # launch agent with parameters, join session in keyword args (session=)
        def join(*args, **kwargs):
            logging.info("Launching TitleRecommenderAgent...")
            logging.info(kwargs)
            agent = TitleRecommenderAgent(*args, **kwargs)
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
            a = TitleRecommenderAgent(name=args.name, session=session, properties=properties)
        elif args.input_stream:
            # no session, work on a single input stream
            a = TitleRecommenderAgent(name=args.name, input_stream=args.input_stream, properties=properties)
        else:
            # create a new session
            a = TitleRecommenderAgent(name=args.name, properties=properties)
            session = a.start_session()

        # wait for session
        if session:
            session.wait()



