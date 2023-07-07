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
## --properties '{"openai_api":"ChatCompletion","openai_model":"gpt-4","output_path":"$.choices[0].message.content","input_json":"[{\"role\":\"user\"}]","input_context":"$[0]","input_context_field":"content","input_field":"messages"}'
chatGPT_properties = {
    "openai_api":"ChatCompletion",
    "openai_model":"gpt-4",
    "output_path":"$.choices[0].message.content",
    "input_json":"[{\"role\":\"user\"}]",
    "input_context":"$[0]",
    "input_context_field":"content",
    "input_field":"messages"
}

## --properties '{"openai_api":"Completion","openai_model":"text-davinci-003","output_path":"$.choices[0].text","input_field":"prompt","input_format":"### Postgres SQL tables, with their properties:\n#\n{schema}\n#\n### {input}\nSELECT","openai_max_tokens":100,"openai_temperature":0,"openai_max_tokens":150,"openai_top_p":1.0,"openai_frequency_penalty":0.0,"openai_presence_penalty":0.0,"openai_stop":["#", ";"],"schema":"","output_format":"SELECT {output}"}'
nl2SQLGPT_properties = {
    "openai_api":"Completion",
    "openai_model":"text-davinci-003",
    "output_path":"$.choices[0].text",
    "input_field":"prompt",
    "input_format": """
### Postgres SQL tables, with their properties:
#
{schema}
#
### A query to {input}
SELECT""",
    "output_format": "SELECT {output}",
    "openai_max_tokens": 100, 
    "openai_temperature": 0,
    "openai_max_tokens": 150,
    "openai_top_p": 1.0,
    "openai_frequency_penalty": 0.0,
    "openai_presence_penalty": 0.0,
    "openai_stop": ["#", ";"]
}

class OpenAIAgent(APIAgent):
    def __init__(self, name="OPENAI", session=None, input_stream=None, processor=None, properties={}):
        super().__init__(name, session=session, input_stream=input_stream, processor=processor, properties=properties)

    def _initialize_properties(self):
        super()._initialize_properties()

        self.properties['openai_api'] = 'Completion'
        self.properties['openai_model'] = "text-davinci-003"
        self.properties['input_json'] = None 
        self.properties['input_context'] = None 
        self.properties['input_context_field'] = None 
        self.properties['input_field'] = 'prompt'
        self.properties['output_path'] = '$.choices[0].text'
        self.properties['openai_stream'] = False
        self.properties['openai_max_tokens'] = 50

    
class ChatGPTAgent(OpenAIAgent):
    def __init__(self, session=None, input_stream=None, processor=None):
        super().__init__(name="CHATGPT", session=session, input_stream=input_stream, processor=processor, properties=chatGPT_properties)

class NL2SQLAgent(OpenAIAgent):
    def __init__(self, session=None, input_stream=None, processor=None):
        super().__init__(name="NL2SQL", session=session, input_stream=input_stream, processor=processor, properties=nl2SQLGPT_properties)

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
        a = OpenAIAgent(session=session, properties=properties)
    elif args.input_stream:
        # no session, work on a single input stream
        a = OpenAIAgent(input_stream=args.input_stream, properties=properties)
    else:
        # create a new session
        a = OpenAIAgent(properties=properties)
        a.start_session()

    # wait for session
    session.wait()