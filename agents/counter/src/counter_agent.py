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
from message import Message, MessageType, ContentType, ControlCode


# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


#######################
class CounterAgent(Agent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "COUNTER"
        super().__init__(**kwargs)

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        if message.isEOS():
            # get all data received from stream
            stream_data = ""
            if worker:
                stream_data = worker.get_data('stream')
            
            # output to stream
            output_data = len(stream_data)
            return output_data
        
        elif message.isBOS():
            # init stream to empty array
            if worker:
                worker.set_data('stream',[])
            pass
        elif message.isData():
            # store data value
            data = message.getData()
            logging.info(data)
            
            if worker:
                worker.append_data('stream', data)
    
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="COUNTER", type=str)
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
        
        af = AgentFactory(_class=CounterAgent, _name=args.serve, _registry=args.registry, platform=platform, properties=properties)
        af.wait()
    else:
        a = None
        session = None

        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = CounterAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = CounterAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()


