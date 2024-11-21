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
from utils import string_utils
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


class AgenticEmployerAgent(Agent):
    def __init__(self, **kwargs):
        if "name" not in kwargs:
            kwargs["name"] = "AGENTICEMPLOYER"
        super().__init__(**kwargs)
        
    def _initialize(self, properties=None):
        super()._initialize(properties=properties)

        # additional initialization

    def _start(self):
        super()._start()
        welcome_message = (
            "Hi! \n\n"
            "I’m here to help you find the perfect candidates for your JDs.\n"
            "Let’s get started!"
        )


        # say welcome, show form
        if self.session:
            # welcome
            self.interact(welcome_message)

            # init results, todos
            self.lists = {}
            self.selected_job_posting_id = None
            self.job_postings = {}
            self.results = {}
            self.todos = set()

            # ats form
            self.show_ats_form(properties=self.properties)
            
            # get lists
            self.get_lists(properties=self.properties)

            # get job postings 
            self.get_job_postings(properties=self.properties)

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

    def issue_nl_query(self, question, worker, id=None):

        # progress
        worker.write_progress(progress_id=worker.sid, label='Issuing question:' + question, value=self.current_step/self.num_steps)

        # query plan
        query_plan = [
            [self.name + ".Q", "NL2SQL-E2E_INPLAN.DEFAULT"],
            ["NL2SQL-E2E_INPLAN.DEFAULT", self.name+".RESULTS"],
        ]
       
        # write query to stream
        query_stream = self.write_to_new_stream(worker, question, "Q", tags=["HIDDEN"], id=id)

        # build query plan
        plan = self.build_plan(query_plan, query_stream, id=id)

        # write plan
        # TODO: this shouldn't necessarily be into a new stream
        self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN","HIDDEN"], id=id)

        return

    def issue_sql_query(self, query, worker, id=None):

        # query plan
        query_plan = [
            [self.name + ".Q", "QUERYEXECUTOR.DEFAULT"],
            ["QUERYEXECUTOR.DEFAULT", self.name+".QUERY_RESULTS_" + id],
        ]
       
        # write query to stream
        query_stream = self.write_to_new_stream(worker, query, "Q", tags=["HIDDEN"], id=id)

        # build query plan
        plan = self.build_plan(query_plan, query_stream, id=id)

        # write plan
        # TODO: this shouldn't necessarily be into a new stream
        self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN","HIDDEN"], id=id)

        return
    
    def issue_queries(self, properties=None, worker=None):
        if worker == None:
            worker = self.create_worker(None)

        session_data = worker.get_all_session_data()

        # init results, todos
        self.results = {}
        self.todos = set()

        # issue queries
        if 'queries' in self.properties:
            queries = self.properties['queries']
            for query_id in queries:
                q = queries[query_id]
                if type(q) == dict:
                    q = json.dumps(q)
                else:
                    q = str(q)
                query = string_utils.safe_substitute(q, **properties, **session_data)
                self.todos.add(query_id)
                self.issue_sql_query(query, worker, id=query_id)

    def move_job_seeker_to_list(self, job_seeker_id, from_list, to_list, properties=None, worker=None):
        if worker == None:
            worker = self.create_worker(None)

        if properties is None:
            properties = self.properties

        session_data = worker.get_all_session_data()
        
        if type(from_list) == list:
            from_list = ",".join(map(str, from_list))
        else:
            from_list = str(from_list)

        to_list = str(to_list)

        if 'move_job_seeker_to_list' in properties:
            move_job_seeker_to_list_query_template = properties['move_job_seeker_to_list']
            query_template = move_job_seeker_to_list_query_template['query']
            query = string_utils.safe_substitute(query_template, **properties, **session_data, JOB_SEEKER_ID=job_seeker_id, FROM_LIST=from_list, TO_LIST=to_list)
            q = copy.deepcopy(move_job_seeker_to_list_query_template)
            q["query"] = query
            self.issue_sql_query(q, worker, id="move_job_seeker_to_list")
        else:
            logging.error("No `move_job_seeker_to_list` query template found in agent properties!")

    def get_lists(self, properties=None, worker=None):

        if worker == None:
            worker = self.create_worker(None)

        if 'lists' in properties:
            lists_property = properties['lists']

            if type(lists_property) == list:
                self.lists = lists_property
            else:
                # query lists
                query = lists_property
                self.issue_sql_query(query, worker, id="lists")

    def get_job_postings(self, properties=None, worker=None):

        if worker == None:
            worker = self.create_worker(None)

        if 'job_postings' in properties:
            job_postings_property = properties['job_postings']

            if type(job_postings_property) == list:
                self.job_postings = job_postings_property
            else:
                # query job_postings
                query = job_postings_property
                self.issue_sql_query(query, worker, id="job_postings")

    def show_ats_form(self, properties=None, worker=None, update=False):

        if worker == None:
            worker = self.create_worker(None)

        form = ui_builders.build_ats_form(self.selected_job_posting_id, self.job_postings, self.lists, self.results)
        form['form_id'] = "ats"

        # write form, updating existing if necessary 
        # update = False
        if update:
            worker.write_control(
                ControlCode.UPDATE_FORM, form, output="FORM", id="ats", scope="agent", tags=["WORKSPACE"]
            )
        else:
            worker.write_control(
                ControlCode.CREATE_FORM, form, output="FORM", id="ats", scope="agent", tags=["WORKSPACE"]
            )
    
    def extract_job_posting_id(self, s):
        results = re.findall(r"\[\s*\+?#(-?\d+)\s*\]", s)
        if len(results) > 0:
            return results[0]
        else:
            return None

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        if input.find("QUERY_RESULTS_") == 0:
            if message.isData():
                stream = message.getStream()
            
                # get query 
                query = input[len("QUERY_RESULTS_"):]

                data = message.getData()
            
                if 'result' in data:
                    query_results = data['result']

                    if query == "job_postings":
                        self.job_postings = query_results
                        # render ats form with job postings
                        self.show_ats_form(properties=properties, worker=worker, update=True)
                    elif query == "lists":
                        self.lists = query_results
                        # render ats form with lists
                        self.show_ats_form(properties=properties, worker=worker, update=True)
                    elif query == "move_job_seeker_to_list":
                        # reissue queries, to reflect update in ui
                        # self.issue_queries(properties=properties, worker=worker)
                        pass
                    else:
                        self.todos.remove(query)
                        self.results[query] = query_results
                        # all queries received
                        if len(self.todos) == 0:
                            # render ats form with jobseekers data
                            self.show_ats_form(properties=properties, worker=worker, update=True)
                else:
                    logging.info("nothing found")
        elif input == "EVENT":
            if message.isData():
                if worker:
                    data = message.getData()
                    stream = message.getStream()
                    form_id = data["form_id"]
                    action = data["action"]
                    
                    # get form stream
                    form_data_stream = stream.replace("EVENT", "OUTPUT:FORM")
                    
                    if action is None:
                        # save form data
                        path = data["path"]
                        value = data["value"]

                        timestamp = worker.get_data(path + ".timestamp")

                        if timestamp is None or data["timestamp"] > timestamp:

                            prev_value = worker.get_data(path + ".value")
                            
                            worker.set_data(path,
                                {
                                    "value": value,
                                    "timestamp": data["timestamp"],
                                }
                            )
                            
                            # new job posting selected
                            if path == "job_posting":
                                # new value
                                if prev_value != value:
                                    # extract JOB_POSTING_ID
                                    JOB_POSTING_ID = self.extract_job_posting_id(value)
                                    if JOB_POSTING_ID:
                                        # save to session
                                        worker.set_session_data("JOB_POSTING_ID", JOB_POSTING_ID)
                                        self.selected_job_posting_id = JOB_POSTING_ID

                                        # issue other queries
                                        self.issue_queries(properties=properties, worker=worker)

                            # job seeker interested
                            elif path.find("JOB_SEEKER_") == 0:
                                ps = path.split("_")
                                if len(ps) == 4 and ps[3] == "Interested":
                                    job_seeker_id = int(ps[2])

                                    # interested value to code
                                    interested_enums_by_list_code = {"✓": 2, "?": 3, "𐄂":4 }
                                    from_list = list(interested_enums_by_list_code.values())
                                    to_list = interested_enums_by_list_code[value]

                                    # issue db delete/insert transaction
                                    self.move_job_seeker_to_list(job_seeker_id, from_list, to_list, properties=properties, worker=worker)


                    
 


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="AGENTICEMPLOYER", type=str)
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
            _class=AgenticEmployerAgent,
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
            a = AgenticEmployerAgent(
                name=args.name, session=session, properties=properties
            )
        else:
            # create a new session
            session = Session()
            a = AgenticEmployerAgent(
                name=args.name, session=session, properties=properties
            )

        # wait for session
        if session:
            session.wait()
