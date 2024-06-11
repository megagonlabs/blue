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
class UserAgent(Agent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "USER"
        super().__init__(**kwargs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="USER", type=str)
    parser.add_argument('--session', type=str)
    parser.add_argument('--text', type=str)
    parser.add_argument('--interactive', type=bool, default=False, action=argparse.BooleanOptionalAction, help="input text interactively (default False)")
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
        
        af = AgentFactory(agent_class=UserAgent, agent_name=args.serve, agent_registry=args.registry, platform=platform, properties=properties)
        af.wait()
    else:
        a = None
        session = None

        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = UserAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = UserAgent(name=args.name, session=session, properties=properties)


        # write to user stream
        while (True):
            text = ""
            if args.interactive:
                text = input('Enter Text:')
            else:
                text = args.text

            # interact 
            a.interact(text)

            if not args.interactive:
                break

        # wait for session
        if session:
            session.wait()


