###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/agent/')
sys.path.append('./lib/apicaller/')
sys.path.append('./lib/openai/')
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
from openai_agent import OpenAIAgent
from rpc import RPCServer

# set log level
logging.getLogger().setLevel(logging.INFO)

## --properties '{"openai.api":"Completion","openai.model":"text-davinci-003","output_path":"$.choices[0].text","input_field":"prompt","input_template":"### Postgres SQL tables, with their properties:\n#\n{schema}\n#\n### {input}\nSELECT","openai.max_tokens":100,"openai.temperature":0,"openai.max_tokens":150,"openai.top_p":1.0,"openai.frequency_penalty":0.0,"openai.presence_penalty":0.0,"openai.stop":["#", ";"],"schema":"","output_template":"SELECT {output}"}'
nl2SQLGPT_properties = {
    "openai.api":"Completion",
    "openai.model":"text-davinci-003",
    "output_path":"$.choices[0].text",
    "input_field":"prompt",
    "input_template": """
### Postgres SQL tables, with their properties:
#
{schema}
#
### A query to {input}
SELECT""",
    "output_template": "SELECT {output}",
    "openai.max_tokens": 100, 
    "openai.temperature": 0,
    "openai.max_tokens": 150,
    "openai.top_p": 1.0,
    "openai.frequency_penalty": 0.0,
    "openai.presence_penalty": 0.0,
    "openai.stop": ["#", ";"],
    "listens": {
        "includes": ["USER"],
        "excludes": []
    },
    "tags": ["SQL"],
}

class NL2SQLAgent(OpenAIAgent):
    def __init__(self, name="NL2SQL", session=None, input_stream=None, processor=None, properties={}):
        super().__init__(name=name, session=session, input_stream=input_stream, processor=processor, properties=properties)

    def _initialize_properties(self):
        super()._initialize_properties()

        # init properties
        for key in nl2SQLGPT_properties:
            self.properties[key] = nl2SQLGPT_properties[key]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="NL2SQL", type=str)
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
            logging.info("Launching UserAgent...")
            logging.info(kwargs)
            agent = NL2SQLAgent(*args, **kwargs)
            session = agent.start_session()
            logging.info("Started session: " + session.name)
            logging.info("Launched.")
            return session.name

        # launch agent with parameters, join session in keyword args (session=)
        def join(*args, **kwargs):
            logging.info("Launching UserAgent...")
            logging.info(kwargs)
            agent = NL2SQLAgent(*args, **kwargs)
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
            a = NL2SQLAgent(name=args.name, session=session, properties=properties)
        elif args.input_stream:
            # no session, work on a single input stream
            a = NL2SQLAgent(name=args.name, input_stream=args.input_stream, properties=properties)
        else:
            # create a new session
            a = NL2SQLAgent(name=args.name, properties=properties)
            session = a.start_session()

        # wait for session
        if session:
            session.wait()