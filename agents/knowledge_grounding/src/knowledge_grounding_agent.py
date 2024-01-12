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
        self.properties['requires'] = ['name'] #, 'top_title_recommendation',]

        self.registry = DataRegistry("default")
        self.db_client = None
        self.db = None

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
                    
                    # get source for resume
                    results = self.registry.search_records(keywords="resume", 
                                                           type="collection", 
                                                           scope=None, 
                                                           approximate=True, 
                                                           hybrid=False, 
                                                           page=0, 
                                                           page_size=10)
                    top_result = None
                    for result in results:
                        if result["name"] == "enriched_resume":
                            top_result = result
                    # establish connection to source
                    if top_result:
                        scope = top_result["scope"]
                        collection = top_result["name"]
                        source = scope.split["/"][1]
                        database = scope.split["/"][2]
                        source_connection = self.registry.connect_source(source)
                        self.db_client = source_connection._connect()
                        self.db = self.db_client[database][collection] #collection
                    else:
                        # output to stream
                        return "DATA", {}, "json", True
                    
                    # 
                    # Senior Developer
                    # execute query
                    ## given resume get top 10 skills and durations
                    ### db.enriched_resume.find({'profileId':"1c1p1gdtu0l1m47s"}).projection({'extractions.skill.duration':1})
                    person = worker.get_session_data("name")
                    current_title = "Senior Developer" # worker.get_session_data("title")
                    profile = "1c1p1gdtu0l1m47s"
                    skills_duration_dict = self.db.find(
                        {'profileId':profile}).projection(
                            {'extractions.skill.duration':1})
                    skills_duration_sorted = sorted(
                        skills_duration_dict.items(), 
                        key=lambda x:x[1])
                    if len(skills_duration_sorted) > 3:
                          skills_duration_sorted = skills_duration_sorted[:3]
                    ### query insight db to get next title skiill recommendation
                    next_title = "Head of Development/Operations"
                    # worker.get_session_data("top_title_recommendation")
                    skills_duration_next = skills_duration_sorted
                    
                    ret = {}
                    ret["resume_skills"] = skills_duration_sorted
                    ret["top_title_skills"] = skills_duration_next

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



