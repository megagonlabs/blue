###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/operator/')
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
from operator import Operator, OperatorFactory
from openai_operator import OpenAIOperator


# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


## --properties '{"openai.api":"Completion","openai.model":"text-davinci-003","output_path":"$.choices[0].text","input_field":"prompt","input_template":"### Postgres SQL tables, with their properties:\n#\n{schema}\n#\n### {input}\nSELECT","openai.max_tokens":100,"openai.temperature":0,"openai.max_tokens":150,"openai.top_p":1.0,"openai.frequency_penalty":0.0,"openai.presence_penalty":0.0,"openai.stop":["#", ";"],"schema":"","output_template":"SELECT {output}"}'
nl2SQLGPT_properties = {
    "openai.api":"Completion",
    "openai.model":"text-davinci-003",
    "output_path":"$.choices[0].text",
    "input_field":"prompt",
    "schema": "",
    "input_template": """
### Postgres SQL tables, with their properties:
#
${schema}
#
### A query to ${input}
SELECT""",
    "output_template": "SELECT ${output}",
    "openai.max_tokens": 100, 
    "openai.temperature": 0,
    "openai.max_tokens": 150,
    "openai.top_p": 1.0,
    "openai.frequency_penalty": 0.0,
    "openai.presence_penalty": 0.0,
    "openai.stop": ["#", ";"],
    "listens": {
        "DEFAULT": {
            "includes": ["USER"],
            "excludes": []
        }
    },
    "tags": {
        "DEFAULT": ["SQL"]
    },
}

class NL2SQLOperator(OpenAIOperator):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "NL2SQL"
        super().__init__(**kwargs)

    def _initialize_properties(self):
        super()._initialize_properties()

        # init properties
        for key in nl2SQLGPT_properties:
            self.properties[key] = nl2SQLGPT_properties[key]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="NL2SQL", type=str)
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
        
        af = OperatorFactory(_class=NL2SQLOperator, _name=args.serve, _registry=args.registry, platform=platform, properties=properties)
        af.wait()
   