###### OS / Systems
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


class JobSearchPlannerAgent(Agent):
    def __init__(self, **kwargs):
        if "name" not in kwargs:
            kwargs["name"] = "JOBSEARCHPLANNER"
        super().__init__(**kwargs)
        self.user_profile = {}
        self.search_predicates = {}
        self.form_data = {}
        # TODO: this is currently in memory
        # move this into the session stream data.

    def _initialize(self, properties=None):
        super()._initialize(properties=properties)

        # additional initialization

    def _initialize_properties(self):
        super()._initialize_properties()

        # additional properties
        listeners = {}
        # listen to user
        default_listeners = {}
        listeners["DEFAULT"] = default_listeners
        self.properties["listens"] = listeners
        default_listeners["includes"] = ["USER"]
        default_listeners["excludes"] = [self.name]

        self.properties["tags"] = {"DEFAULT": ["PLAN"]}

    def _start(self):
        super()._start()

        # say hello
        if self.session:
            self.interact("Hello, I'm your job search assistant. How can I help you?")

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        ##### Upon USER input text
        if input == "DEFAULT":
            if message.isEOS():
                # get all data received from user stream
                stream = message.getStream()
                stream_data = ""
                if worker:
                    stream_data = worker.get_data(stream)

                # create a plan to process user text
                plan_id = util_functions.create_uuid()

                # TODO: hard-coded plan and agent names

                plan_dag = [
                    ["USER.TEXT", "OPENAI_EXTRACTOR2.DEFAULT"],
                    ["OPENAI_EXTRACTOR2.DEFAULT", "JOBSEARCHPLANNER.EXTRACTIONS"],
                ]

                plan_context = {"scope": stream[:-7], "streams": {"USER.TEXT": stream}}

                plan = {"id": plan_id, "steps": plan_dag, "context": plan_context}

                return plan

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
        elif input == "EXTRACTIONS":
            if message.isData():
                # process and update
                extractions = message.getData()

                ### DECIDE NEXT STEPS
                ## parse the extraction results
                # if minimal requirment met, proceed to skills recommendation
                # if not, proceed to ask more questions and extract again.

                extracted = util_functions.extract_json(extractions)

                next_question = []
                if "Job Title" in extracted:
                    self.search_predicates["job_title"] = extracted["Job Title"]
                else:
                    next_question.append("job title")
                if "Location" in extracted:
                    self.search_predicates["location"] = extracted["Location"]
                else:
                    next_question.append("location")

                if len(extracted) >= 2:
                    # write form
                    profile_form = ui_builders.build_form_profile(json.dumps(extracted))

                    if worker:
                        worker.write_control(
                            ControlCode.CREATE_FORM, profile_form, output="FORM"
                        )
                else:
                    if worker:
                        worker.write_data(
                            f"Can you provide the {','.join(next_question)} of the job?",
                            output="QUESTION",
                        )

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
                    if action == "DONE_PROFILE":
                        # get form data
                        skills = worker.get_stream_data(
                            "profile_skills.value", stream=form_data_stream
                        )
                        yoe = worker.get_stream_data(
                            "yoe.value", stream=form_data_stream
                        )

                        # close form
                        args = {"form_id": form_id}
                        worker.write_control(
                            ControlCode.CLOSE_FORM, args, output="FORM"
                        )
                        skills = [item["skill"] for item in skills]

                        profile_form = ui_builders.build_form_more_skills(skills)

                        if worker:
                            worker.write_control(
                                ControlCode.CREATE_FORM, profile_form, output="FORM"
                            )
                        return (
                            f"{yoe} years of experiences and skills {','.join(skills)}"
                        )
                        # TODO: add EOS to stream to user
                        """
                        ### DECIDE NEXT STEPS
                        # create a plan to issue a query
                        query = f"Find a job {self.search_predicates['job_title']} in {self.search_predicates['location']}"
                        output_stream = worker.write_data(
                            query,
                            output="QUERY",
                        )
                        worker.write_eos(output="QUERY")

                        plan_id = util_functions.create_uuid()

                        # TODO: hard-coded plan and agent names
                        plan_dag = [
                            ["JOBSEARCHPLANNER.QUERY", "NL2SQL-E2E_INPLAN.DEFAULT"],
                            ["NL2SQL-E2E_INPLAN.DEFAULT", "JOBSEARCHPLANNER.RETRIEVAL"],
                        ]

                        plan_context = {
                            "scope": stream[:-7],
                            "streams": {"JOBSEARCHPLANNER.QUERY": output_stream},
                        }

                        plan = {
                            "id": plan_id,
                            "steps": plan_dag,
                            "context": plan_context,
                        }

                        return plan
                        """
                    elif action == "DONE_MORE_SKILLS":
                        # get form data

                        args = {"form_id": form_id}
                        worker.write_control(
                            ControlCode.CLOSE_FORM, args, output="FORM"
                        )

                        return json.dumps(self.form_data)

                    else:
                        # save form data
                        path = data["path"]
                        timestamp = worker.get_stream_data(
                            path + ".timestamp", stream=form_data_stream
                        )

                        # TODO: timestamp should be replaced by id to determine order
                        if timestamp is None or data["timestamp"] > timestamp:

                            worker.set_stream_data(
                                path,
                                {
                                    "value": data["value"],
                                    "timestamp": data["timestamp"],
                                },
                                stream=form_data_stream,
                            )
                        timestamp_local = self.form_data.get(path, None)
                        if timestamp_local is not None:
                            timestamp_local = timestamp_local["timestamp"]
                        if (
                            timestamp_local is None
                            or data["timestamp"] > timestamp_local
                        ):
                            self.form_data[path] = {
                                "value": data["value"],
                                "timestamp": data["timestamp"],
                            }

        elif input == "RETRIEVAL":
            if message.isData():
                data = message.getData()
                return data

        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="JOBSEARCHPLANNER", type=str)
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
            _class=JobSearchPlannerAgent,
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
            a = JobSearchPlannerAgent(
                name=args.name, session=session, properties=properties
            )
        else:
            # create a new session
            session = Session()
            a = JobSearchPlannerAgent(
                name=args.name, session=session, properties=properties
            )

        # wait for session
        if session:
            session.wait()
