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
class FormAgent(Agent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "FORM"
        super().__init__(**kwargs)

    def triggered(self, text, properties):
        triggers = properties['triggers']
        for trigger in triggers:
            if trigger.lower() in text.lower():
                return True
        return False 
    
    def default_processor(self, stream, id, label, data, dtype=None, tags=None, properties=None, worker=None):
        if ":EVENT_MESSAGE:" in stream:
            if label == "DATA":
                if worker:
                   
                    output_stream_cid = stream[:stream.rindex("EVENT_MESSAGE")-1] 

                    # when the user clicked DONE
                    if data["name_id"] == "DONE":
                        # gather all data in the form from stream memory
                        schema = properties['schema']['properties'].keys()

                        json_data = {}
                        for element in schema:
                            json_data[element] = worker.get_stream_data(stream=output_stream_cid, key = element + ".value")

            
                        # get output stream with original form
                        output_stream = Producer(cid=output_stream_cid, properties=properties)
                        output_stream.start()

                        # close form
                        output_stream.write(
                            label="INTERACTION",
                            data={
                                "type": "DONE",
                                "form_id": data["form_id"],
                            },
                            dtype="json",
                        )

                        # stream form data
                        return ("DATA", json_data, "json", True)
                    else:
                        timestamp = worker.get_stream_data(
                            stream=output_stream_cid, key=f'{data["name_id"]}.timestamp'
                        )

                        # TODO: timestamp should be replaced by id to determine order
                        if timestamp is None or data["timestamp"] > timestamp:
                            # save data into stream memory
                            worker.set_stream_data(
                                key=data["name_id"],
                                value={
                                    "value": data["value"],
                                    "timestamp": data["timestamp"],
                                },
                                stream=output_stream_cid,
                            )
        else:
            if label == "EOS":
                stream_message = ""
                if worker:
                    stream_message = pydash.to_lower(" ".join(worker.get_data(stream)))

                # check trigger condition, and output to stream form UI when triggered
                if self.triggered(stream_message, properties):
                    interactive_form = {
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
    parser.add_argument('--name', default="FORM", type=str)
    parser.add_argument('--session', type=str)
    parser.add_argument('--input_stream', type=str)
    parser.add_argument('--properties', type=str)
    parser.add_argument('--loglevel', default="INFO", type=str)
    parser.add_argument('--serve', type=str, default='FORM')
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
            session = Session(args.session)
            a = FormAgent(name=args.name, session=session, properties=properties)
        elif args.input_stream:
            # no session, work on a single input stream
            a = FormAgent(name=args.name, input_stream=args.input_stream, properties=properties)
        else:
            # create a new session
            a = FormAgent(name=args.name, properties=properties)
            session = a.start_session()

        # wait for session
        if session:
            session.wait()
