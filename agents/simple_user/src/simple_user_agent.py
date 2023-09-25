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
class UserAgent(Agent):
    def __init__(self, session=None, properties={}):
        super().__init__("USER", session=session, input_stream=None, properties=properties)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--session', type=str)
    parser.add_argument('--text', type=str, default='sample')
    parser.add_argument('--interactive', type=bool, default=False, action=argparse.BooleanOptionalAction, help="input text interactively (default False)")
    parser.add_argument('--loglevel', default="INFO", type=str)
 
    args = parser.parse_args()
   
    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())


    session = None
    a = None

    
    if args.session:
        # join an existing session
        session = Session(args.session)
        a = UserAgent(session=session)
    else:
        # create a new session
        a = UserAgent()
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
    session.wait()


