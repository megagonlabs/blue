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
class UserAgent(Agent):
    def __init__(self, name = "USER", session=None, properties={}):
        super().__init__(name=name, session=session, input_stream=None, properties=properties)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="USER", type=str)
    parser.add_argument('--session', type=str)
    parser.add_argument('--text', type=str)
    parser.add_argument('--interactive', type=bool, default=False, action=argparse.BooleanOptionalAction, help="input text interactively (default False)")
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
            logging.info("Launching UserAgent...")
            logging.info(kwargs)
            input = None
            if 'input' in kwargs:
                input = kwargs['input']
                del kwargs['input']
            agent = UserAgent(*args, **kwargs)
            session = agent.start_session()
            logging.info("Started session: " + session.name)
            if input:
                agent.interact(input)
                logging.info("Interact: " + input)
            logging.info("Launched.")
            return session.name

        # launch agent with parameters, join session in keyword args (session=)
        def join(*args, **kwargs):
            logging.info("Launching UserAgent...")
            logging.info(kwargs)
            input = None
            if 'input' in kwargs:
                input = kwargs['input']
                del kwargs['input']
            agent = UserAgent(*args, **kwargs)
            logging.info("Joined session: " + kwargs['session'])
            if input:
                agent.interact(input)
                logging.info("Interact: " + input)
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
            a = UserAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            a = UserAgent(name=args.name, properties=properties)
            session = a.start_session()


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


