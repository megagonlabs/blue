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
class ObserverAgent(Agent):
    def __init__(self, session=None, input_stream=None, processor=None, properties={}):
        super().__init__("OBSERVER", session=session, input_stream=input_stream, processor=processor, properties=properties)


    def default_processor(self, stream, id, event, value, tags=None, properties=None, worker=None):
        if event == 'EOS':
            # compute stream data
            l = 0
            if worker:
                data = worker.get_data(stream)[0]
                print("{} [{}]: {}".format(stream, ",".join(tags), str(" ".join(data))))
    
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
    parser.add_argument('--loglevel', default="ERROR", type=str)
 
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
        a = ObserverAgent(session=session, properties=properties)
    elif args.input_stream:
        # no session, work on a single input stream
        a = ObserverAgent(input_stream=args.input_stream, properties=properties)
    else:
        # create a new session
        a = ObserverAgent(properties=properties)
        a.start_session()

    # wait for session
    session.wait()



