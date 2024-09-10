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
from data_registry import DataRegistry
from session import Session
from message import Message, MessageType, ContentType, ControlCode

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s",
    level=logging.ERROR,
    datefmt="%Y-%m-%d %H:%M:%S",
)

NL2SQL_PROMPT = """Your task is to translate a natural language question into a SQL query based on the schema of the database.

Here are the requirements:
- The SQL query should be compatible with the provided schema.
- Output the SQL query directly without ```. Do not generate explanation or other additional output.

Graph Schema: ${schema}

Question: ${input}

SQL Query:
"""

agent_properties = {
    "openai.api": "ChatCompletion",
    "openai.model": "gpt-4o",
    "output_path": "$.choices[0].message.content",
    "input_json": "[{\"role\":\"user\"}]",
    "input_context": "$[0]",
    "input_context_field": "content",
    "input_field": "messages",
    "input_template": NL2SQL_PROMPT,
    "openai.temperature": 0,
    "openai.max_tokens": 512,
    "listens": {
        "DEFAULT": {
            "includes": ["USER"],
            "excludes": []
        }
    }
}


#######################
class Nl2SqlE2EAgent(OpenAIAgent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "NL2SQL_E2E"
        super().__init__(**kwargs)

    def _initialize(self, properties=None):
        super()._initialize(properties=properties)
        platform_id = self.properties["platform.name"]
        prefix = 'PLATFORM:' + platform_id
        self.registry = DataRegistry(id=self.properties['data_registry.name'], prefix=prefix,
                                     properties=self.properties)

    def _initialize_properties(self):
        super()._initialize_properties()
        for key in agent_properties:
            self.properties[key] = agent_properties[key]

    def extract_input_params(self, input_data):
        source = self.registry.connect_source('jobs_db_sample')
        schema = source.fetch_database_collection_schema('', '')
        logging.info(type(schema))
        schema = str(schema)
        # self.schema = schema
        return {'schema': schema}

    def process_output(self, output_data):
        query = output_data.replace('```sql', '').replace('```', '').strip()
        source = self.registry.connect_source('jobs_db_sample')
        cursor = source.connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        return {
            'source': 'jobs_db_sample',
            'query': query,
            'result': data
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="SQLFORGE", type=str)
    parser.add_argument('--session', type=str)
    parser.add_argument('--properties', type=str)
    parser.add_argument('--loglevel', default="INFO", type=str)
    parser.add_argument('--serve', type=str)
    parser.add_argument('--platform', type=str, default='default')
    parser.add_argument('--registry', type=str, default='default')

    args = parser.parse_args()

    for i in range(10):
        print('qwer' * 100 + str(i))

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

        af = AgentFactory(_class=Nl2SqlE2EAgent, _name=args.serve, _registry=args.registry, platform=platform,
                          properties=properties)
        af.wait()
    else:
        a = None
        session = None

        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = Nl2SqlE2EAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = Nl2SqlE2EAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()
