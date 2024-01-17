###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/agent/')
sys.path.append('./lib/openai/')
sys.path.append('./lib/platform/')
sys.path.append('./lib/agent_registry')
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
from agent_registry import AgentRegistry

# set log level
logging.getLogger().setLevel(logging.INFO)


## --properties '{"openai.api":"ChatCompletion","openai.model":"gpt-4","output_path":"$.choices[0].message.content","listens":{"includes":["USER"],"excludes":[]},"tags": ["TRIPLE"], "input_json":"[{\"role\":\"user\"}]","input_context":"$[0]","input_context_field":"content","input_field":"messages","input_template":"Examine the text below and identify a task plan  thatcan be fulfilled by various agents. Specify plan in JSON format, where each agent has attributes of name, description, input and output parameters with names and descriptions:\n{input}",  "openai.temperature":0,"openai.max_tokens":256,"openai.top_p":1,"openai.frequency_penalty":0,"openai.presence_penalty":0}'
plannerGPT_properties = {
    "openai.api":"ChatCompletion",
    "openai.model":"gpt-4",
    "output_path":"$.choices[0].message.content",
    "input_json":"[{\"role\":\"user\"}]",
    "input_context":"$[0]",
    "input_context_field":"content",
    "input_field":"messages",
    "input_template": """
Examine the text below and identify a task plan  thatcan be fulfilled by various agents. Specify plan in JSON format, where each agent has attributes of name, description, input and output parameters with names and descriptions:
{input}
""",
    "openai.temperature":0,
    "openai.max_tokens":1024,
    "openai.top_p":1,
    "openai.frequency_penalty":0,
    "openai.presence_penalty":0,
    "registry.name": "default",
    "listens": {
        "includes": ["USER"],
        "excludes": []
    },
    "tags": ["PLAN"],
}

class GPTPlannerAgent(OpenAIAgent):
    def __init__(self, name="GPTPLANNER", session=None, input_stream=None, processor=None, properties={}):
        super().__init__(name=name, session=session, input_stream=input_stream, processor=processor, properties=properties)

        logging.info("Using agent registry:" + self.properties['registry.name'])
        self.agent_registry = AgentRegistry(self.properties['registry.name'])

        agents = self.agent_registry.list_records()
        logging.info(json.dumps(agents, indent=4))

    def _initialize_properties(self):
        super()._initialize_properties()

        # init properties
        for key in plannerGPT_properties:
            self.properties[key] = plannerGPT_properties[key]

    def process_output(self, output_data):
        logging.info(output_data)
        gpt_plan = json.loads(output_data)
        extracted_plan = self.extract_plan(gpt_plan)
        logging.info(json.dumps(extracted_plan, indent = 4))
        return output_data
        
    def extract_plan(self, data):
        plan = {}
        self._extract_plan(data, plan)
        self._clean_plan(plan)
        return(plan)

    def _extract_plan(self, data, plan, prefix=""):
        if type(data) == list:
            for i in range(len(data)):
                self._extract_plan(data[i], plan, prefix=prefix + '.' + str(i))
        elif type(data) == dict:
            for k in data:
                self._extract_plan(data[k], plan, prefix=prefix + '.' + k)
        else:
            if data:
                path = self._extract_path(prefix)
                self._set_plan_data(path, data, plan)

    def _extract_path(self, prefix):
        scope = []
        indices = []
        sp = prefix.split('.')
        for spi in sp:
            n = None
            try:
                n = int(spi)
            except:
                n = None
            if spi == '':
                continue
            elif n is not None:
                indices.append(n)
            elif spi.find('agent') > -1:
                scope.append('agent')
            elif spi.find('input') > -1:
                scope.append('input')
            elif spi.find('output') > -1:
                scope.append('output')
            else:
                if len(scope) > 0:
                    indices.append(spi)
        path = ''
        for s,i in zip(scope, indices[:-1]):
            path = path + str(s) + '['+ str(i)+ ']' + '.'
        if len(indices) > 0:
            path = path + indices[-1]
        return path
          
      
    def _set_plan_data(self, path, value, plan):
        p = path.split('.')
        scope = plan
        for pi in p[:-1]:
            s = pi.replace(']','').replace('[','.').split('.')
            ss = s[0]
            si = s[1]
            if ss in scope:
                scope = scope[ss]
            else:
                scope[ss] = {}
                scope = scope[ss]
            ndx = si
            is_number = None
            try:
                is_number = int(si)
            except:
                is_number = None
            if is_number is None:
                ndx2p = {}
                if '_ndx2p' in scope:
                    ndx2p = scope['_ndx2p']
                else:
                    scope['_ndx2p'] = ndx2p
                npp = str(p[:-1])
                ndx = len(scope)
                if npp in ndx2p: 
                    ndx = ndx2p[npp]
                else:
                    ndx2p[npp] = ndx
            if ndx in scope:
                scope = scope[ndx]
            else:
                scope[ndx] = {}
                scope = scope[ndx]
                if is_number is None:
                    scope['name'] = si
        key = p[-1]   
        scope[key] = value
       

    def _clean_plan(self, data):
        if type(data) == list:
            for i in range(len(data)):
                self._clean_plan(data[i])
        elif type(data) == dict:
            for k in data:
                self._clean_plan(data[k])
            if '_ndx2p' in data:
                del data['_ndx2p']
            if '' in data:
                del data['']


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--session', type=str)
    parser.add_argument('--name', default="GPTPLANNER", type=str)
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
        a = GPTPlannerAgent(name=args.name, session=session, properties=properties)
    elif args.input_stream:
        # no session, work on a single input stream
        a = GPTPlannerAgent(name=args.name, input_stream=args.input_stream, properties=properties)
    else:
        # create a new session
        a = GPTPlannerAgent(name=args.name, properties=properties)
        a.start_session()

    # wait for session
    session.wait()