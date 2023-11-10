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


    def default_processor(self, stream, id, label, value, dtype=None, tags=None, properties=None, worker=None):
        if label == 'EOS':
            # compute stream data
            l = 0
            if dtype == 'json':
                pass
            else:
                if worker:
                    data = worker.get_data(stream)
                    str_data = str(" ".join(data))
                    if len(str_data.strip()) > 0:
                        logging.error("{} [{}]: {}".format(stream, ",".join(tags), str_data))
    
        elif label == 'BOS':
            # init stream to empty array
            if worker:
                worker.set_data(stream,[])
            pass
        elif label == 'DATA':
            # store data value
            # logging.error(value)
            if dtype == 'json':
                logging.error("{} [{}]: {}".format(stream, ",".join(tags), value))
            else: 
                if worker:
                    worker.append_data(stream, str(value))
    
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



