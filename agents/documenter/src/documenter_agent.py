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
from jinja2 import Environment, BaseLoader

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


class DocumenterAgent(Agent):
    def __init__(self, **kwargs):
        if "name" not in kwargs:
            kwargs["name"] = "DOCUMENTER"
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

    def issue_nl_query(self, question, worker, id=None):

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
            ["QUERYEXECUTOR.DEFAULT", self.name+".RESULTS"],
        ]
       
        # write query to stream
        query_stream = self.write_to_new_stream(worker, query, "Q", tags=["HIDDEN"], id=id)

        # build query plan
        plan = self.build_plan(query_plan, query_stream, id=id)

        # write plan
        # TODO: this shouldn't necessarily be into a new stream
        self.write_to_new_stream(worker, plan, "PLAN", tags=["PLAN","HIDDEN"], id=id)

        return
    
    def render_doc(self, worker, results):
        session_data = worker.get_all_session_data()
        if session_data is None:
            session_data = {}

        template = self.properties['template']
        if type(template) is dict:
            template = json.dumps(template)

        processed_template = string_utils.safe_substitute(template, **self.properties,  **session_data)

        t = Environment(loader=BaseLoader()).from_string(processed_template)
        o = t.render(**results)

        logging.info(o)
        doc_form = ui_builders.build_doc_form(o)

        # write vis
        worker.write_control(
            ControlCode.CREATE_FORM, doc_form, output="DOC"
        )

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

                    # user initiated summarizer, kick off queries from template
                    self.results = {}
                    self.todos = set()

                    
                    # nl questions
                    if 'questions' in self.properties:
                        questions = self.properties['questions']
                        for question_id in questions:
                            q = questions[question_id]
                            question = string_utils.safe_substitute(q, **self.properties, **session_data, input=input_data)
                            self.todos.add(question_id)
                            self.issue_nl_query(question, worker, id=query_id)
                    # db queries
                    if 'queries' in self.properties:
                        queries = self.properties['queries']
                        for query_id in queries:
                            q = queries[query_id]
                            if type(q) == dict:
                                q = json.dumps(q)
                            else:
                                q = str(q) 
                            query = string_utils.safe_substitute(q, **self.properties, **session_data, input=input_data)
                            self.todos.add(query_id)
                            self.issue_sql_query(query, worker, id=query_id)
                    if 'questions' not in self.properties and 'queries' not in self.properties:
                        self.render_doc(worker, {})

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

        elif input == "RESULTS":
            if message.isData():
                stream = message.getStream()
                # TODO: REVISE
                # get query from incoming stream
                query = stream[stream.find("Q"):].split(":")[1]

                data = message.getData()

                logging.info(data)
            
                if 'result' in data:
                    query_results = data['result']

                    self.results[query] = json.dumps(query_results)
                    self.todos.remove(query)

                    if len(self.todos) == 0:
                        if len(query_results) == 0:
                            self.write_to_new_stream(worker, "No results...", "TEXT")
                        else:
                            self.render_doc(worker, self.results)
                else:
                    logging.info("nothing found")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="DOCUMENTER", type=str)
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
            _class=DocumenterAgent,
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
            a = DocumenterAgent(
                name=args.name, session=session, properties=properties
            )
        else:
            # create a new session
            session = Session()
            a = DocumenterAgent(
                name=args.name, session=session, properties=properties
            )

        # wait for session
        if session:
            session.wait()
