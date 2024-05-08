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

###### 
import time
import argparse
import logging
import uuid
import random

###### Parsers, Formats, Utils
import re
import csv
import json
from utils import json_utils

import itertools
from tqdm import tqdm

###### Machine learning, Data Science
import pandas

###### Databases
from neo4j import GraphDatabase


###### Blue
from agent import Agent, AgentFactory
from session import Session
from data_registry import DataRegistry


# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


#######################
class KnowledgeGroundingAgent(Agent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "KNOWLEDGE"
        super().__init__(**kwargs)

    def _initialize_properties(self):
        super()._initialize_properties()

        listeners = {}
        self.properties['listens'] = listeners
        listeners['includes'] = ["USER"]
        listeners['excludes'] = [self.name]

        ### default tags to tag output streams
        tags = []
        self.properties['tags'] = ['JSON']

        # rationalizer config
        self.properties['requires'] = [] #'name', 'top_title_recommendation',]

        self.registry = DataRegistry("default")
        self.db_client = None
        self.db = None

    def resume_processing(self, profile):
        # get source for resume
        results = self.registry.search_records(keywords="resume", 
                                                type="collection", 
                                                scope=None, 
                                                approximate=True, 
                                                hybrid=False, 
                                                page=0, 
                                                page_size=10)
        
        logging.info("List of collections with relevant information about resume.")
        logging.info(results)
        top_result = None
        for result in results:
            if result["name"] == "enriched_resume":
                top_result = result
        # establish connection to source
        if top_result:
            scope = top_result["scope"]
            collection = top_result["name"]
            source = scope.split("/")[1]
            database = scope.split("/")[2]
            source_connection = self.registry.connect_source(source)
            self.db_client = source_connection.connection
            self.db = self.db_client[database][collection]
        else:
            # output to stream
            # return "DATA", {}, "json", True
            return {}
        
        db_cursor = self.db.find(
            {'profileId':profile},
            {'extractions.skill.duration':1})
        skills_duration_dict_ls = []
        for dbc in db_cursor:
            skills_duration_dict_ls.append(dbc)
        skills_duration_dict = skills_duration_dict_ls[0]['extractions']['skill']['duration']
        skills_duration_tuple = sorted(
            skills_duration_dict.items(), 
            key=lambda x:x[1],
            reverse=True)
        skills_durations_current = []
        for i, t in enumerate(skills_duration_tuple):
            skill, duration = t
            skills_durations_current.append({
                "skill":skill,
                "duration":duration
            })
        logging.info(skills_durations_current)
        return skills_durations_current
    
    def insight_processing(self, next_title):
        # get source for insights
        results = self.registry.search_records(keywords="hr insights", 
                                                type="collection", 
                                                scope=None, 
                                                approximate=True, 
                                                hybrid=False, 
                                                page=0, 
                                                page_size=10)
        top_result = None
        for result in results:
            if result["name"] == "megagon_hr_insights":
                top_result = result
        # establish connection to source
        if top_result:
            scope = top_result["scope"]
            source = scope.split("/")[1]
            source_connection = self.registry.connect_source(source)
            self.db_client = source_connection.connection
        else:
            # output to stream
            # return "DATA", {}, "json", True
            return {}
        
        #next_title = "hse officer"
        ## what does the insight DB have about a skill?
        # MATCH p = (n:JobTitle {{name:'{}'}})-[*1..2]->(d) Return n,d
        # MATCH (j:JobTitle{{name: '{}'}})-[r:requires]->(s:Skill)
        # RETURN s.name as skill, r.duration as duration
        # ORDER BY r.duration DESC
        # LIMIT 3
        title_query = '''
            MATCH (j:JobTitle{{name: '{}'}})-[r:requires]->(s:Skill)
            RETURN s.name as skill, r.duration as duration
            ORDER BY r.duration DESC
        '''.format(next_title) 
        logging.info(title_query)
        result = self.db_client.run_query(title_query)

        logging.info(result)
        return result

    def data_processing(self, worker):
        profile = self.properties['profile'] #"1bv5ncadl2srsbmv" #1c1p1gdtu0l1m47s"
        current_title = self.properties["title"] #"Software Engineer" # worker.get_session_data("title")
        skills_duration_current = self.resume_processing(profile)
        
        ### query insight db to get next title skiill recommendation
        next_title = self.properties["next_title"] #"Senior Software Engineer"
        # worker.get_session_data("top_title_recommendation")
        skills_duration_next = self.insight_processing(next_title)
        
        ret = {}
        ret["current_title"] = {"title": current_title}
        ret["title_recommendations"] = [current_title, next_title]
        ret["resume_skills"] = skills_duration_current
        ret["top_title_skills"] = skills_duration_next
        return ret
    
    def default_processor(self, stream, id, label, data, dtype=None, tags=None, properties=None, worker=None):    
        if label == 'EOS':
            if worker:
                logging.info("WORKER")
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

                    ret = self.data_processing(worker)

                     # set processed to true
                    worker.set_agent_data('processed', True)

                    # output to stream
                    return "DATA", ret, "json", True
    
        return None
        
        
        # if worker:
        #     return self.data_processing(worker)
        # if label == 'EOS':
        #     if worker:
        #         processed = worker.get_agent_data('processed')
        #         if processed:
        #             return 'EOS', None, None
        #     return None
                
        # elif label == 'BOS':
        #     pass
        # elif label == 'DATA':
        #     pass
        # # check if a required variable is seen
        # requires = properties['requires']

        # required_recorded = True
        # for require in requires:
        #     # check if require is in session memory
        #     if worker:
        #         v = worker.get_session_data(require)
        #         logging.info("variable: {} value: {}".format(require, v))
        #         if v is None:
        #             required_recorded = False 
        #             break

        # if required_recorded:
        #     if worker:
        #         processed = worker.get_agent_data('processed')
        #         if processed:
        #             return None
                
        #         ################################
        #         ### resume processing code ####
        #         ################################
        #         return self.data_processing(worker)
    
        # return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="KNOWLEDGE", type=str)
    parser.add_argument('--session', type=str)
    parser.add_argument('--properties', type=str)
    parser.add_argument('--loglevel', default="INFO", type=str)
    parser.add_argument('--serve', type=str, default='KNOWLEDGE')
    parser.add_argument('--platform', type=str, default='default')
    parser.add_argument('--registry', type=str, default='default')

    #TODO: temporary, remove
    parser.add_argument('--profile', type=str)
    parser.add_argument('--title', type=str)
    parser.add_argument('--next_title', type=str)
    
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
        
        af = AgentFactory(agent_class=KnowledgeGroundingAgent, agent_name=args.serve, agent_registry=args.registry, platform=platform, properties=properties)
        af.wait()
    else:
        a = None
        session = None

        # TODO, temporary, remove
        if args.profile:
            properties['profile'] = args.profile
        
        if args.title:
            properties['title'] = args.title

        if args.next_title:
            properties['next_title'] = args.next_title

        if args.session:
            # join an existing session
            session = Session(args.session)
            a = e(session=session, properties=properties)
        else:
            # create a new session
            a = e(properties=properties)
            session = a.start_session()

        # wait for session
        if session:
            session.wait()



