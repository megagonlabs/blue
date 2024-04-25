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
        if label == "EOS":
            user_signal = ""
            if worker:
                user_signal = pydash.to_lower(" ".join(worker.get_data(stream)))
            # compute and output to stream
            if pydash.is_equal(user_signal, "knock knock"):
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
                                    "style": {"marginBottom": 15, "fontSize": "15pt"},
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
                                    "nameId": "done",
                                    "large": True,
                                },
                            },
                        ],
                    },
                }
                event_stream = Producer(name="EVENT", properties=self.properties)
                event_stream.start()
                self.stream_injection(interactive_form, event_stream.get_stream())
                logging.info("EVENT_STREAM " + event_stream.get_stream())
                return "INTERACTIVE", interactive_form, "json", False
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
            # worker set stream data, key: first_name, value: rafael
        return None

    def stream_injection(self, form_element: dict, stream: str):
        if "uischema" in form_element:
            self.stream_injection(form_element["uischema"], stream)
        else:
            if "elements" in form_element:
                for element in form_element["elements"]:
                    self.stream_injection(element, stream)
            elif pydash.includes(["Control", "Button"], form_element["type"]):
                pydash.objects.set_(form_element, "props.streamId", stream)


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
