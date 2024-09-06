###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/agent/')
sys.path.append('./lib/apicaller/')
sys.path.append('./lib/openai/')
sys.path.append('./lib/platform/')
sys.path.append('./lib/agent_registry')
sys.path.append('./lib/utils/')

######
import time
import argparse
import logging
import time
import uuid
import random

###### Parsers, Formats, Utils
import re
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

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


def create_uuid():
    return str(hex(uuid.uuid4().fields[0]))[2:]


class JobSearchPlannerAgent(Agent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "JOBSEARCHPLANNER"
        super().__init__(**kwargs)

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
        self.properties['listens'] = listeners
        default_listeners['includes'] = ['USER']
        default_listeners['excludes'] = [self.name]
        
        self.properties['tags'] = {
            "DEFAULT": [
                "PLAN"
            ]
        }


    def _start(self):
        super()._start()

        # say hello
        if self.session:
            self.interact("Hello, can I help you?")
   

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
                plan_id = create_uuid()
               
                plan_dag = [
                    [
                        "USER.TEXT",
                        "OPENAI_EXTRACTOR.DEFAULT"
                    ],
                    [
                        "OPENAI_EXTRACTOR.DEFAULT",
                        "JOBSEARCHPLANNER.EXTRACTIONS"
                    ]
                ]

                plan_context = {
                    "scope": stream[:-7], 
                    "streams": {
                        "USER.TEXT": stream
                    }
                }

                plan = {
                    "id":  plan_id,
                    "steps": plan_dag,
                    "context": plan_context
                }
                
                return plan
                
            elif message.isBOS():
                stream = message.getStream()
                # init private stream data to empty array
                if worker:
                    worker.set_data(stream,[])
                pass
            elif message.isData():
                # store data value
                data = message.getData()
                stream = message.getStream()
                # append to private stream data
                if worker:
                    worker.append_data(stream, data)
        elif input == "EXTRACTIONS":
            if message.isEOS():
                # process and update 
                extractions = message.getData()
                logging.info(extractions)

                ### DECIDE NEXT STEPS
                # e.g. present a form to ask about skills
                
                # design form
                skills_ui = {
                    "type": "Control",
                    "scope": "#/properties/skills",
                    "options": {
                        "detail": {
                            "type": "VerticalLayout",
                            "elements": [
                                {
                                    "type": "Label",
                                    "label": "Skills"
                                },
                                {
                                    "type": "HorizontalLayout",
                                    "elements": [
                                        {
                                            "type": "Control",
                                            "scope": "#/properties/skill"
                                        },
                                        {
                                            "type": "Control",
                                            "scope": "#/properties/duration"
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }

                form_ui = {
                    "type": "VerticalLayout",
                    "elements": [
                        {
                            "type": "Label",
                            "label": "Skills Profile",
                            "props": {
                                "style": {
                                    "fontWeight": "bold"
                                }
                            }
                        },
                        {
                            "type": "Label",
                            "label": "List your skills and determine a duration for each skill",
                            "props": {
                                "muted": True,
                                "style": {
                                    "marginBottom": 15,
                                    "fontStyle": "italic"
                                }
                            }
                        },
                        {
                            "type": "VerticalLayout",
                            "elements": [ skills_ui ]
                        },
                        {
                            "type": "Button",
                            "label": "Submit",
                            "props": {
                                "intent": "success",
                                "action": "DONE",
                                "large": True,
                            },
                        }
                    ]
                }


                form_schema = {
                    "type": "object",
                    "properties": {
                        "skills": {
                            "type": "array",
                            "title": "Skills",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "skill": {
                                        "type": "string"
                                    },
                                    "duration": {
                                        "type": "string"
                                    }
                                }
                            }
                        }
                    }
                }


                form = {
                    "schema": form_schema,
                    "data": { "skills": [] },
                    "uischema": form_ui
                }
                # write form
                worker.write_control(ControlCode.CREATE_FORM, form, output="FORM")

                return None
        
           
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
                        # get form data
                        skills = worker.get_stream_data("skills.value", stream=form_data_stream)
                        logging.info(skills)
                        # close form
                        args = {
                            "form_id": form_id
                        }
                        worker.write_control(ControlCode.CLOSE_FORM, args, output="FORM")

                        ### DECIDE NEXT STEPS
                        # e.g. ask a question
                        worker.write_data("where do you want to work?", output="QUESTION")

                    else:
                        # save form data
                        path = data["path"]
                        timestamp = worker.get_stream_data(path + ".timestamp", stream=form_data_stream)

                        # TODO: timestamp should be replaced by id to determine order
                        if timestamp is None or data["timestamp"] > timestamp:
                            worker.set_stream_data(
                                path,
                                {
                                    "value": data["value"],
                                    "timestamp": data["timestamp"],
                                },
                                stream=form_data_stream
                            )

                        

            
        return None
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="JOBSEARCHPLANNER", type=str)
    parser.add_argument('--session', type=str)
    parser.add_argument('--properties', type=str)
    parser.add_argument('--loglevel', default="INFO", type=str)
    parser.add_argument('--serve', type=str)
    parser.add_argument('--platform', type=str, default='default')
    parser.add_argument('--registry', type=str, default='default')

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

        af = AgentFactory(_class=JobSearchPlannerAgent, _name=args.serve, _registry=args.registry, platform=platform, properties=properties)
        af.wait()
    else:
        a = None
        session = None
        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = JobSearchPlannerAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = JobSearchPlannerAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()

