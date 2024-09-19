###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/agent/')
sys.path.append('./lib/platform/')
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

import itertools
from tqdm import tqdm

###### Communication
import asyncio
from websockets.sync.client import connect


###### Blue
from agent import Agent, AgentFactory
from session import Session
from message import Message, MessageType, ContentType, ControlCode


# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")

class PromptOptimizerAgent(Agent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "PROMPTOPTIMIZER"
        super().__init__(**kwargs)


    def _initialize(self, properties=None):
        super()._initialize(properties=properties)

    def _initialize_properties(self):
        super()._initialize_properties()

        self.properties['dspy.service'] = "ws://localhost:8001"
        self.properties['prompt_model'] = "gpt-4o-mini"
        self.properties['task_model'] = "task_model"
        self.properties['num_candidates'] = 5
        self.properties['temperature'] = 0.7
        self.properties['max_bootstrapped_demos'] = 4
        self.properties['max_labeled_demos'] = 4 
        self.properties['num_trials'] = 5


    def optimize(self, examples):
        prompt = "Optimizing"
        return prompt

    def build_optimizer_form(self):
        # design form
        examples_ui = {
            "type": "Control",
            "scope": "#/properties/examples",
            "options": {
                "detail": {
                    "type": "VerticalLayout",
                    "elements": [
                        {"type": "Label", "label": "Examples"},
                        {
                            "type": "HorizontalLayout",
                            "elements": [
                                {
                                    "type": "Control",
                                    "scope": "#/properties/text",
                                },
                                {
                                    "type": "Control",
                                    "scope": "#/properties/annotation",
                                },
                            ],
                        },
                    ],
                }
            }
        }

        form_ui = {
            "type": "VerticalLayout",
            "elements": [
                {
                    "type": "Label",
                    "label": "Prompt Optimizer",
                    "props": {"style": {"fontWeight": "bold"}},
                },
                {
                    "type": "Label",
                    "label": f"Provide text examples and annotations",
                    "props": {
                        "muted": True,
                        "style": {"marginBottom": 15, "fontStyle": "italic"},
                    },
                },
                { "type": "VerticalLayout", "elements": [examples_ui] },
                {
                    "type": "Button",
                    "label": "Optimize",
                    "props": {
                        "intent": "success",
                        "action": "DONE",
                        "large": True,
                    },
                },
            ]
        }

        form_schema = {
            "type": "object",
            "properties": {
                "examples": {
                    "type": "array",
                    "title": "Examples",
                    "items": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "annotation": {"type": "string"},
                        },
                    },
                }
            },
        }

        form = {
            "schema": form_schema,
            "data": {"examples": []},
            "uischema": form_ui,
        }
        return form

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        if input == "DEFAULT":
            if message.isEOS():
                # compute stream data
                stream_data = ""
                if worker:
                    stream_data = " ".join(worker.get_data('stream_data'))

                optimizer_form = self.build_optimizer_form()
                if worker:
                    worker.write_control(
                        ControlCode.CREATE_FORM, optimizer_form, output="FORM"
                    )
            
            elif message.isBOS():
                # init stream to empty array
                if worker:
                    worker.set_data('stream_data',[])
                pass
            elif message.isData():
                # store data value
                data = message.getData()
                logging.info(data)
                
                if worker:
                    worker.append_data('stream_data', data)
        elif input == "EVENT":
            if message.isData():
                if worker:
                    data = message.getData()
                    stream = message.getStream()
                    form_id = data["form_id"]
                    action = data["action"]

                    # get form stream
                    form_data_stream = stream.replace("EVENT", "OUTPUT:FORM")

                    # when the user clicked DONE
                    if action == "DONE":
                        # get form data
                        examples = worker.get_stream_data(
                            "examples.value", stream=form_data_stream
                        )
                        logging.info(examples)

                        # close form
                        args = {"form_id": form_id}
                        worker.write_control(
                            ControlCode.CLOSE_FORM, args, output="FORM"
                        )

                        ### OPTIMIZE
                        return self.optimize(examples)

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
    
        return None
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="PROMPTOPTIMIZER", type=str)
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
        
        af = AgentFactory(_class=PromptOptimizerAgent, _name=args.serve, _registry=args.registry, platform=platform, properties=properties)
        af.wait()
    else:
        a = None
        session = None
        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = PromptOptimizerAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = PromptOptimizerAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()



