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

##### analytics
import pandas as pd

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

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s",
    level=logging.ERROR,
    datefmt="%Y-%m-%d %H:%M:%S",
)


GENERATE_PROMPT = """
fill in template with query results in the template below, return only the summary as natural language text, rephrasing the template contents:
${input}
"""

agent_properties = {
    "openai.api": "ChatCompletion",
    "openai.model": "gpt-4o",
    "output_path": "$.choices[0].message.content",
    "input_json": "[{\"role\":\"user\"}]",
    "input_context": "$[0]",
    "input_context_field": "content",
    "input_field": "messages",
    "input_template": GENERATE_PROMPT,
    "openai.temperature": 0,
    "openai.max_tokens": 512,
    "nl2q.case_insensitive": True,
    "rephrase": True,
    "tags": {"PLAN": ["PLAN"]},
    "summary_template": "",
    "queries": {}
}

class SummarizerAgent(OpenAIAgent):
    def __init__(self, **kwargs):
        if "name" not in kwargs:
            kwargs["name"] = "SUMMARIZER"
        super().__init__(**kwargs)


    def _initialize(self, properties=None):
        super()._initialize(properties=properties)

        # additional initialization

    def _initialize_properties(self):
        super()._initialize_properties()

        for key in agent_properties:
            self.properties[key] = agent_properties[key]
    
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

    def summarize_doc(self, properties=None, worker=None):

        if worker == None:
            worker = self.create_worker(None)

        if properties is None:
            properties = self.properties

        # progress
        worker.write_progress(progress_id=worker.sid, label='Summarizing doc...', value=self.current_step/self.num_steps)

        session_data = worker.get_all_session_data()
        
        if session_data is None:
            session_data = {}

        # create a unique id
        id = util_functions.create_uuid()

        summary_template = properties['template']
        summary = string_utils.safe_substitute(summary_template, **self.results,  **session_data)

        if 'rephrase' in properties and properties['rephrase']:
            # progress 
            worker.write_progress(progress_id=worker.sid, label='Rephrasing doc...', value=self.current_step/self.num_steps)
            
            #### call api to rephrase summary
            worker.write_data(self.handle_api_call([summary], properties=properties))
            worker.write_eos()

        else:
            worker.write_data(summary)
            worker.write_eos()

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

                    # user initiated summarizer, kick off queries from template
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
                            self.issue_nl_query(question, worker, name=query_name)

                    # db queries
                    if 'queries' in self.properties:
                        queries = self.properties['queries']
                        for query_name in queries:
                            q = queries[query_name]
                            if type(q) == dict:
                                q = json.dumps(q)
                            else:
                                q = str(q)
                            query = string_utils.safe_substitute(q, **self.properties, **session_data, input=input_data)
                            self.todos.add(query_name)
                            self.issue_sql_query(query, worker, name=query_name)
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

                    self.todos.remove(query)
                    self.results[query] = query_results
                    
                    # all queries received
                    if len(self.todos) == 0:
                        self.summarize_doc(properties=properties, worker=worker)
                else:
                    logging.info("nothing found")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="SUMMARIZER", type=str)
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
            _class=SummarizerAgent,
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
            a = SummarizerAgent(
                name=args.name, session=session, properties=properties
            )
        else:
            # create a new session
            session = Session()
            a = SummarizerAgent(
                name=args.name, session=session, properties=properties
            )

        # wait for session
        if session:
            session.wait()
