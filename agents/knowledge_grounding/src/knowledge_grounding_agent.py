###### OS / Systems
import os
import sys
import json

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
# import openai

###### Parsers, Formats, Utils
import re
import csv
import json

import itertools
from tqdm import tqdm

###### Blue
from agent import Agent
from session import Session

from py2neo import Graph
import pandas

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

                    graph = Graph("http://18.216.233.236:7474", auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PWD"]))
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

                    s1 = graph.run(name_query) 
                    s2 = graph.run(title_query)
                    s1.columns = ['skill', 'duration']
                    s2.columns = ['skill', 'avg_duration']
    
                    ret = {}
                    resume_skills = json.loads(s1.to_data_frame().to_json(orient='records'))
                    top_title_skills = json.loads(s2.to_data_frame().to_json(orient='records'))
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



