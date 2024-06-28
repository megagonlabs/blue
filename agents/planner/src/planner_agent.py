###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/agent/')
sys.path.append('./lib/apicaller/')
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
import copy

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
from agent_registry import AgentRegistry


# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


## --properties '{"openai.api":"ChatCompletion","openai.model":"gpt-4","output_path":"$.choices[0].message.content","listens":{"includes":["USER"],"excludes":[]},"tags": ["TRIPLE"], "input_json":"[{\"role\":\"user\"}]","input_context":"$[0]","input_context_field":"content","input_field":"messages","input_template":"Examine the text below and identify a task plan  thatcan be fulfilled by various agents. Specify plan in JSON format, where each agent has attributes of name, description, input and output parameters with names and descriptions:\n{input}",  "openai.temperature":0,"openai.max_tokens":256,"openai.top_p":1,"openai.frequency_penalty":0,"openai.presence_penalty":0}'
planner_properties = {
    "openai.api": "ChatCompletion",
    "openai.model": "gpt-4",
    "output_path": "$.choices[0].message.content",
    "input_json": "[{\"role\":\"user\"}]",
    "input_context": "$[0]",
    "input_context_field": "content",
    "input_field": "messages",
    "input_template": """
Examine the text below and identify a task plan that can be fulfilled by various agents, leveraging agents listed below only. 
Output only the plan, where each inputs and outputs from agents are paired to execute the plan, as a directed acyclic graph, in JSON, using the plan format below. 
TEXT: ${input} 
AGENTS: ${agents} 
PLAN FORMAT: [{{\"from\": \"<agent>.<output>\", \"to\":\"<agent>.<input>\"}}] 
PLAN:",
""",
    "openai.temperature": 0,
    "openai.max_tokens": 1024,
    "openai.top_p": 1,
    "openai.frequency_penalty": 0,
    "openai.presence_penalty": 0,
    "registry.name": "default",
    "search.threshold": 0.05,
    "search.limit": 10,
    "listens": {"includes": ["USER"], "excludes": []},
    "tags": ["PLAN"],
}


class PlannerAgent(OpenAIAgent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "PLANNER"
        super().__init__(**kwargs)

    def _initialize(self, properties=None):
        super()._initialize(properties=properties)

        # connect to registry
        platform_id = self.properties["platform.name"]
        prefix = 'PLATFORM:' + platform_id

        logging.info("Using agent registry:" + self.properties['registry.name'])
        self.registry = AgentRegistry(id=self.properties['registry.name'], prefix=prefix, properties=self.properties)

        agents = self.registry.list_records()
        logging.info('Registry contents:')
        logging.info(json.dumps(agents, indent=4))

    def _initialize_properties(self):
        super()._initialize_properties()

        # init properties
        for key in planner_properties:
            self.properties[key] = planner_properties[key]

    def extract_input_params(self, input_data):
        ### given input data, find potentially relevant agents
        # query agent registry
        results = self.registry.search_records(input_data, type='agent', approximate=True, page_size=self.properties["search.limit"])

        logging.info(json.dumps(results, indent=4))
        agents = set()

        # threshold
        threshold = self.properties["search.threshold"]

        # process results in order, to get a list of agents
        prev_score = None 

        for result in results:
            score = float(result['score'])
            if prev_score == None or ( score / prev_score < (1 + threshold) ): 
                prev_score = score
                if result['type'] == "agent":
                    agents.add(result['name'])
                else:
                    agents.add(result['scope'].split("/")[1])

        # always include user
        agents.add('USER')
        
        agents_data = {}
        for agent in agents:
            agent_data = self.registry.get_agent(agent)
            # process agent data, get name, description, inputs and outputs
            del agent_data['type']
            del agent_data['scope']
            del agent_data['properties']
            agent_data['inputs'] = {}
            agent_data['outputs'] = {}
            for param in agent_data['contents']:
                param_data = agent_data['contents'][param]
                if param_data['type'] == 'input':
                    agent_data['inputs'][param_data['name']] = param_data
                elif param_data['type'] == 'output':
                    agent_data['outputs'][param_data['name']] = param_data
                del param_data['type']
                del param_data['scope']
                del param_data['properties']
                del param_data['contents']

            del agent_data['contents']
            agents_data[agent] = agent_data

        return {"agents": agents_data}
    
    def extract_output_params(self, output_data):
        return {}
    
    def process_output(self, output_data):
        # logging.info(output_data)
        # get gpt plan as json
        plan = json.loads(output_data)
        logging.info('Initial Plan:')
        logging.info(json.dumps(plan, indent=4))
        logging.info('========================================================================================================')

        return plan


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="PLANNER", type=str)
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

        af = AgentFactory(agent_class=PlannerAgent, agent_name=args.serve, agent_registry=args.registry, platform=platform, properties=properties)
        af.wait()
    else:
        a = None
        session = None
        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = PlannerAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = PlannerAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()
