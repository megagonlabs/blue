###### OS / Systems
from ctypes import util
import os
import sys

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/agent/")
sys.path.append("./lib/apicaller/")
sys.path.append("./lib/openai/")
sys.path.append("./lib/platform/")
sys.path.append("./lib/agent_registry")
sys.path.append("./lib/utils/")

######
import time
import argparse
import logging
import time

import random

###### Parsers, Formats, Utils
import csv
import json
from utils import json_utils
from string import Template
import copy
import re
import itertools
from tqdm import tqdm

###### Communication
import asyncio
from websockets.sync.client import connect


###### Blue
from agent import Agent, AgentFactory
from api_agent import APIAgent
from session import Session
from producer import Producer
from consumer import Consumer

from openai_agent import OpenAIAgent
from agent_registry import AgentRegistry
from message import Message, MessageType, ContentType, ControlCode
import util_functions
import ui_builders

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s",
    level=logging.ERROR,
    datefmt="%Y-%m-%d %H:%M:%S",
)

from enum import Enum, auto


class EmployerPlannerAgent(Agent):
    def __init__(self, **kwargs):
        if "name" not in kwargs:
            kwargs["name"] = "EMPLOYERPLANNER"
        super().__init__(**kwargs)
        
    def _initialize(self, properties=None):
        super()._initialize(properties=properties)

        # additional initialization

    def _start(self):
        super()._start()
        welcome_message = (
            "Welcome to Employer Assistant! \n\n"
            "I’m here to help you find the perfect candidate for your JDs.\n"
            "Let’s get started!"
        )

        # say welcome
        if self.session:
            self.interact(welcome_message)

    def build_plan(self, plan_dag, stream, id=None):
        
        # create a plan id
        if id is None:
            id = util_functions.create_uuid()
        
        # plan context, initial streams, scope
        plan_context = {"scope": stream[:-7], "streams": {plan_dag[0][0]: stream}}
        
        # construct plan
        plan = {"id": id, "steps": plan_dag, "context": plan_context}

        return plan

    def write_to_new_stream(self, worker, content, output, id=None, tags=None):
        
        # create a unique id
        if id is None:
            id = util_functions.create_uuid()

        if worker:
            output_stream = worker.write_data(
                content, output=output, id=id, tags=tags
            )
            worker.write_eos(output=output, id=id)

        return output_stream

    def issue_sql_query(self, query, worker, id=None):

        # query plan
        query_plan = [
            [self.name + ".QUERY", "NL2SQL-E2E_INPLAN.DEFAULT"],
            ["NL2SQL-E2E_INPLAN.DEFAULT", self.name+".RESULTS"],
        ]
       
        # write query to stream
        query_stream = self.write_to_new_stream(worker, query, "QUERY", tags=["HIDDEN"], id=id)

        # build query plan
        plan = self.build_plan(query_plan, query_stream, id=id)

        # write plan
        # TODO: this shouldn't necessarily be into a new stream
        self.write_to_new_stream(worker, plan, "PLAN", tags=["HIDDEN", "PLAN"], id=id)

        return

    
    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):

        stream = stream = message.getStream()

        ##### Upon USER input text
        if input == "DEFAULT":
           
            if message.isEOS():
                stream = message.getStream()

                # check if welcomed
                welcome = worker.get_session_data("welcome")
                if welcome:
                    # identify intent
                    self.identify_intent(worker, stream)

                else:
                    # set welcome
                    worker.set_session_data("welcome", True)

                    # present main form
                    form = ui_builders.build_form()

                    # write form
                    worker.write_control(
                        ControlCode.CREATE_FORM, form, output="FORM"
                    )


                    # self.write_to_new_stream(worker, "Below is a summary of skills and educational backgrounds", "TEXT")

                    # # present form
                    # skill_vis = ui_builders.build_skill_viz()
                    # # logging.info(json.dumps(skill_vis, indent=3))
                    
                    # # write vis
                    # worker.write_control(
                    #     ControlCode.CREATE_FORM, skill_vis, output="SKILLVIS"
                    # )

                    # # present form
                    # ed_vis = ui_builders.build_ed_viz()
                    # # logging.info(json.dumps(ed_vis, indent=3))
                    
                    # # write vis
                    # worker.write_control(
                    #     ControlCode.CREATE_FORM, ed_vis, output="EDVIS"
                    # )

                    # # present form
                    # list_vis = ui_builders.build_list_viz()
                    # # logging.info(json.dumps(list_vis, indent=3))
                    
                    # # write vis
                    # worker.write_control(
                    #     ControlCode.CREATE_FORM, list_vis, output="LISTVIS"
                    # )
        elif input == "INTENT":
            if message.isData():
                if worker:
                    data = message.getData()
                    logging.info(json.dumps(data, indent=3))

                    if 'intent' in data:
                        intent = data['intent']
                        entities = {}
                        if 'entities' in data:
                            entities = data['entities']

                        self.init_action(worker, intent, entities)

            
        elif input == "EVENT":
            if message.isData():
                if worker:
                    data = message.getData()
                    stream = message.getStream()
                    plan_id = form_id = data["form_id"]
                    action = data["action"]

                    # get form stream
                    form_data_stream = stream.replace("EVENT", "OUTPUT:FORM")

                    # when the user clicked DONE
                    if action == "DONE":
                      
                        # close form
                        worker.write_control(
                            ControlCode.CLOSE_FORM,
                            args={"form_id": form_id},
                            output="FORM",
                        )
                    elif action == "SUMMARIZE":
                        session_data = worker.get_all_session_data()
                        logging.info(json.dumps(session_data, indent=3)) 
                        
                        self.summarize_all_jobseekers(worker, session_data)
                               
                        pass 
                    elif action == "RECENT":
                        pass
                    elif action == "RANK":
                        pass
                    elif action == "TOP":
                        pass
                    elif action == "SHORTLIST":
                        pass 
                    elif action == "COMPARE":
                        pass 
                    elif action == "SMARTQUERIES":
                        pass 
                    else:
                        # save form data
                        path = data["path"]
                        value = data["value"]
                        timestamp = worker.get_stream_data(
                            path + ".timestamp", stream=form_data_stream
                        )

                        if timestamp is None or data["timestamp"] > timestamp:
                            worker.set_stream_data(
                                path,
                                {
                                    "value": value,
                                    "timestamp": data["timestamp"],
                                },
                                stream=form_data_stream,
                            )
                        
                        # save to session
                        sesion_path_filter = set(["JOB_ID"])

                        if path in sesion_path_filter:
                            worker.set_session_data(path, value)
                            
        # process query results
        elif input == "RESULTS":
                if message.isData():
                    stream = message.getStream()
                    # TODO: REVISE
                    # get query from incoming stream
                    query = stream[stream.find("QUERY"):].split(":")[1]

                    data = message.getData()

                    logging.info(data)
                
                    if 'result' in data:
                        query_results = data['result']
            

    #### 
    #### INTENT
    def identify_intent(self, worker, user_stream, id=None):
        # create a unique id
        if id is None:
            id = util_functions.create_uuid()

        # intent plan
        intent_plan = [
            ["USER.TEXT", "OPENAI_CLASSIFIER.DEFAULT"],
            ["OPENAI_CLASSIFIER.DEFAULT", self.name + ".INTENT"]
        ]
    

        # build query plan
        plan = self.build_plan(intent_plan, user_stream, id=id)

        # write plan
        # TODO: change to tags=["HIDDEN"]
        self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN"], id=id)

        return


    def init_action(self, worker, intent, entities):
        # update entities in session
        for entity in entities:
            worker.set_session_data(entity, entities[entity])

        if intent == "SUMMARIZE":
            session_data = worker.get_all_session_data()
            logging.info(json.dumps(session_data, indent=3)) 
            self.summarize_all_jobseekers(worker, session_data)

    #### ACTIONS
    ## summaries
    def summarize_all_jobseekers(self, worker, session_data, id=None):

        # create a unique id
        if id is None:
            id = util_functions.create_uuid()

        # summary plan
        summary_plan = [
            [self.name + ".SESSION_DATA", "SUMMARIZER.DEFAULT"]
        ]
    
        # write session_data to stream
        # TODO: change to tags=["HIDDEN"]
        session_data_stream = self.write_to_new_stream(worker, session_data, "SESSION_DATA", id=id)

        # build query plan
        plan = self.build_plan(summary_plan, session_data_stream, id=id)

        # write plan
        # TODO: change to tags=["HIDDEN"]
        self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN"], id=id)

        return

    def summarize_recent_jobseekers(self, jd_id, date):
        pass

    def compare_jobseekers(self, js_ids):
        pass

    def summarize_jobseekers_jd(self, js_ids, jd_id):
        pass 

    ## visualizations
    def show_skills_distribution(self, jd_id):
        pass

    def show_education_distribution(self, jd_id):
        pass

    ## lists
    def list_all_jobseekers(self, jd_id):
        pass
    
    def list_ranked_jobseekers(self, jd_id, topk):
        pass

    def list_shortlisted_jobseekers(self, jd_id):
        pass

    def add_shortlist_jobseekers(self, js_ids):
        pass 

    def remove_shortlist_jobseekers(self, js_ids):
        pass

    ## example queries
    def show_smart_query_examples(self):
        pass




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="EMPLOYERPLANNER", type=str)
    parser.add_argument("--session", type=str)
    parser.add_argument("--properties", type=str)
    parser.add_argument("--loglevel", default="INFO", type=str)
    parser.add_argument("--serve", type=str)
    parser.add_argument("--platform", type=str, default="default")
    parser.add_argument("--registry", type=str, default="default")

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

        af = AgentFactory(
            _class=EmployerPlannerAgent,
            _name=args.serve,
            _registry=args.registry,
            platform=platform,
            properties=properties,
        )
        af.wait()
    else:
        a = None
        session = None
        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = EmployerPlannerAgent(
                name=args.name, session=session, properties=properties
            )
        else:
            # create a new session
            session = Session()
            a = EmployerPlannerAgent(
                name=args.name, session=session, properties=properties
            )

        # wait for session
        if session:
            session.wait()
