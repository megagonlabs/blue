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

NL2CYPHER_PROMPT = """Your task is to translate a natural language question into a Cypher query based on the schema of a Neo4j knowledge graph.

Here are the requirements:
- The Cypher query should be compatible with the graph schema. In the graph schema you will be provided with the node properties for each type of node in the graph, the relationship properties for each type of relationship, as well as all unique relationship schemas.
- Pay attention to the datatypes of the properties in the graph schema.
- Output the Cyper query directly without ```. Do not generate explanation or other additional output.

Graph Schema: ${schema}

Question: ${input}

Cypher Query:
"""

# NBA_SCHEMA = """
# Node properties are the following:
# Player {name: STRING, date_of_birth: DATE, height_cm: FLOAT, eid: STRING, mass_kg: FLOAT, aliases: LIST, description: STRING},Team {name: STRING, eid: STRING, description: STRING, head_coach: STRING, aliases: LIST},Venue {aliases: LIST, name: STRING, description: STRING, eid: STRING},Position {name: STRING, eid: STRING, description: STRING, aliases: LIST},Award {name: STRING, eid: STRING, aliases: LIST, description: STRING},Division {aliases: LIST, name: STRING, description: STRING, eid: STRING},Conference {aliases: LIST, name: STRING, description: STRING, eid: STRING}
# Relationship properties are the following:
# playsFor {end_year: INTEGER, start_year: INTEGER},draftedBy {year: INTEGER},receivesAward {year: INTEGER},hasHomeVenue {end_year: INTEGER, start_year: INTEGER}
# The relationships are the following:
# (:Player)-[:playsPosition]->(:Position),(:Player)-[:playsFor]->(:Team),(:Player)-[:draftedBy]->(:Team),(:Player)-[:receivesAward]->(:Award),(:Team)-[:hasHomeVenue]->(:Venue),(:Team)-[:partOfDivision]->(:Division),(:Division)-[:partOfConference]->(:Conference)
# """

nl2cypher_properties = {
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
class Nl2CypherAgent(OpenAIAgent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "NL2CYPHER"
        super().__init__(**kwargs)

    def _initialize(self, properties=None):
        super()._initialize(properties=properties)
        platform_id = self.properties["platform.name"]
        prefix = 'PLATFORM:' + platform_id
        self.registry = DataRegistry(id=self.properties['data_registry.name'], prefix=prefix,
                                     properties=self.properties)

    def _initialize_properties(self):
        super()._initialize_properties()
        for key in nl2cypher_properties:
            self.properties[key] = nl2cypher_properties[key]

    def extract_input_params(self, input_data, properties=None):
        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        neo4j_source = self.registry.connect_source('megagon_hr_insights')
        schema = neo4j_source.fetch_database_collection_schema('neo4j', 'neo4j')
        logging.info(type(schema))
        schema = str(schema)
        # self.schema = schema
        return {'schema': schema}

    # def process_output(self, output_data, properties=None):
    # get properties, overriding with properties provided
    # properties = self.get_properties(properties=properties)
    #     return output_data + '<schema>' + self.schema


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

        af = AgentFactory(_class=Nl2CypherAgent, _name=args.serve, _registry=args.registry, platform=platform,
                          properties=properties)
        af.wait()
    else:
        a = None
        session = None

        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = Nl2CypherAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = Nl2CypherAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()
