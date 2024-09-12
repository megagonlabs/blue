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

NL2CYPHER_PROMPT = """Your task is to translate a natural language question into a Cypher query based on a list of provided data sources.
Each source is a Neo4j graph with a schema.

Here are the requirements:
- The output should be a JSON object with the following fields
  - "source": the name of the data source that the query will be executed on
  - "query": the Cypher query that is translated from the natural language question
- The Cypher query should be compatible with the graph schema of the data source.
- Output the JSON directly. Do not generate explanation or other additional output.

Data sources:
```
${sources}
```
Question: ${question}
Output:
"""

agent_properties = {
    "openai.api": "ChatCompletion",
    "openai.model": "gpt-4o",
    "output_path": "$.choices[0].message.content",
    "input_json": "[{\"role\":\"user\"}]",
    "input_context": "$[0]",
    "input_context_field": "content",
    "input_field": "messages",
    "input_template": NL2CYPHER_PROMPT,
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
class Nl2CypherE2EAgent(OpenAIAgent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "NL2CYPHER_E2E"
        super().__init__(**kwargs)

    def _initialize(self, properties=None):
        super()._initialize(properties=properties)
        platform_id = self.properties["platform.name"]
        prefix = 'PLATFORM:' + platform_id
        self.registry = DataRegistry(id=self.properties['data_registry.name'], prefix=prefix,
                                     properties=self.properties)
        self.schemas = {}
        logging.info('<sources>' + json.dumps(self.registry.get_sources(), indent=2) + '</sources>')
        for source in self.registry.get_sources():
            properties = self.registry.get_source_properties(source)
            if 'connection' not in properties or properties['connection']['protocol'] != 'bolt':
                continue
            logging.info(f'Connecting to source: {source}')
            try:
                source_db = self.registry.connect_source(source)
            except Exception as e:
                logging.error(f'Error connecting to source: {source}, {str(e)}')
                continue
            # Note: the `database` and `collection` parameters are not used by neo4j_source.py
            schema = source_db.fetch_database_collection_schema('', '')
            self.schemas[source] = schema

    def _initialize_properties(self):
        super()._initialize_properties()
        for key in agent_properties:
            self.properties[key] = agent_properties[key]

    def extract_input_params(self, input_data, properties=None):
        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        sources = [{
            'source': source,
            'schema': schema
        } for source, schema in self.schemas.items()]
        sources = json.dumps(sources, indent=2)
        logging.info(f'<sources>{sources}</sources>')
        return {'sources': sources, 'question': input_data}

    def process_output(self, output_data, properties=None):
        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        response = output_data.replace('```json', '').replace('```', '').strip()
        source, query, result, error = None, None, None, None
        try:
            response = json.loads(response)
            source = response['source']
            query = response['query']
            source_db = self.registry.connect_source(source)
            result = source_db.connection.run_query(query)
        except Exception as e:
            error = str(e)
        return {
            'source': source,
            'query': query,
            'result': result,
            'error': error
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

        af = AgentFactory(_class=Nl2CypherE2EAgent, _name=args.serve, _registry=args.registry, platform=platform,
                          properties=properties)
        af.wait()
    else:
        a = None
        session = None

        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = Nl2CypherE2EAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = Nl2CypherE2EAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()
