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



## --properties '{"openai.api":"ChatCompletion","openai.model":"gpt-4","output_path":"$.choices[0].message.content","listens":{"includes":["USER"],"excludes":[]},"tags": ["TRIPLE"], "input_json":"[{\"role\":\"user\"}]","input_context":"$[0]","input_context_field":"content","input_field":"messages","input_template":"Given below schema that describe an ontology:\n{schema}\nwhere  {explanation}\n extract one triple from the below sentence in the above format using only above ontology concepts, entities, relations, and properties:\n{input}",  "openai.temperature":0,"openai.max_tokens":256,"openai.top_p":1,"openai.frequency_penalty":0,"openai.presence_penalty":0,"schema":"(PERSON {name,age,id})\n(JOB {from,to,company,title,description})\n(RESUME {date,content,id})\nand relations:\n(PERSON) --[HAS]-> (RESUME)\n(RESUME)--[CONTAINS]->(JOB)\n","explanation":"PERSON, JOB, and RESUME are Concepts,\nHAS is a Relation between PERSON and RESUME,  CONTAINS is a Relation between RESUME and JOB,\nname, age are properties of PERSON and  date, content are properties of RESUME, \n(PERSON {name: \"Michael Gibbons\"})--[HAS]-> (RESUME),\n(RESUME) --[CONTAINS]->(JOB {title:  \"software engineer\"}) are example triples \n"}'
tripleExtractorGPT_properties = {
    "openai.api": "ChatCompletion",
    "openai.model": "gpt-4",
    "output_path": "$.choices[0].message.content",
    "input_json": "[{\"role\":\"user\"}]",
    "input_context": "$[0]",
    "input_context_field": "content",
    "input_field": "messages",
    "input_template": """
Given below schema that describe an ontology:
{schema}
where  {explanation}
extract one triple from the below sentence in the above format in a list using only above ontology concepts, entities, relations, and properties:
{input}
""",
    "openai.temperature": 0,
    "openai.max_tokens": 256,
    "openai.top_p": 1,
    "openai.frequency_penalty": 0,
    "openai.presence_penalty": 0,
    "schema": "(PERSON {name,age,id})\n(JOB {from,to,company,title,description})\n(RESUME {date,content,id})\nand relations:\n(PERSON) --[HAS]-> (RESUME)\n(RESUME)--[CONTAINS]->(JOB)\n",
    "explanation": "PERSON, JOB, and RESUME are Concepts,\nHAS is a Relation between PERSON and RESUME,  CONTAINS is a Relation between RESUME and JOB,\nname, age are properties of PERSON and  date, content are properties of RESUME, \n(PERSON {name: \"Michael Gibbons\"})--[HAS]-> (RESUME),\n(RESUME) --[CONTAINS]->(JOB {title:  \"software engineer\"}) are example triples \n",
    "example": "(PERSON {name: \"Michael Gibbons\"})--[HAS]-> (RESUME)",
    "listens": {
        "includes": ["USER"],
        "excludes": []
    },
    "tags": ["TRIPLE"]
}



class TripleExtractorAgent(OpenAIAgent):
    def __init__(self, name="TRIPLEEXTRACTOR", session=None, input_stream=None, processor=None, properties={}):
        super().__init__(name=name, session=session, input_stream=input_stream, processor=processor, properties=properties)

    def _initialize_properties(self):
        super()._initialize_properties()

        # init properties
        for key in tripleExtractorGPT_properties:
            self.properties[key] = tripleExtractorGPT_properties[key]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="TRIPLEEXTRACTOR", type=str)
    parser.add_argument('--session', type=str)
    parser.add_argument('--input_stream', type=str)
    parser.add_argument('--properties', type=str)
    parser.add_argument('--loglevel', default="INFO", type=str)
    parser.add_argument('--serve', type=str, default='TRIPLEEXTRACTOR')
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
        
        af = AgentFactory(agent_class=TripleExtractorAgent, agent_name=args.serve, agent_registry=args.registry, platform=platform, properties=properties)
        af.wait()
    else:
        a = None
        session = None
        if args.session:
            # join an existing session
            session = Session(args.session)
            a = TripleExtractorAgent(name=args.name, session=session, properties=properties)
        elif args.input_stream:
            # no session, work on a single input stream
            a = TripleExtractorAgent(name=args.name, input_stream=args.input_stream, properties=properties)
        else:
            # create a new session
            a = TripleExtractorAgent(name=args.name, properties=properties)
            session = a.start_session()

        # wait for session
        if session:
            session.wait()