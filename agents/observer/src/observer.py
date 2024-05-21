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

    def default_processor(self, stream, id, label, value, dtype=None, tags=None, properties=None, worker=None):
        base_message = {
            "type": "OBSERVER_SESSION_MESSAGE",
            "session_id": properties["session_id"],
            "connection_id": properties["connection_id"],
            "message": {"type": label, "content": value},
            "stream": stream,
            "timestamp": str(id).split("-")[0],
        }
        if label == "EOS":
            # compute stream data
            l = 0
            if dtype == "json":
                pass
            else:
                if worker:
                    data = worker.get_data(stream)
                    str_data = ""
                    if data is not None:
                        str_data = str(" ".join(data))
                    if len(str_data.strip()) > 0:
                        if "output" in properties and properties["output"] == "websocket":
                            ws = create_connection(properties["websocket"])
                            ws.send(json.dumps({**base_message, "message": {"type": "STRING", "content": str_data}}))
                            time.sleep(1)
                            ws.close()
                        else:
                            logging.info("{} [{}]: {}".format(stream, ",".join(tags), str_data))
        elif label == "BOS":
            # init stream to empty array
            if worker:
                worker.set_data(stream, [])
            pass
        elif label == "DATA":
            # store data value
            if dtype == "json":
                logging.info("{} [{}]: {}".format(stream, ",".join(tags), value))
            else:
                if worker:
                    worker.append_data(stream, str(value))
        elif label == "INTERACTION":
            # interactive messages
            if "output" in properties and properties["output"] == "websocket":
                ws = create_connection(properties["websocket"])
                ws.send(json.dumps(base_message))
                time.sleep(1)
                ws.close()

        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="OBSERVER", type=str)
    parser.add_argument("--session", type=str)
    parser.add_argument("--properties", type=str)
    parser.add_argument("--loglevel", default="INFO", type=str)
    parser.add_argument("--serve", type=str, default="OBSERVER")
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
            session = Session(args.session)
            a = ObserverAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            a = ObserverAgent(name=args.name, properties=properties)
            session = a.start_session()

        # wait for session
        if session:
            session.wait()
