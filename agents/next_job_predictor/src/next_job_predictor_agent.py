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
import openai

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
class NextJobAgent(Agent):
    def __init__(self, session=None, input_stream=None, processor=None, properties={}):
        super().__init__("NEXT_JOB", session=session, input_stream=input_stream, processor=processor, properties=properties)

    def default_processor(self, stream, id, event, value, properties=None, worker=None):
        if event == 'EOS':
            if worker:
                time.sleep(4)
                return '''
                Software Development Engineer-2, Python, 2, Bash scripting, 2, React, 2 ; Software Development Engineer-3, Python, 5, Bash scripting, 4, Postgres, 4 ; Technical Lead, Python, 7, Postgres, 8, Project Management, 5 ; Site Reliability Engineer, Javascript, 3, Agile Testing, 2, Cloud computing, 1 
                '''
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
 
    args = parser.parse_args()

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
        a = NextJobAgent(session=session, properties=properties)
    elif args.input_stream:
        # no session, work on a single input stream
        a = NextJobAgent(input_stream=args.input_stream, properties=properties)
    else:
        # create a new session
        a = NextJobAgent(properties=properties)
        a.start_session()

    # wait for session
    session.wait()



