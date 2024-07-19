###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/agent/")
sys.path.append("./lib/platform/")
sys.path.append("./lib/utils/")

######
import time
import argparse
import logging
import uuid
import random

###### Parsers, Formats, Utils
import re
import csv
import json
from utils import json_utils

import itertools
from tqdm import tqdm

###### Blue
from agent import Agent, AgentFactory
from session import Session
from tqdm import tqdm
from websocket import create_connection
from message import Message, MessageType, ContentType, ControlCode, MessageEncoder


# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s",
    level=logging.ERROR,
    datefmt="%Y-%m-%d %H:%M:%S",
)


#######################
class ObserverAgent(Agent):
    def __init__(self, **kwargs):
        if "name" not in kwargs:
            kwargs["name"] = "OBSERVER"
        super().__init__(**kwargs)

    def response_handler(self, stream,  properties=None, message={}):
        try:
            output = {}
            if "output" in properties:
                output = properties["output"]
            if output.get('type') == "websocket":
                ws = create_connection(output.get("websocket"))
                ws.send(json.dumps(message))
                ws.close()
            else:
                logging.info("{} : {}".format(stream, message))
        except Exception as exception:
            logging.error("{}: {}".format(stream, exception))

    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):
        mode = None
        if 'output' in properties:
            mode = properties['output'].get('mode', 'batch')

        id = message.getID()
        stream = message.getStream()

        message_json = json.loads(message, cls=MessageEncoder)
        label = message_json["label"]
        contents = message_json["contents"]
        content_type = message_json["content_type"]

        base_message = {
            "type": "OBSERVER_SESSION_MESSAGE",
            "session_id": properties["session_id"],
            "connection_id": properties["connection_id"],
            # TODO: REPLACE WITH BELOW
            # "message": {"label": label, "contents": contents, "content_type": content_type},
            "message": {"label": label, "content": contents, "dtype": content_type},
            "stream": stream,
            "mode": mode,
            "timestamp": int(id.split("-")[0]),
            "order": int(id.split("-")[1]),
            "id": id,
        }
        if message.isEOS():
            # compute stream data
            if worker:
                if mode == 'batch':
                    data = worker.get_data(stream)
                    stream_dtype = worker.get_data(f'{stream}:content_type')
                    if stream_dtype == 'json' and data is not None:
                        try:
                            self.response_handler(
                                stream=stream,
                                properties=properties,
                                # TODO: REPLACE WITH BELOW
                                # TODO: Why is label JSON? 
                                # message={**base_message, "message": {**base_message['message'], "label": "JSON", "contents": [json.loads(json_data) for json_data in data]}},
                                message={**base_message, "message": {**base_message['message'], "label": "JSON", "content": [json.loads(json_data) for json_data in data]}},
                            )
                        except Exception as exception:
                            logging.error("{} : {}".format(stream, exception))
                    else:
                        str_data = ""
                        if data is not None:
                            # convert elements inside data list into string format
                            str_data = str(" ".join(map(str, data)))
                        if len(str_data.strip()) > 0:
                            self.response_handler(
                                stream=stream,
                                properties=properties,
                                # TODO: REPLACE WITH BELOW
                                # TODO: Why is label TEXT? 
                                message={**base_message, "message": {**base_message['message'], "label": "TEXT", "contents": str_data}},
                            )
                elif mode == 'streaming':
                    self.response_handler(stream=stream, properties=properties, message=base_message)
        elif message.isBOS():
            # init stream to empty array
            if worker:
                if mode == 'batch':
                    worker.set_data(stream, [])
                elif mode == 'streaming':
                    self.response_handler(stream=stream, properties=properties, message=base_message)
        elif message.isData():
            # store data value
            data = message.getData()
            
            if worker:
                if mode == 'batch':
                    worker.set_data(f'{stream}:content_type', content_type)
                    worker.append_data(stream, str(data))
                elif mode == 'streaming':
                    self.response_handler(stream=stream, properties=properties, message=base_message)
        elif message.getCode() in [ControlCode.CREATE_FORM, ControlCode.UPDATE_FORM, ControlCode.CLOSE_FORM]:
            # interactive messages
            self.response_handler(stream=stream, properties=properties, message=base_message)

        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="OBSERVER", type=str)
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
            agent_class=ObserverAgent,
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
            a = ObserverAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = ObserverAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()
