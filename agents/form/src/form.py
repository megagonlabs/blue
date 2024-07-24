###### OS / Systems
import os
import sys

import pydash

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
import uuid
import random

###### Parsers, Formats, Utils
import re
import csv
import json

import itertools
from tqdm import tqdm

###### Blue
from agent import Agent, AgentFactory
from session import Session
from producer import Producer
from consumer import Consumer
from message import Message, MessageType, ContentType, ControlCode

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s",
    level=logging.ERROR,
    datefmt="%Y-%m-%d %H:%M:%S",
)


#######################
class FormAgent(Agent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "FORM"
        super().__init__(**kwargs)

    def triggered(self, text, properties):
        # if instructed, consider it triggered
        if 'instructable' in properties:
            if properties['instructable']:
                return True
            
        triggers = properties['triggers']
        for trigger in triggers:
            if trigger.lower() in text.lower():
                return True
        return False

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        stream = message.getStream()

        if input == "EVENT":
            if message.isData():
                if worker:
                    data = message.getData()
                    stream = message.getStream()
                    form_id = data["form_id"]
                    action = data["action"]

                    # when the user clicked DONE
                    if action == "DONE":
                        # gather all data in the form from stream memory
                        schema = properties['schema']['properties'].keys()

                        form_data = {}
                        for element in schema:
                            form_data[element] = worker.get_stream_data(stream=stream, key=element + ".value")

            
                        # close form
                        args = {
                            "form_id": form_id
                        }
                        worker.write_control(ControlCode.CLOSE_FORM, args, output="FORM")

                        # stream form data
                        return form_data
                    
                    else:
                        timestamp = worker.get_stream_data(stream=stream, key=f'{data["path"]}.timestamp')

                        # TODO: timestamp should be replaced by id to determine order
                        if timestamp is None or data["timestamp"] > timestamp:
                            # save data into stream memory
                            worker.set_stream_data(
                                key=data["path"],
                                value={
                                    "value": data["value"],
                                    "timestamp": data["timestamp"],
                                },
                                stream=stream,
                            )
        else:
            if message.isEOS():
                stream_message = ""
                if worker:
                    stream_message = pydash.to_lower(" ".join(worker.get_data(stream)))

                # check trigger condition, and output to stream form UI when triggered
                if self.triggered(stream_message, properties):
                    args = {
                        "schema": properties['schema'],
                        "uischema": {
                            "type": "VerticalLayout",
                            "elements": [
                                properties['form'],
                                {
                                    "type": "Button",
                                    "label": "Submit",
                                    "props": {
                                        "intent": "success",
                                        "action": "DONE",
                                        "large": True,
                                    },
                                },
                            ],
                        },
                    }
                    # write ui
                    worker.write_control(ControlCode.CREATE_FORM, args, output="FORM")

            elif message.isBOS():
                # init stream to empty array
                if worker:
                    worker.set_data(stream, [])
                pass
            elif message.isData():
                # store data value
                data = message.getData()
                logging.info(data)

                if worker:
                    worker.append_data(stream, data)
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="FORM", type=str)
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

        af = AgentFactory(
            agent_class=FormAgent,
            agent_name=args.serve,
            agent_registry=args.registry,
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
            a = FormAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = FormAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()
