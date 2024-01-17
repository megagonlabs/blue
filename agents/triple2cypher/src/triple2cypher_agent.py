###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/agent/')
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

# set log level
logging.getLogger().setLevel(logging.INFO)


## --properties '{"openai.api":"ChatCompletion","openai.model":"gpt-4","output_path":"$.choices[0].message.content","listens":{"includes":["TRIPLE"],"excludes":[]},"tags": ["CYPHER"],"input_json":"[{\"role\":\"user\"}]","input_context":"$[0]","input_context_field":"content","input_field":"messages","input_template":"Convert below triple into a MATCH CYPHER query: {input}","openai.temperature":0,"openai.max_tokens":256,"openai.top_p":1,"openai.frequency_penalty":0,"openai.presence_penalty":0}'
triple2CYPHERGPT_properties = {
    "openai.api":"ChatCompletion",
    "openai.model":"gpt-4",
    "output_path":"$.choices[0].message.content",
    "input_json":"[{\"role\":\"user\"}]",
    "input_context":"$[0]",
    "input_context_field":"content",
    "input_field":"messages",
     "input_template": """
Convert below triple into a CYPHER query:
{input}
""",
  "openai.temperature":0,
  "openai.max_tokens":256,
  "openai.top_p":1,
  "openai.frequency_penalty":0,
  "openai.presence_penalty":0,
  "listens": {
    "includes": ["TRIPLE"],
    "excludes": []
  },
  "tags": ["CYPHER"],
}


class Triple2CypherAgent(OpenAIAgent):
    def __init__(self, name="TRIPLE2CYPHER", session=None, input_stream=None, processor=None, properties={}):
        super().__init__(name=name, session=session, input_stream=input_stream, processor=processor, properties=properties)

    def _initialize_properties(self):
        super()._initialize_properties()

        # init properties
        for key in triple2CYPHERGPT_properties:
            self.properties[key] = triple2CYPHERGPT_properties[key]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="TRIPLE2CYPHER", type=str)
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
        a = Triple2CypherAgent(name=args.name, session=session, properties=properties)
    elif args.input_stream:
        # no session, work on a single input stream
        a = Triple2CypherAgent(name=args.name, input_stream=args.input_stream, properties=properties)
    else:
        # create a new session
        a = Triple2CypherAgent(name=args.name, properties=properties)
        a.start_session()

    # wait for session
    session.wait()