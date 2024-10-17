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

        # create lists
        if self.session:
            self.session.set_data("lists", {})

        # create empty short list
        if self.session:
            # by default create a short list
            self.session.set_data("lists.short_list", {})
            # by defaul create a recent list
            self.session.set_data("lists.recent_list", {})

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

    def write_to_new_stream(self, worker, content, output, id=None, tags=None, scope="worker"):
        
        # create a unique id
        if id is None:
            id = util_functions.create_uuid()

        if worker:
            output_stream = worker.write_data(
                content, output=output, id=id, tags=tags, scope=scope
            )
            worker.write_eos(output=output, id=id, scope=scope)

        return output_stream


    
    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):

        stream = stream = message.getStream()

        ##### PROCESS USER input text
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

                    # present main employer form
                    form = ui_builders.build_form()

                    # write form
                    worker.write_control(
                        ControlCode.CREATE_FORM, form, output="FORM"
                    )

                    # describe possible inputs to user
                    self.write_to_new_stream(worker, "You can also directly ask questions in English (e.g. summarize recent candidates, who is top 5 candidates for JD 123)", "TEXT")

        ##### PROCESS RESULTS FROM INTENT CLASSIFICATION   
        elif input == "INTENT":
            if message.isData():
                if worker:
                    data = message.getData()
                    logging.info(json.dumps(data, indent=3))

                    input = None
                    intent = None
                    entities = {}

                    for key in data:
                        if key.upper() == 'INPUT':
                            input = data[key]
                        elif key.upper() == 'INTENT':
                            intent = data[key]
                        elif key.upper() == 'ENTITIES':
                            entities = data[key]
                        else:
                            entities[key.upper()] = data[key]

                    self.init_action(worker, intent=intent, entities=entities, input=input)

        elif input == "ADD_LIST_FROM_QUERY":
            if message.isData():
                if worker:
                    data = message.getData()
                    logging.info(json.dumps(data, indent=3))

                    list = worker.get_session_data("list")
                    if list is None:
                        list = "short_list"

                    if 'result' in data:
                        results = data['result']
                        if results:
                            
                            for result in results:
                                if 'job_seeker_id' in result:
                                    job_seeker_id = result['job_seeker_id']
                                    worker.set_session_data("lists."+list+"."+str(job_seeker_id), True)

                    self._display_list(worker, list, text="Your list now contains: \n")

        elif input == "REMOVE_LIST_FROM_QUERY":
            if message.isData():
                if worker:
                    data = message.getData()
                    logging.info(json.dumps(data, indent=3))

                    list = worker.get_session_data("list")
                    if list is None:
                        list = "short_list"

                    if 'result' in data:
                        results = data['result']
                        if results:
                            
                            for result in results:
                                if 'job_seeker_id' in result:
                                    job_seeker_id = result['job_seeker_id']
                                    worker.set_session_data("lists."+list+"."+str(job_seeker_id), False)

                    self._display_list(worker, list, text="Your list now contains: \n")

        ##### PROCESS FORM UI EVENTS
        elif input == "EVENT":
            if message.isData():
                if worker:
                    data = message.getData()
                    stream = message.getStream()
                    plan_id = form_id = data["form_id"]
                    action = data["action"]

                    # debug
                    context = worker.get_all_session_data()
                    logging.info(json.dumps(context, indent=3)) 
                    
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
                    elif action == "RECENT":
                        self.summarize_recent_jobseekers(worker, context=context)
                    elif action == "TOP":
                        self.list_top_jobseekers(worker, context=context)
                    elif action == "SHORTLIST":
                        self.summarize_shortlisted_jobseekers(worker, context=context)
                    elif action == "COMPARE":
                        self.write_to_new_stream(worker, "You can compare candidates by asking 'compare candidate A, B and C", "TEXT") 
                    elif action == "SMARTQUERIES":
                        self.write_to_new_stream(worker, "Here are a few example queries you can try 'which candidate has the most required skills?'", "TEXT") 
                    elif action == "SKILLS":
                        self.show_skills_distribution(worker, context=context)
                    elif action == "EDUCATION":
                        self.show_education_distribution(worker, context=context)
                    elif action == "YOE":
                        self.show_yoe_distribution(worker, context=context)
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
                        logging.info("PATH====")
                        logging.info(path)
                        sesion_path_filter = set(["JOB_ID"])

                        if path in sesion_path_filter:
                            logging.info("RECORDED")
                            worker.set_session_data(path, value)
                            
            

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
        self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN"], id=id)

        return


    def init_action(self, worker, intent=None, entities=None, input=None):

        ### Possible Intents
        # Intent: SUMMARIZE, SHOW, COMPARE, ADD, REMOVE 
        # Entities: JOB_ID, JOB_SEEKER_ID, LIST, QUERY

        # get session data
        context = worker.get_all_session_data()
        if context is None:
            context = {}

        if entities is None:
            entities = {}

        # update context, if JOB_ID present
        if "JOB_ID" in entities:
            worker.set_session_data("JOB_ID", entities["JOB_ID"])

        if "JOB_SEEKER_ID" in entities:
            worker.set_session_data("JOB_SEEKER_ID", entities["JOB_SEEKER_ID"])

        if intent == "SUMMARIZE":
            if "LIST" in entities:
                list = entities["LIST"]
                if list == "recent_list":
                    self.summarize_recent_jobseekers(worker, context=context, entities=entities, input=input)
                else:
                    self.summarize_listed_jobseekers(worker, context=context, entities=entities, input=input)
            else:
                self.summarize_shortlisted_jobseekers(worker, context=context, entities=entities, input=input)   
        elif intent == "SHOW":
            self.show_list_jobseekers(worker, context=context, entities=entities, input=input)
        elif intent == "ADD":
            self.add_list_jobseekers(worker, context=context, entities=entities, input=input)
        elif intent == "REMOVE":
            self.remove_list_jobseekers(worker, context=context, entities=entities, input=input)
        elif intent == "QUERY":
            self.issue_nl_query(worker, context=context, entities=entities, input=input)
        else:
            self.write_to_new_stream(worker, "I don't know how to help you on that, try summarizing, querying, comparing applies...", "TEXT") 

    #### ACTIONS
    ## summaries
    # recents
    def summarize_recent_jobseekers(self,  worker, context=None, entities=None, input=None):

        self.write_to_new_stream(worker, "Analyzing recent applies to your posting...", "TEXT") 

        # create a unique id
        id = util_functions.create_uuid()

        # summary plan
        summary_plan = [
            [self.name + ".SESSION_DATA", "SUMMARIZER_RECENT.DEFAULT"]
        ]
    
        # filter relevant session data and write to stream
        session_data_stream = self.write_to_new_stream(worker, context, "SESSION_DATA", id=id)

        # build query plan
        plan = self.build_plan(summary_plan, session_data_stream, id=id)

        # write plan
        self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN"], id=id)

        return

    # comparisons
    def summarize_compare_jobseekers(self, worker, context=None, entities=None, input=None):

        self.write_to_new_stream(worker, "Comparing selected applies to your posting...", "TEXT") 

        # create a unique id
        id = util_functions.create_uuid()

        # summary plan
        summary_plan = [
            [self.name + ".SESSION_DATA", "SUMMARIZER_COMPARE.DEFAULT"]
        ]
    
        # filter relevant session data and write to stream
        session_data_stream = self.write_to_new_stream(worker, context, "SESSION_DATA", id=id)

        # build query plan
        plan = self.build_plan(summary_plan, session_data_stream, id=id)

        # write plan
        self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN"], id=id)

        return

    ### lists
    def summarize_listed_jobseekers(self,  worker, context=None, entities=None, input=None):

        self.write_to_new_stream(worker, "Analyzing applies in your list...", "TEXT") 

        # create a unique id
        id = util_functions.create_uuid()

        # summary plan
        summary_plan = [
            [self.name + ".SESSION_DATA", "SUMMARIZER_LIST.DEFAULT"]
        ]
    
        # filter relevant session data and write to stream
        session_data_stream = self.write_to_new_stream(worker, context, "SESSION_DATA", id=id)

        # build query plan
        plan = self.build_plan(summary_plan, session_data_stream, id=id)

        # write plan
        self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN"], id=id)

        return

    def _display_list(self, worker, list, text="List contents: \n"):

        lists = worker.get_session_data("lists")

        if list in lists:
            list_contents = worker.get_session_data("lists." + list)
            if len(list_contents.values()) > 0:
                job_seeker_ids_in_list = worker.get_session_data("lists." + list)
                job_seekers = []
                for job_seeker_id in job_seeker_ids_in_list:
                    if job_seeker_ids_in_list[job_seeker_id]:
                        job_seekers.append({"id":job_seeker_id, "label":"Candidate " + str(job_seeker_id),"value":True })

                # create a form with the list
                form = ui_builders.build_list(job_seekers, title=list, 
                                            text="Below are candidates in your list, toggle checkbox to add/remove from the list...",
                                            element_actions=[{"label": "View", "action":"VIEW"}, {"label": "E-Mail", "action":"EMAIL"}], 
                                            list_actions=[{"label": "Compare", "action":"COMPARE"}, {"label": "Summarize", "action":"SUMMARIZE"}])

                # write form, scope=agent
                worker.write_control(
                    ControlCode.CREATE_FORM, form, output="LIST_"+list, id=list, scope="agent"
                )
            else:
                self.write_to_new_stream(worker, "Your list is empty...", "TEXT")
        else:
            self.write_to_new_stream(worker, "Your list is empty...", "TEXT")
        

    def _identify_list(self, worker, context=None, entities=None, input=None):
        list = "short_list"
        if "LIST" in entities:
            entities_list = entities["LIST"]

            if entities_list is None:
                return list 
            
            # if list, take first one
            if type(entities_list) == list:
                if len(entities_list) == 0:
                    return list
                elif len(entities_list) == 1:
                    entities_list = entities_list[0]

            list = entities_list.replace(" ", "_")
        
        return list

    def show_list_jobseekers(self, worker, context=None, entities=None, input=None):
        
        # identify list to operate on
        list = self._identify_list(worker, context=context, entities=entities, input=input)

        # create list, if not exists
        lists = worker.get_session_data("lists")
        if list not in lists:
            # create list
            worker.set_session_data("lists."+list, {})

        # set list to the session
        worker.set_session_data("list", list)

        logging.info(entities)

        if "QUERY" in entities:
            query = entities["QUERY"]

            # Expand query with context as context
            expanded_query = "Answer the following question with the below context. Ignore information in context if the query overrides context:\n"
            expanded_query += json.dumps(context, indent=3) + "\n"
        
            expanded_query += query

            # create a unique id
            id = util_functions.create_uuid()

            # query plan
            query_plan = [
                [self.name + ".QUERY", "NL2SQL-E2E_INPLAN.DEFAULT"],
                ["NL2SQL-E2E_INPLAN.DEFAULT", self.name + ".ADD_LIST_FROM_QUERY"],
            ]

            # write query to stream
            query_stream = self.write_to_new_stream(worker, expanded_query, "QUERY", id=id)

            # build query plan
            plan = self.build_plan(query_plan, query_stream, id=id)

            # write plan
            self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN"], id=id)

        else:
            self._display_list(worker, list)
            
    def add_list_jobseekers(self, worker, context=None, entities=None, input=None):
        
        # identify list to operate on
        list = self._identify_list(worker, context=context, entities=entities, input=input)

        # create list, if not exists
        lists = worker.get_session_data("lists")
        if list not in lists:
            # create list
            worker.set_session_data("lists."+list, {})

        # set list to the session
        worker.set_session_data("list", list)

        logging.info(entities)

        if "JOB_SEEKER_ID" in entities:
            job_seeker_ids = entities["JOB_SEEKER_ID"]
            if type(job_seeker_ids) == str:
                job_seeker_ids = [job_seeker_ids]
            
            for job_seeker_id in job_seeker_ids:
                worker.set_session_data("lists."+list+"."+str(job_seeker_id), True)

            self._display_list(worker, list, text="Your list now contains: \n")
        else:
            query = None
            if "QUERY" in entities:
                query = entities["QUERY"]
            else:
                query = input
        
            # Expand query with context as context
            expanded_query = "Answer the following question with the below context. Ignore information in context if the query overrides context:\n"
            expanded_query += json.dumps(context, indent=3) + "\n"
            expanded_query += query

            # create a unique id
            id = util_functions.create_uuid()

            # query plan
            query_plan = [
                [self.name + ".QUERY", "NL2SQL-E2E_INPLAN.DEFAULT"],
                ["NL2SQL-E2E_INPLAN.DEFAULT", self.name + ".ADD_LIST_FROM_QUERY"],
            ]

            # write query to stream
            query_stream = self.write_to_new_stream(worker, expanded_query, "QUERY", id=id)

            # build query plan
            plan = self.build_plan(query_plan, query_stream, id=id)

            # write plan
            self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN"], id=id)
        
        
    def remove_list_jobseekers(self, worker, context=None, entities=None, input=None):
        
        # identify list to operate on
        list = self._identify_list(worker, context=context, entities=entities, input=input)

        # create list, if not exists
        lists = worker.get_session_data("lists")
        if list not in lists:
            # create list
            worker.set_session_data("lists."+list, {})

        # set list to the session
        worker.set_session_data("list", list)

        logging.info(entities)


        if "JOB_SEEKER_ID" in entities:
            job_seeker_ids = entities["JOB_SEEKER_ID"]
            if type(job_seeker_ids) == str:
                job_seeker_ids = [job_seeker_ids]
            
            for job_seeker_id in job_seeker_ids:
                worker.set_session_data("lists."+list+"."+str(job_seeker_id), False)

            self._display_list(worker, list, text="Your list now contains: \n")
        else:
            query = None
            if "QUERY" in entities:
                query = entities["QUERY"]
            else:
                query = input

            # Expand query with context as context
            expanded_query = "Answer the following question with the below context. Ignore information in context if the query overrides context:\n"
            expanded_query += json.dumps(context, indent=3) + "\n"
            expanded_query += query

            # create a unique id
            id = util_functions.create_uuid()

            # query plan
            query_plan = [
                [self.name + ".QUERY", "NL2SQL-E2E_INPLAN.DEFAULT"],
                ["NL2SQL-E2E_INPLAN.DEFAULT", self.name + ".REMOVE_LIST_FROM_QUERY"],
            ]

            # write query to stream
            query_stream = self.write_to_new_stream(worker, expanded_query, "QUERY", id=id)

            # build query plan
            plan = self.build_plan(query_plan, query_stream, id=id)

            # write plan
            self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN"], id=id)

    def summarize_jobseekers_jd(self, worker, context=None, entities=None, input=None):
        pass 

    ## visualizations
    def show_skills_distribution(self, worker, context=None, entities=None, input=None):

        # show skill distribution visualization
        skill_vis = ui_builders.build_skill_viz()
        
        # logging.info(json.dumps(skill_vis, indent=3))
        
        # write vis
        worker.write_control(
            ControlCode.CREATE_FORM, skill_vis, output="SKILLVIS"
        )

    def show_education_distribution(self, worker, context=None, entities=None, input=None):
         # show education visualization
        ed_vis = ui_builders.build_ed_viz()
        
        # logging.info(json.dumps(skill_vis, indent=3))
        
        # write vis
        worker.write_control(
            ControlCode.CREATE_FORM, ed_vis, output="EDVIS"
        )


    def show_yoe_distribution(self, worker, context=None, entities=None, input=None):
         # create a unique id
        id = util_functions.create_uuid()

        # query plan
        query_plan = [
            [self.name + ".DEFAULT", "VISUALIZER_YOE.DEFAULT"]
        ]

        # write trigger to stream
        a_stream = self.write_to_new_stream(worker, "visualize yoe", "DEFAULT", tags=["HIDDEN"], id=id)

        # build query plan
        plan = self.build_plan(query_plan, a_stream, id=id)

        # write plan
        self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN"], id=id)

    # def show_yoe_distribution(self, worker, context=None, entities=None, input=None):
    #      # show education visualization
    #     ed_vis = ui_builders.build_yeo_viz()
        
    #     # logging.info(json.dumps(skill_vis, indent=3))
        
    #     # write vis
    #     worker.write_control(
    #         ControlCode.CREATE_FORM, ed_vis, output="YOEVIS"
    #     )

    ## lists
    def list_all_jobseekers(self, worker, context=None, entities=None, input=None):
        # show list visualization
        list_vis = ui_builders.build_list_viz()
        
        # logging.info(json.dumps(skill_vis, indent=3))
        
        # write vis
        worker.write_control(
            ControlCode.CREATE_FORM, list_vis, output="LISTVIS"
        )

    def list_top_jobseekers(self, worker, context=None, entities=None, input=None):
        # show list visualization
        # list_vis = ui_builders.build_list_viz()
        
        # # logging.info(json.dumps(skill_vis, indent=3))
        
        # # write vis
        # worker.write_control(
        #     ControlCode.CREATE_FORM, list_vis, output="LISTVIS"
        # )

        # show list ui
        # present main employer form
        top_list = [
            {"id":1001, "label":"Candidate 1001","value":True },
            {"id":1002, "label":"Candidate 1002","value":True },
            {"id":1003, "label":"Candidate 1003","value":False },
            {"id":1004, "label":"Candidate 1004","value":True },
            {"id":1005, "label":"Candidate 1005","value":False },
            {"id":1006, "label":"Candidate 1006","value":False },
            {"id":1007, "label":"Candidate 1007","value":False }
        ]

        form = ui_builders.build_list(top_list, title="Top Applies", 
                                      text="Below are top 10 applies to your JD, toggle checkbox to add/remove from the shortlist...",
                                      element_actions=[{"label": "View", "action":"VIEW"}, {"label": "E-Mail", "action":"EMAIL"}], 
                                      list_actions=[{"label": "Compare", "action":"COMPARE"}, {"label": "Summarize", "action":"SUMMARIZE"}])

        # write form
        worker.write_control(
            ControlCode.CREATE_FORM, form, output="LIST"
        )

    
    def issue_nl_query(self, worker, context=None, entities=None, input=None):

        if "QUERY" in entities:
            query = entities["QUERY"]
        else:
            query = input


        # Expand query with context as context
        expanded_query = "Answer the following question with the below context. Ignore information in context if the query overrides context:\n"
        expanded_query += json.dumps(context, indent=3) + "\n"
        expanded_query += query

        logging.info("ISSUE NL QUERY:" + expanded_query)
        # create a unique id
        id = util_functions.crecate_uuid()

        # query plan
        query_plan = [
            [self.name + ".QUERY", "NL2SQL-E2E_INPLAN.DEFAULT"],
            ["NL2SQL-E2E_INPLAN.DEFAULT", "OPENAI_EXPLAINER.DEFAULT"],
        ]

        # write query to strea
        query_stream = self.write_to_new_stream(worker, expanded_query, "QUERY", id=id)

        # build query plan
        plan = self.build_plan(query_plan, query_stream, id=id)

        # write plan
        # TODO: this shouldn't necessarily be into a new strea
        self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN"], id=id)

        return



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
