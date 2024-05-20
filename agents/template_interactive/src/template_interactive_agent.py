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
from rpc import RPCServer

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s",
    level=logging.ERROR,
    datefmt="%Y-%m-%d %H:%M:%S",
)


#######################
class TemplateInteractiveAgent(Agent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "TEMPLATE_INTERACTIVE"
        super().__init__(**kwargs)

    def default_processor(self, stream, id, label, data, dtype=None, tags=None, properties=None, worker=None):
        if ":EVENT_MESSAGE:" in stream:
            if label == "DATA":
                if worker:
                    # get INTERACTION stream
                    # TODO: Instead of figuring out the stream where the ui resided, it should be in the message..

                    interaction_stream = stream[:stream.rindex("EVENT_MESSAGE")-1] 

                    # when the user clicked DONE
                    if data["name_id"] == "DONE":
                        # gather all data, check if first_name is set
                        first_name = worker.get_stream_data(stream=interaction_stream, key="first_name.value")
                        last_name = worker.get_stream_data(stream=interaction_stream, key="last_name.value")
                        first_name_filled = not pydash.is_empty(pydash.strings.trim(first_name))
                        last_name_filled = not pydash.is_empty(pydash.strings.trim(last_name))
                        
                        # close previous form and send a new one asking for last_name, in a new form
                        interactive_stream_producer = Producer(cid=interaction_stream, properties=properties)
                        interactive_stream_producer.start()

                        if not first_name_filled:
                            return (
                                "INTERACTION",
                                {
                                    "type": "CALLOUT",
                                    "content": {
                                        "message": "First name cannot be empty.",
                                        "intent": "warning",
                                    },
                                },
                                "json",
                                False,
                            )
                        else:
                            interactive_stream_producer.write(
                                label="INTERACTION",
                                data={
                                    "type": "DONE",
                                    "form_id": data["form_id"],
                                },
                                dtype="json",
                            )
                            if first_name_filled and not last_name_filled:
                                interactive_form = {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"last_name": {"type": "string"}},
                                    },
                                    "uischema": {
                                        "type": "VerticalLayout",
                                        "elements": [
                                            {
                                                "type": "Label",
                                                "label": f"{first_name} who?",
                                                "props": {
                                                    "large": True,
                                                    "style": {
                                                        "marginBottom": 15,
                                                        "fontSize": "15pt",
                                                    },
                                                },
                                            },
                                            {
                                                "type": "HorizontalLayout",
                                                "elements": [
                                                    {
                                                        "type": "Control",
                                                        "label": "Last Name",
                                                        "scope": "#/properties/last_name",
                                                    }
                                                ],
                                            },
                                            {
                                                "type": "Button",
                                                "label": "Done",
                                                "props": {
                                                    "intent": "success",
                                                    "nameId": "DONE",
                                                    "large": True,
                                                },
                                            },
                                        ],
                                    },
                                }
                                return (
                                    "INTERACTION",
                                    {
                                        "type": "JSONFORM",
                                        "content": interactive_form,
                                    },
                                    "json",
                                    False,
                                )
                            elif first_name_filled and last_name_filled:
                                return ("DATA", f"Hello, {first_name} {last_name}.", "str", True)
                    else:
                        timestamp = worker.get_stream_data(
                            stream=interaction_stream, key=f'{data["name_id"]}.timestamp'
                        )
                        if timestamp is None or data["timestamp"] > timestamp:
                            worker.set_stream_data(
                                key=data["name_id"],
                                value={
                                    "value": data["value"],
                                    "timestamp": data["timestamp"],
                                },
                                stream=interaction_stream,
                            )
        else:
            if label == "EOS":
                stream_message = ""
                if worker:
                    stream_message = pydash.to_lower(" ".join(worker.get_data(stream)))
                # compute and output to stream
                if pydash.is_equal(stream_message, "knock knock"):
                    interactive_form = {
                        "schema": {
                            "type": "object",
                            "properties": {"first_name": {"type": "string"}},
                        },
                        "uischema": {
                            "type": "VerticalLayout",
                            "elements": [
                                {
                                    "type": "Label",
                                    "label": "Who's there?",
                                    "props": {
                                        "large": True,
                                        "style": {
                                            "marginBottom": 15,
                                            "fontSize": "15pt",
                                        },
                                    },
                                },
                                {
                                    "type": "HorizontalLayout",
                                    "elements": [
                                        {
                                            "type": "Control",
                                            "label": "First Name",
                                            "scope": "#/properties/first_name",
                                        }
                                    ],
                                },
                                {
                                    "type": "Button",
                                    "label": "Done",
                                    "props": {
                                        "intent": "success",
                                        "nameId": "DONE",
                                        "large": True,
                                    },
                                },
                            ],
                        },
                    }
                    return ("INTERACTION", {"type": "JSONFORM", "content": interactive_form}, "json", False)
            elif label == "BOS":
                # init stream to empty array
                if worker:
                    worker.set_data(stream, [])
                pass
            elif label == "DATA":
                # store data value
                logging.info(data)

                if worker:
                    worker.append_data(stream, data)
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="TEMPLATE_INTERACTIVE", type=str)
    parser.add_argument('--session', type=str)
    parser.add_argument('--input_stream', type=str)
    parser.add_argument('--properties', type=str)
    parser.add_argument('--loglevel', default="INFO", type=str)
    parser.add_argument('--serve', type=str, default='TEMPLATE_INTERACTIVE')
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
            agent_class=TemplateInteractiveAgent,
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
            session = Session(args.session)
            a = TemplateInteractiveAgent(name=args.name, session=session, properties=properties)
        elif args.input_stream:
            # no session, work on a single input stream
            a = TemplateInteractiveAgent(name=args.name, input_stream=args.input_stream, properties=properties)
        else:
            # create a new session
            a = TemplateInteractiveAgent(name=args.name, properties=properties)
            session = a.start_session()

        # wait for session
        if session:
            session.wait()
