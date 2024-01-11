###### OS / Systems
import json
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/agent/')
sys.path.append('./lib/platform/')
sys.path.append('./lib/utils/')
sys.path.append('./lib/data_registry/')

import argparse
import csv
import itertools
import json
import logging
import random
###### Parsers, Formats, Utils
import re
###### 
import time
import uuid

import pandas
###### Blue
from agent import Agent
from data_registry import DataRegistry
from neo4j import GraphDatabase
from session import Session
from tqdm import tqdm

# import openai





# set log level
logging.getLogger().setLevel(logging.INFO)

#######################
class KnowledgGroundingAgent(Agent):
    def __init__(self, session=None, input_stream=None, processor=None, properties={}):
        super().__init__("KNOWLEDGE", session=session, input_stream=input_stream, processor=processor, properties=properties)

    def _initialize_properties(self):
        super()._initialize_properties()

        listeners = {}
        self.properties['listens'] = listeners
        listeners['includes'] = ['RECORDER']
        listeners['excludes'] = [self.name]

        ### default tags to tag output streams
        tags = []
        self.properties['tags'] = ['JSON']

        # rationalizer config
        self.properties['requires'] = ['name', 'top_title_recommendation',]

        dr = DataRegistry("rat")

    def default_processor(self, stream, id, label, data, dtype=None, tags=None, properties=None, worker=None):    
        if label == 'EOS':
            if worker:
                processed = worker.get_agent_data('processed')
                if processed:
                    return 'EOS', None, None
            return None
                
        elif label == 'BOS':
            pass
        elif label == 'DATA':
            # check if a required variable is seen
            requires = properties['requires']

            required_recorded = True
            for require in requires:
                # check if require is in session memory
                if worker:
                    v = worker.get_session_data(require)
                    logging.info("variable: {} value: {}".format(require, v))
                    if v is None:
                        required_recorded = False 
                        break

            if required_recorded:
                if worker:
                    processed = worker.get_agent_data('processed')
                    if processed:
                        return None

                    URI = "http://18.216.233.236:7474"
                    AUTH = (os.environ["NEO4J_USER"], os.environ["NEO4J_PWD"])
                    driver = GraphDatabase.driver(URI, auth=AUTH)

                    person = worker.get_session_data("name")
                    next_title = worker.get_session_data("top_title_recommendation")
                    name_query = '''
                        MATCH (p:PERSON{{name: '{}'}})-[h1:HAS]->(b)-[h2:HAS]->(c)
                        RETURN c.label AS skill, h2.duration AS duration
                        ORDER BY h2.duration DESC
                        LIMIT 2
                    '''.format(person)

                    title_query = '''
                        MATCH (j:TITLE{{label: '{}'}})-[r:REQUIRES]->(b)
                        RETURN b.label AS skill, r.avg_duration AS avg_duration
                        ORDER BY r.avg_duration DESC
                        LIMIT 2
                    '''.format(next_title)

                    s1, _, _ = driver.execute_query(name_query)
                    s2, _, _ = driver.execute_query(title_query)
    
                    ret = {}
                    resume_skills = []
                    top_title_skills = []

                    for record in s1:
                        resume_skills.append(dict(record))

                    for record in s2:
                        top_title_skills.append(dict(record))

                    ret["resume_skills"] = resume_skills
                    ret["top_title_skills"] = top_title_skills

                     # set processed to true
                    worker.set_agent_data('processed', True)

                    # output to stream
                    return "DATA", ret, "json", True
    
        return None

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
        a = KnowledgGroundingAgent(session=session, properties=properties)
    elif args.input_stream:
        # no session, work on a single input stream
        a = KnowledgGroundingAgent(input_stream=args.input_stream, properties=properties)
    else:
        # create a new session
        a = KnowledgGroundingAgent(properties=properties)
        a.start_session()

    # wait for session
    session.wait()



