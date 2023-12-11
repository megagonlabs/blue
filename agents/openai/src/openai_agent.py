###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/agent/')

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


#######################
 ##### sample properties for different openai models
## --properties '{"openai.api":"ChatCompletion","openai.model":"gpt-4","output_path":"$.choices[0].message.content","input_json":"[{\"role\":\"user\"}]","input_context":"$[0]","input_context_field":"content","input_field":"messages"}'
chatGPT_properties = {
    "openai.api":"ChatCompletion",
    "openai.model":"gpt-4",
    "output_path":"$.choices[0].message.content",
    "input_json":"[{\"role\":\"user\"}]",
    "input_context":"$[0]",
    "input_context_field":"content",
    "input_field":"messages"
}

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
    "openai.stop": ["#", ";"]
}

## --properties '{"openai.api":"ChatCompletion","openai.model":"gpt-4","output_path":"$.choices[0].message.content","listens":{"includes":["USER"]},"tags": ["TRIPLE"], "input_json":"[{\"role\":\"user\"}]","input_context":"$[0]","input_context_field":"content","input_field":"messages","input_template":"Given below schema that describe an ontology:\n{schema}\nwhere  {explanation}\n extract one triple from the below sentence in the above format using only above ontology concepts, entities, relations, and properties:\n{input}",  "openai.temperature":0,"openai.max_tokens":256,"openai.top_p":1,"openai.frequency_penalty":0,"openai.presence_penalty":0,"schema":"(PERSON {name,age,id})\n(JOB {from,to,company,title,description})\n(RESUME {date,content,id})\nand relations:\n(PERSON) --[HAS]-> (RESUME)\n(RESUME)--[CONTAINS]->(JOB)\n","explanation":"PERSON, JOB, and RESUME are Concepts,\nHAS is a Relation between PERSON and RESUME,  CONTAINS is a Relation between RESUME and JOB,\nname, age are properties of PERSON and  date, content are properties of RESUME, \n(PERSON {name: \"Michael Gibbons\"})--[HAS]-> (RESUME),\n(RESUME) --[CONTAINS]->(JOB {title:  \"software engineer\"}) are example triples \n"}'
tripleExtractorGPT_properties = {
    "openai.api":"ChatCompletion",
    "openai.model":"gpt-4",
    "output_path":"$.choices[0].message.content",
    "input_json":"[{\"role\":\"user\"}]",
    "input_context":"$[0]",
    "input_context_field":"content",
    "input_field":"messages",
     "input_template": """
Given below schema that describe an ontology:
{schema}
where  {explanation} 
extract one triple from the below sentence in the above format using above ontology concepts, entities, relations, and properties:
{input}
""",
  "openai.temperature":0,
  "openai.max_tokens":256,
  "openai.top_p":1,
  "openai.frequency_penalty":0,
  "openai.presence_penalty":0
}

## --properties '{"openai.api":"ChatCompletion","openai.model":"gpt-4","output_path":"$.choices[0].message.content","listens":{"includes":["TRIPLE"],"excludes":["OPENAI"]},"tags": ["CYPHER"], "input_json":"[{\"role\":\"user\"}]","input_context":"$[0]","input_context_field":"content","input_field":"messages","input_template":"Convert below triple into a CYPHER query: {input}",  "openai.temperature":0,"openai.max_tokens":256,"openai.top_p":1,"openai.frequency_penalty":0,"openai.presence_penalty":0}'
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
  "openai.presence_penalty":0
}

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

    
class ChatGPTAgent(OpenAIAgent):
    def __init__(self, session=None, input_stream=None, processor=None):
        super().__init__(name="CHATGPT", session=session, input_stream=input_stream, processor=processor, properties=chatGPT_properties)

class NL2SQLAgent(OpenAIAgent):
    def __init__(self, session=None, input_stream=None, processor=None):
        super().__init__(name="NL2SQL", session=session, input_stream=input_stream, processor=processor, properties=nl2SQLGPT_properties)

class TripleExtractorGPTAgent(OpenAIAgent):
    def __init__(self, session=None, input_stream=None, processor=None):
        super().__init__(name="CONCEPTGPT", session=session, input_stream=input_stream, processor=processor, properties=tripleExtractorGPT_properties)

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