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
from string import Template
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
interactive_planner_properties = {
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


{
    "type": "Control",
    "scope": "#/properties/steps",
    "options": {
        "detail": {
            "type": "VerticalLayout",
            "elements": [
                {
                    "type": "Label",
                    "label": "From"
                },
                {
                    "type": "HorizontalLayout",
                    "elements": [
                        {
                            "type": "Control",
                            "scope": "#/properties/from_agent"
                        },
                        {
                            "type": "Control",
                            "scope": "#/properties/from_output"
                        }
                    ]
                },
                {
                    "type": "Label",
                    "label": "To"
                },
                {
                    "type": "HorizontalLayout",
                    "elements": [
                        {
                            "type": "Control",
                            "scope": "#/properties/to_agent"
                        },
                        {
                            "type": "Control",
                            "scope": "#/properties/to_input"
                        }
                    ]
                }
            ]
        }
    }
}

{
    "type": "object",
    "properties": {
        "steps": {
            "type": "array",
            "title": "Steps",
            "items": {
                "type": "object",
                "properties": {
                    "from_agent": {
                        "type": "string",
                        "enum": [
                            "CandidateSearch"
                        ]
                    },
                    "from_output": {
                        "type": "string",
                        "enum": [
                            "keywords"
                        ]
                    },
                    "to_agent": {
                        "type": "string",
                        "enum": [
                            "CandidateSearch"
                        ]
                    },
                    "to_input": {
                        "type": "string",
                        "enum": [
                            "resumes"
                        ]
                    }
                }
            }
        }
    }
}

class InteractivePlannerAgent(OpenAIAgent):
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
        for key in interactive_planner_properties:
            self.properties[key] = interactive_planner_properties[key]

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

        # represent plan as a form
        interactive_plan = self.create_interactive_plan(plan)
        return interactive_plan

    def create_interactive_plan(self, plan):
        steps_ui = {
            "type": "Control",
            "scope": "#/properties/steps",
            "options": {
                "detail": {
                    "type": "VerticalLayout",
                    "elements": [
                        {
                            "type": "Label",
                            "label": "From"
                        },
                        {
                            "type": "HorizontalLayout",
                            "elements": [
                                {
                                    "type": "Control",
                                    "scope": "#/properties/from_agent"
                                },
                                {
                                    "type": "Control",
                                    "scope": "#/properties/from_agent_param"
                                }
                            ]
                        },
                        {
                            "type": "Label",
                            "label": "To"
                        },
                        {
                            "type": "HorizontalLayout",
                            "elements": [
                                {
                                    "type": "Control",
                                    "scope": "#/properties/to_agent"
                                },
                                {
                                    "type": "Control",
                                    "scope": "#/properties/to_agent_param"
                                }
                            ]
                        }
                    ]
                }
            }
        }

        plan_ui = {
            "type": "VerticalLayout",
            "elements": [
                {
                    "type": "Label",
                    "label": "PROPOSED PLAN",
                    "props": {
                        "style": {
                            "fontWeight": "bold"
                        }
                    }
                },
                {
                    "type": "Label",
                    "label": "Review the proposed plan below and if necessary make appropriate adjustments",
                    "props": {
                        "muted": True,
                        "style": {
                            "marginBottom": 15,
                            "fontStyle": "italic"
                        }
                    }
                },
                {
                    "type": "VerticalLayout",
                    "elements": steps_ui
                }
            ]
        }


        plan_schema_template = """
        {
            "type": "object",
            "properties": {
                "steps": {
                    "type": "array",
                    "title": "Steps",
                    "items": {
                        "type": "object",
                        "properties": {
                            "from_agent": {
                                "type": "string",
                                "enum": ${from_agent_list}
                            },
                            "from_agent_param": {
                                "type": "string",
                                "enum": ${from_agent_params}
                            },
                            "to_agent": {
                                "type": "string",
                                "enum":  ${to_agent_list}
                            },
                            "to_agent_param": {
                                "type": "string",
                                "enum": ${to_agent_params}
                            }
                        }
                    }
                }
            }
        }
        """

        plan_data = []

        step_data_template = """
        {
            "from_agent": "${from_agent}",
            "from_agent_param": "${from_agent_param}",
            "to_agent": "${to_agent}",
            "to_agent_param": "${to_agent_param}"
        }
        """

        ## set plan schema
        records = self.registry.list_records()
        agents = list(records.keys())
        params = list(set(json_utils.json_query(records, "*.contents.*.name", single=False)))
        # convert to json strings

        agents = json.dumps(agents)
        params = json.dumps(params)
        # assign
        from_agent_list = agents
        to_agent_list = agents
        from_agent_params = params
        to_agent_params = params


        plan_schema_t = Template(plan_schema_template)
        plan_schema = plan_schema_t.substitute(from_agent_list=from_agent_list, from_agent_params=from_agent_params, to_agent_list=to_agent_list, to_agent_params=to_agent_params)
        logging.info(plan_schema)
        plan_schema = json.loads(plan_schema)

        # inject plan/steps data
        index = 0 
        for step in plan:
            _from = step['from']
            from_split = _from.split(".")
            from_agent =  from_split[0]
            from_agent_description = ""
            from_agent_param = from_split[1]

            _to = step['to']
            to_split = _to.split(".")
            to_agent =  to_split[0]
            to_agent_description = ""
            to_agent_param = to_split[1]

            step_data_t = Template(step_data_template)
            step_data = step_data_t.substitute(index=index, from_agent=from_agent, from_agent_param=from_agent_param, to_agent=to_agent, to_agent_param=to_agent_param)
            logging.info(step_data)
            step_data = json.loads(step_data)

            plan_data.append(step_data)

            index = index + 1

        interactive_form = {
            "schema": plan_schema,
            "data": plan_data,
            "uischema": plan_ui,
            }

        logging.info(json.dumps(interactive_form, indent=3))
        return ("INTERACTION", {"type": "JSONFORM", "content": interactive_form}, "json", False)

    def default_processor(self, stream, id, label, data, dtype=None, tags=None, properties=None, worker=None):
        if label == 'EOS':
            # get all data received from stream
            stream_data = ""
            if worker:
                stream_data = worker.get_data('stream')

            #### call api to compute, render interactive plan
            return self.handle_api_call(stream_data)
            
        elif label == 'BOS':
            # init stream to empty array
            if worker:
                worker.set_data('stream',[])
            pass
        elif label == 'DATA':
            # store data value
            logging.info(data)
            
            if worker:
                worker.append_data('stream', data)
        
        return None
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="INTERACTIVE_PLANNER", type=str)
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

        af = AgentFactory(agent_class=InteractivePlannerAgent, agent_name=args.serve, agent_registry=args.registry, platform=platform, properties=properties)
        af.wait()
    else:
        a = None
        session = None
        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = InteractivePlannerAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = InteractivePlannerAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()
