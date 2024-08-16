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
from agent import Agent, AgentFactory
from api_agent import APIAgent
from session import Session
from openai_agent import OpenAIAgent


# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")



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
${input}
""",
  "openai.temperature":0,
  "openai.max_tokens":256,
  "openai.top_p":1,
  "openai.frequency_penalty":0,
  "openai.presence_penalty":0,
  "listens": {
      "DEFAULT": {
          "includes": ["TRIPLE"],
          "excludes": []
        }
  },
  "tags": {
      "DEFAULT": ["CYPHER"]
  }
}


class Triple2CypherAgent(OpenAIAgent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "TRIPLE2CYPHER"
        super().__init__(**kwargs)

    def _initialize_properties(self):
        super()._initialize_properties()

        # init properties
        for key in triple2CYPHERGPT_properties:
            self.properties[key] = triple2CYPHERGPT_properties[key]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="TRIPLE2CYPHER", type=str)
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
        
        af = AgentFactory(agent_class=Triple2CypherAgent, agent_name=args.serve, agent_registry=args.registry, platform=platform, properties=properties)
        af.wait()
    else:
        a = None
        session = None
        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = Triple2CypherAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = Triple2CypherAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()