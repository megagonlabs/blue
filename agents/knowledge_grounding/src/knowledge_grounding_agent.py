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

        # rationalizer config
        self.properties['requires'] = ['title', 'title_recommendation']

    def default_processor(self, stream, id, label, data, dtype=None, tags=None, properties=None, worker=None):    
        if label == 'EOS':
            pass
                
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
                    graph = Graph("http://18.216.233.236:7474", auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PWD"]))
                    person = worker.get_session_data("name")[0]
                    next_title = worker.get_session_data("title_recommendation")[0]
                    name_query = '''
                        MATCH (p:PERSON{{name: '{}'}})-[h1:HAS]->(b)-[h2:HAS]->(c)
                        RETURN c.label, h2.duration
                        ORDER BY h2.duration DESC
                        LIMIT 2
                    '''.format(person)

                    title_query = '''
                        MATCH (j:TITLE{{label: '{}'}})-[r:REQUIRES]->(b)
                        RETURN b.label, r.avg_duration
                        ORDER BY r.avg_duration DESC
                        LIMIT 2
                    '''.format(next_title)

                    s1 = graph.run(name_query) #.to_ndarray(dtype='str')
                    s2 = graph.run(title_query) #.to_ndarray(dtype='str')
                    s1.columns = ['skill', 'duration']
                    s2.columns = ['skill', 'avg_duration']
    
                    # s1 = s1.to_json(orient='records', lines=True)
                    ret = {}
                    ret["resume_skills"] = list(s1.T.to_dict().values())
                    ret["job_skills"] = list(s2.T.to_dict().values())
                    ret = json.loads(json.dumps(ret))
                    return ret
    
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



