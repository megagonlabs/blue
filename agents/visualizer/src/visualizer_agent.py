###### OS / Systems
from ctypes import util
import os
import sys

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/agent/")
sys.path.append("./lib/platform/")
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

##### analytics
import pandas as pd

###### Communication
import asyncio
from websockets.sync.client import connect


###### Blue
from agent import Agent, AgentFactory
from session import Session
from producer import Producer
from consumer import Consumer

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


class VisualizerAgent(Agent):
    def __init__(self, **kwargs):
        if "name" not in kwargs:
            kwargs["name"] = "VISUALIZER"
        super().__init__(**kwargs)


    def _initialize_properties(self):
        super()._initialize_properties()
    
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

    def issue_nl_query(self, question, worker, name=None, id=None):

       # create a unique id
        if id is None:
            id = util_functions.create_uuid()

        if name is None:
            name = "unspecified"

        # progress
        worker.write_progress(progress_id=worker.sid, label='Issuing question:' + question, value=self.current_step/self.num_steps)

  
        # query plan
        query_plan = [
            [self.name + ".Q", "NL2SQL-E2E___INPLAN.DEFAULT"],
            ["NL2SQL-E2E___INPLAN.DEFAULT", self.name+".QUESTION_RESULTS_" + name],
        ]
       
        # write query to stream
        query_stream = self.write_to_new_stream(worker, question, "Q", tags=["HIDDEN"], id=id)

        # build query plan
        plan = self.build_plan(query_plan, query_stream, id=id)

        # write plan
        # TODO: this shouldn't necessarily be into a new stream
        self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN","HIDDEN"], id=id)

        return

    def issue_sql_query(self, query, worker, name=None, id=None):

        # create a unique id
        if id is None:
            id = util_functions.create_uuid()

        if name is None:
            name = "unspecified"

        # query plan
        query_plan = [
            [self.name + ".Q", "QUERYEXECUTOR.DEFAULT"],
            ["QUERYEXECUTOR.DEFAULT", self.name+".QUERY_RESULTS_" + name],
        ]
       
        # write query to stream
        query_stream = self.write_to_new_stream(worker, query, "Q", tags=["HIDDEN"], id=id)

        # build query plan
        plan = self.build_plan(query_plan, query_stream, id=id)

        # write plan
        # TODO: this shouldn't necessarily be into a new stream
        self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN","HIDDEN"], id=id)

        return
    
    def render_vis(self, properties=None, worker=None):

        logging.info("r1")
        if worker == None:
            worker = self.create_worker(None)

        if properties is None:
            properties = self.properties

        logging.info("r2")
        # progress
        worker.write_progress(progress_id=worker.sid, label='Rendering visualization...', value=self.current_step/self.num_steps)

        session_data = worker.get_all_session_data()

        if session_data is None:
            session_data = {}

        template = self.properties['template']
        if type(template) is dict:
            template = json.dumps(template)

        logging.info("r3")
        vis_json = string_utils.safe_substitute(template, **self.properties, **self.results,  **session_data)

        vis = json.loads(vis_json)
        vis_form = ui_builders.build_vis_form(vis)

        # write vis
        worker.write_control(
            ControlCode.CREATE_FORM, vis_form, output="VIS"
        )

        # progress, done
        worker.write_progress(progress_id=worker.sid, label='Done...', value=1.0)


    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
    
        ##### Upon USER input text
        if input == "DEFAULT":
            if message.isEOS():
                # get all data received from user stream
                stream = message.getStream()

                stream_data = worker.get_data(stream)
                input_data = " ".join(stream_data)
                if worker:
                    session_data = worker.get_all_session_data()

                    if session_data is None:
                        session_data = {}

                    # user initiated visualizer, kick off queries from template
                    self.results = {}
                    self.todos = set()

                    self.num_steps = 1  
                    self.current_step = 0

                    if 'questions' in self.properties:
                        self.num_steps = self.num_steps + len(self.properties['questions'].keys())
                    if 'queries' in self.properties:
                        self.num_steps = self.num_steps + len(self.properties['queries'].keys())

                    # nl questions
                    if 'questions' in self.properties:
                        questions = self.properties['questions']
                        for question_name in questions:
                            q = questions[question_name]
                            question = string_utils.safe_substitute(q, **self.properties, **session_data, input=input_data)
                            self.todos.add(question_name)
                            self.issue_nl_query(question, worker, name=question_name)
                    # db queries
                    if 'queries' in self.properties:
                        queries = self.properties['queries']
                        for question_name in queries:
                            q = queries[question_name]
                            if type(q) == dict:
                                q = json.dumps(q)
                            else:
                                q = str(q) 
                            query = string_utils.safe_substitute(q, **self.properties, **session_data, input=input_data)
                            self.todos.add(question_name)
                            self.issue_sql_query(query, worker, name=question_name)
                    if 'questions' not in self.properties and 'queries' not in self.properties:
                        self.render_vis(properties=properties, worker=None)

                    return

            elif message.isBOS():
                stream = message.getStream()

                # init private stream data to empty array
                if worker:
                    worker.set_data(stream, [])
                pass
            elif message.isData():
                # store data value
                data = message.getData()
                stream = message.getStream()

                # append to private stream data
                if worker:
                    worker.append_data(stream, data)

        elif input.find("QUERY_RESULTS_") == 0:
            if message.isData():
                stream = message.getStream()
                
                # get query 
                query = input[len("QUERY_RESULTS_"):]

                data = message.getData()

                if 'result' in data:
                    query_results = data['result']

                    self.results[query] = json.dumps(query_results)
                    self.todos.remove(query)

                    # progress
                    self.current_step = len(self.results)
                    q = ""
                    if 'query' in data and data['query']:
                        q = data['query']
                    if 'question' in data and data['question']:
                        q = data['question']

                    worker.write_progress(progress_id=worker.sid, label='Received query results: ' + q, value=self.current_step/self.num_steps)

                    if len(self.todos) == 0:
                        if len(query_results) == 0:
                            self.write_to_new_stream(worker, "No results...", "TEXT")
                            worker.write_progress(progress_id=worker.sid, label='Done...', value=1.0)
                        else:
                            self.render_vis(properties=properties, worker=worker)
                else:
                    logging.info("nothing found")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="VISUALIZER", type=str)
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
            _class=VisualizerAgent,
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
            a = VisualizerAgent(
                name=args.name, session=session, properties=properties
            )
        else:
            # create a new session
            session = Session()
            a = VisualizerAgent(
                name=args.name, session=session, properties=properties
            )

        # wait for session
        if session:
            session.wait()
