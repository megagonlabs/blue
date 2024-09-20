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


class InputType(Enum):
    EXTRACTED = auto()
    UPDATE = auto()
    QUESTION = auto()
    ANSWER_PRESENT = auto()
    ANSWER_INTERNAL = auto()
    NONE = auto()


class JobSearchPlannerAgent(Agent):
    def __init__(self, **kwargs):
        if "name" not in kwargs:
            kwargs["name"] = "JOBSEARCHPLANNER"
        super().__init__(**kwargs)
        self.search_predicates = {
            "job title": "",
            "location": "",
            "minimum salary": "",
            "employment type": "",
        }
        self.user_profile = {
            "years of experience": -1,
            "skills": [],
            "suggested_skills": [],
            "confirmed_skills": [],
        }
        self.form_data = {}  # UI form data
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

    def build_plan(self, plan_dag, stream):
        plan_id = util_functions.create_uuid()
        plan_context = {"scope": stream[:-7], "streams": {plan_dag[0][0]: stream}}
        plan = {"id": plan_id, "steps": plan_dag, "context": plan_context}
        return plan

    def issue_sql_query(self, query, final):
        """
        system issued sql queries queries.
        """
        worker = self.worker
        if worker:
            output_stream = worker.write_data(
                query,
                output="QUERY",
            )
            worker.write_eos(output="QUERY")

        # TODO: hard-coded plan and agent names
        plan_query_planner = [
            ["JOBSEARCHPLANNER.QUERY", "NL2SQL-E2E_INPLAN.DEFAULT"],
            ["NL2SQL-E2E_INPLAN.DEFAULT", "JOBSEARCHPLANNER.ANSWERPLANNER"],
        ]
        plan_query_final = [
            ["JOBSEARCHPLANNER.QUERY", "NL2SQL-E2E_INPLAN.DEFAULT"],
            ["NL2SQL-E2E_INPLAN.DEFAULT", "JOBSEARCHPLANNER.ANSWERFINAL"],
        ]
        if final:
            plan_query = plan_query_final
        else:
            plan_query = plan_query_planner
        plan = self.build_plan(plan_query, output_stream)

        return plan

    def update_memory(self, content):
        for key, value in content.items():

            k = key.lower()
            if k in self.search_predicates and len(value) > 0:
                self.search_predicates[k] = value
            if k in self.user_profile:
                if k == "years of experience":
                    if value > -1:
                        self.user_profile[k] = value
                else:
                    if len(value) > 0:
                        self.user_profile[k].extend(value)
                        self.user_profile[k] = sorted(list(set(self.user_profile[k])))
        logging.warning("UPDATE MEMORY")
        logging.warning(self.search_predicates)
        logging.warning(self.user_profile)

        return

    def next_action(self):
        """
        Act based on memory
        """
        logging.warning("CURRENT MEMORY")
        logging.warning(self.search_predicates)
        logging.warning(self.user_profile)
        covered_predicates = [k for k, v in self.search_predicates.items() if v]
        if len(covered_predicates) < 2:
            uncovered_predicates = list(
                set(self.search_predicates.keys()) - set(covered_predicates)
            )
            clarification_question = f"Can you also provide {','.join(uncovered_predicates)} you are interested in?"
            return clarification_question

        elif (
            self.user_profile["years of experience"] == -1
            or len(self.user_profile["skills"]) == 0
        ):
            profile_form = ui_builders.build_form_profile("")  # TODO
            if self.worker:
                self.worker.write_control(
                    ControlCode.CREATE_FORM, profile_form, output="FORM"
                )
        # query insights for additional skills
        elif len(self.user_profile["suggested_skills"]) == 0:
            query = f"What are the top 5 skills that co-occur frequently with {self.user_profile['skills'][0]}"

            return self.issue_sql_query(query=query, final=False)
        # ask user to confirm suggested skills
        elif len(self.user_profile["confirmed_skills"]) == 0:
            profile_form = ui_builders.build_form_more_skills(
                self.user_profile["suggested_skills"]
            )
            if self.worker:
                self.worker.write_control(
                    ControlCode.CREATE_FORM, profile_form, output="FORM"
                )
        else:
            # issue final query
            employment_type = self.search_predicates["employment type"]
            job_title = self.search_predicates["job title"]
            location = self.search_predicates["location"]
            minimum_salary = self.search_predicates["minimum salary"]
            search_skills = (
                self.user_profile["skills"] + self.user_profile["confirmed_skills"]
            )
            yoe = self.user_profile["years of experience"]
            query = (
                f"Find top 5 {employment_type if len(employment_type)>0 else ''} {job_title if len(job_title)> 0 else ''} job ",
                f"in location {location}" if len(location) > 0 else "",
                (
                    f" with at least {minimum_salary} salary, "
                    if len(minimum_salary) > 0
                    else ""
                ),
                (
                    f", requring {' '.join(search_skills)} skills "
                    if len(search_skills) > 0
                    else ""
                ),
                (
                    f", requiring no more than {yoe} years of experince"
                    if yoe > -1
                    else ""
                ),
            )
            print("".join(query))

            return [self.issue_sql_query(query="".join(query), final=True), Message.EOS]

    def action(self, input_type, input_content, user_stream):
        logging.warning("ACTION")
        logging.warning([input_type, input_content, user_stream])
        # TODO: hard-coded agent name
        plan_extraction = [
            ["USER.TEXT", "OPENAI_EXTRACTOR2.DEFAULT"],
            ["OPENAI_EXTRACTOR2.DEFAULT", "JOBSEARCHPLANNER.EXTRACTIONS"],
        ]
        plan_query_user = [
            ["USER.TEXT", "NL2SQL-E2E_INPLAN.DEFAULT"],
            ["NL2SQL-E2E_INPLAN.DEFAULT", "JOBSEARCHPLANNER.ANSWERUSER"],
        ]

        # user asking exploration questions, call NL2Q
        if input_type == InputType.QUESTION.name:
            # ouput to query stream, write eos
            return self.build_plan(plan_query_user, user_stream)
        # present answer to user
        elif input_type == InputType.ANSWER_PRESENT.name:
            # present: now assuming

            return [input_content["result"], Message.EOS]
        # user providing information
        # call extractor
        elif input_type == InputType.UPDATE.name:
            return self.build_plan(plan_extraction, user_stream)

        elif input_type == InputType.EXTRACTED.name:

            self.update_memory(input_content)
            return self.next_action()
        else:
            return

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        input_type = InputType.NONE.name
        input_content = None
        stream = None
        self.worker = worker
        ##### Upon USER input text
        if input == "DEFAULT":
            if message.isEOS():
                # get all data received from user stream
                stream = message.getStream()

                stream_data = ""
                if worker:
                    stream_data = worker.get_data(stream)

                logging.warning("STREAM DATA:user input")
                logging.warning(stream_data)
                # judge user intent
                # TODO: better matching
                user_input = stream_data[0]
                if user_input.lower().startswith("what"):
                    input_type = "QUESTION"
                    input_content = user_input
                else:
                    input_type = "UPDATE"
                    input_content = user_input

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
                extracted = util_functions.extract_json(extractions)
                # convert to lowercase
                extracted = {
                    key.lower(): value
                    for key, value in extracted.items()
                    if len(value) > 0
                }
                logging.warning("EXTRACTED")
                logging.warning(extracted)
                input_type = InputType.EXTRACTED.name
                input_content = extracted

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
                        worker.write_control(
                            ControlCode.CLOSE_FORM,
                            args={"form_id": form_id},
                            output="FORM",
                        )

                        skills = [item["skill"] for item in skills]

                        input_type = InputType.EXTRACTED.name
                        input_content = {"years of experience": yoe, "skills": skills}

                    elif action == "DONE_MORE_SKILLS":
                        # get form data

                        args = {"form_id": form_id}
                        worker.write_control(
                            ControlCode.CLOSE_FORM, args, output="FORM"
                        )

                        input_type = InputType.EXTRACTED.name

                        logging.warning("MORE SKILL FORM")
                        logging.warning(input_content)

                        confirmed_skills = []
                        for k, v in self.form_data.items():
                            if k.startswith("more_skills.") and v:
                                confirmed_skills.append(k[len("more_skills.") :])
                        input_content = {"confirmed_skills": confirmed_skills}

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

        elif input == "ANSWERPLANNER":
            if message.isData():
                data = message.getData()
                # TODO: hardcoded, only extract for suggested skills query
                logging.warning("RETRIEVAL MORE SKILLs")
                logging.warning(data)
                input_type = InputType.EXTRACTED.name
                input_content = {
                    "suggested_skills": [
                        util_functions.remove_non_alphanumeric(item[0])
                        for item in data["result"]
                    ]
                }

        elif input == "ANSWERUSER" or input == "ANSWERFINAL":
            if message.isData():
                data = message.getData()
                input_type = InputType.ANSWER_PRESENT.name
                input_content = data

        else:
            logging.warning("unexpected input stream")

        if input_type == InputType.NONE.name:
            return None
        else:
            return self.action(
                input_type=input_type, input_content=input_content, user_stream=stream
            )


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
