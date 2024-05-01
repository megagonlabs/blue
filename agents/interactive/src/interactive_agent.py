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
from agent import Agent
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
class InteractiveAgent(Agent):
    def __init__(
        self,
        name="INTERACTIVE",
        session=None,
        input_stream=None,
        processor=None,
        properties={},
    ):
        super().__init__(
            name,
            session=session,
            input_stream=input_stream,
            processor=processor,
            properties=properties,
        )
        self.event_stream_consumer = {}

    def default_processor(
        self,
        stream,
        id,
        label,
        data,
        dtype=None,
        tags=None,
        properties=None,
        worker=None,
    ):
        if stream.startswith("EVENT_MESSAGE:"):
            if label == "DATA":
                if worker:
                    # get INTERACTIVE stream
                    interactive_stream = stream[stream.rindex("INTERACTIVE") :]
                    # custom logic for when user is "DONE" with a form
                    if data["name_id"] == "DONE":
                        # check if first_name is set
                        first_name = worker.get_stream_data(
                            stream=interactive_stream, key="first_name.value"
                        )
                        last_name = worker.get_stream_data(
                            stream=interactive_stream, key="last_name.value"
                        )
                        first_name_filled = not pydash.is_empty(
                            pydash.strings.trim(first_name)
                        )
                        last_name_filled = not pydash.is_empty(
                            pydash.strings.trim(last_name)
                        )
                        # close previous form and send a new one asking for last_name
                        interactive_stream_producer = Producer(
                            name="INTERACTIVE", sid=interactive_stream
                        )
                        interactive_stream_producer.start()
                        if not first_name_filled:
                            return (
                                "INTERACTIVE",
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
                                label="INTERACTIVE",
                                data={"type": "DONE", "form_id": data["form_id"]},
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
                                    "INTERACTIVE",
                                    {"type": "JSONFORM", "content": interactive_form},
                                    "json",
                                    False,
                                )
                            elif first_name_filled and last_name_filled:
                                return (
                                    "DATA",
                                    f"Hello, {first_name} {last_name}.",
                                    "str",
                                    True,
                                )
                    else:
                        timestamp = worker.get_stream_data(
                            stream=interactive_stream,
                            key=f'{data["name_id"]}.timestamp',
                        )
                        if timestamp is None or data["timestamp"] > timestamp:
                            worker.set_stream_data(
                                key=data["name_id"],
                                value={
                                    "value": data["value"],
                                    "timestamp": data["timestamp"],
                                },
                                stream=interactive_stream,
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
                    return (
                        "INTERACTIVE",
                        {"type": "JSONFORM", "content": interactive_form},
                        "json",
                        False,
                    )
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
    parser.add_argument("--name", default="INTERACTIVE", type=str)
    parser.add_argument("--session", type=str)
    parser.add_argument("--input_stream", type=str)
    parser.add_argument("--properties", type=str)
    parser.add_argument("--loglevel", default="INFO", type=str)
    parser.add_argument("--serve", default=False, action=argparse.BooleanOptionalAction)

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
        # launch agent with parameters, start session
        def launch(*args, **kwargs):
            logging.info("Launching InteractiveAgent...")
            logging.info(kwargs)
            agent = InteractiveAgent(*args, **kwargs)
            session = agent.start_session()
            logging.info("Started session: " + session.name)
            logging.info("Launched.")
            return session.name

        # launch agent with parameters, join session in keyword args (session=)
        def join(*args, **kwargs):
            logging.info("Launching InteractiveAgent...")
            logging.info(kwargs)
            agent = InteractiveAgent(*args, **kwargs)
            logging.info("Joined session: " + kwargs["session"])
            logging.info("Launched.")
            return kwargs["session"]

        # run rpc server
        rpc = RPCServer(args.name, properties=properties)
        rpc.register(launch)
        rpc.register(join)
        rpc.run()
    else:
        a = None
        session = None
        if args.session:
            # join an existing session
            session = Session(args.session)
            a = InteractiveAgent(name=args.name, session=session, properties=properties)
        elif args.input_stream:
            # no session, work on a single input stream
            a = InteractiveAgent(
                name=args.name, input_stream=args.input_stream, properties=properties
            )
        else:
            # create a new session
            a = InteractiveAgent(name=args.name, properties=properties)
            session = a.start_session()

        # wait for session
        if session:
            session.wait()
