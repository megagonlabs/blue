###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/agent/")
sys.path.append('./lib/openai/')
sys.path.append("./lib/platform/")
sys.path.append("./lib/utils/")
sys.path.append('./lib/data_registry/')

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

import itertools
from tqdm import tqdm

###### Blue
from agent import Agent, AgentFactory
from openai_agent import OpenAIAgent
# from data_registry import DataRegistry
from session import Session
from message import Message, MessageType, ContentType, ControlCode

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s",
    level=logging.ERROR,
    datefmt="%Y-%m-%d %H:%M:%S",
)

MAGQSQL_PROMPT = """### Complete sqlite SQL query only and with no explanation.

### Some example pairs of question and corresponding SQL query are provided based on similar problems:
Demonstration: 
${demos}

### Given the following database schema: 
${schema}

### Answer the following question: ${question}

SELECT 
"""


magesql_properties = {
    "openai.api": "ChatCompletion",
    "openai.model": "gpt-4o",
    "output_path": "$.choices[0].message.content",
    "input_json": "[{\"role\":\"user\"}]",
    "input_context": "$[0]",
    "input_context_field": "content",
    "input_field": "messages",
    "input_template": MAGQSQL_PROMPT,
    "openai.temperature": 0,
    "openai.max_tokens": 4096,
    "listens": {
        "DEFAULT": {
            "includes": ["USER"],
            "excludes": []
        }
    }
}


#######################
class MageSQLAgent(OpenAIAgent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "MAGQSQL"
        super().__init__(**kwargs)

    def _initialize(self, properties=None):
        super()._initialize(properties=properties)
        with open('database_schema.json','r') as f:
            self.schemas = json.load(f)
        with open('demos.json','r') as f:
            self.demo_candidates = json.load(f)

    def _initialize_properties(self):
        super()._initialize_properties()
        for key in magesql_properties:
            self.properties[key] = magesql_properties[key]

    def _jaccard_similarity(self, list1, list2):
        intersection = len(list(set(list1).intersection(list2)))
        union = (len(set(list1)) + len(set(list2))) - intersection
        return float(intersection) / union
    
    def _select_demo_jac(self, question, k=5):
        tmp = []
        question_tokens = question.split(' ')
        for cand in self.demo_candidates:
            jac = self._jaccard_similarity(question_tokens, cand['question'].split(' '))
            tmp.append((jac, cand))
        tmp.sort(reverse=True,key = lambda x: (x[0]))
        res = [x[1] for x in tmp[:k]]
        demo_str = ""
        demo_fill = "### Answer the following question: "
        for item in res:
            demo_str += demo_fill+item['question']+'\n'+item['query']+'\n'
        return demo_str

    def extract_input_params(self, input_data, properties=None):
        question = input_data.split('#')[0]
        db_id = input_data.split('#')[1]
        print(db_id)
        demos = self._select_demo_jac(question)
        schema = self.schemas[db_id]
        print(demos)
        print(schema)
        return {'demos': demos, 
        'schema': schema,
        'question': question}



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="MAGESQL", type=str)
    parser.add_argument('--session', type=str)
    parser.add_argument('--properties', type=str)
    parser.add_argument('--loglevel', default="INFO", type=str)
    parser.add_argument('--serve', type=str)
    parser.add_argument('--platform', type=str, default='default')
    parser.add_argument('--registry', type=str, default='default')

    args = parser.parse_args()

    #for i in range(10):
    #    print('qwer' * 100 + str(i))

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

        af = AgentFactory(_class=MageSQLAgent, _name=args.serve, _registry=args.registry, platform=platform,
                          properties=properties)
        af.wait()
    else:
        a = None
        session = None

        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = MageSQLAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = MageSQLAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()
