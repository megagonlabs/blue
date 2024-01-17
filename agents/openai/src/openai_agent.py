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
from utils import json_utils

import itertools
from tqdm import tqdm

###### Communication
import asyncio
from websockets.sync.client import connect


###### Blue
from agent import Agent
from api_agent import APIAgent
from session import Session

# set log level
logging.getLogger().setLevel(logging.INFO)


class OpenAIAgent(APIAgent):
    def __init__(self, name="OPENAI", session=None, input_stream=None, processor=None, properties={}):
        super().__init__(name, session=session, input_stream=input_stream, processor=processor, properties=properties)

    def _initialize_properties(self):
        super()._initialize_properties()

        self.properties['openai.service'] = "ws://localhost:8003"

        self.properties['openai.api'] = 'Completion'
        self.properties['openai.model'] = "text-davinci-003"
        self.properties['input_json'] = None 
        self.properties['input_context'] = None 
        self.properties['input_context_field'] = None 
        self.properties['input_field'] = 'prompt'
        self.properties['output_path'] = '$.choices[0].text'
        self.properties['openai.stream'] = False
        self.properties['openai.max_tokens'] = 50

        # prefix for service specific properties
        self.properties['service.prefix'] = 'openai'

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="OPENAI", type=str)
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
        a = OpenAIAgent(name=args.name, session=session, properties=properties)
    elif args.input_stream:
        # no session, work on a single input stream
        a = OpenAIAgent(name=args.name, input_stream=args.input_stream, properties=properties)
    else:
        # create a new session
        a = OpenAIAgent(name=args.name, properties=properties)
        a.start_session()

    # wait for session
    session.wait()