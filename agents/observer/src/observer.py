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
from rpc import RPCServer

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s",
    level=logging.ERROR,
    datefmt="%Y-%m-%d %H:%M:%S",
)


#######################
class ObserverAgent(Agent):
    def __init__(
        self,
        name="OBSERVER",
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
        value,
        dtype=None,
        tags=None,
        properties=None,
        worker=None,
    ):
        if label == "EOS":
            # compute stream data
            l = 0
            if dtype == "json":
                pass
            else:
                if worker:
                    data = worker.get_data(stream)
                    str_data = str(" ".join(data))
                    if len(str_data.strip()) > 0:
                        if (
                            "output" in properties
                            and properties["output"] == "websocket"
                        ):
                            ws = create_connection(properties["websocket"])
                            ws.send(
                                json.dumps(
                                    {
                                        "type": "OBSERVER_SESSION_MESSAGE",
                                        "session_id": properties["session_id"],
                                        "message": {
                                            "type": "STRING",
                                            "content": str_data,
                                        },
                                        "stream": stream,
                                    }
                                )
                            )
                            time.sleep(1)
                            ws.close()
                        else:
                            logging.info(
                                "{} [{}]: {}".format(stream, ",".join(tags), str_data)
                            )
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
        elif label.startswith("INTERACTIVE"):
            # interactive messages
            if "output" in properties and properties["output"] == "websocket":
                ws = create_connection(properties["websocket"])
                ws.send(
                    json.dumps(
                        {
                            "type": "OBSERVER_SESSION_MESSAGE",
                            "session_id": properties["session_id"],
                            "message": {
                                "type": label,
                                "content": value,
                            },
                            "stream": stream,
                        }
                    )
                )
                time.sleep(1)
                ws.close()

        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="OBSERVER", type=str)
    parser.add_argument("--session", type=str)
    parser.add_argument("--input_stream", type=str)
    parser.add_argument("--properties", type=str)
    parser.add_argument("--loglevel", default="ERROR", type=str)
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
        elif args.input_stream:
            # no session, work on a single input stream
            a = ObserverAgent(
                name=args.name, input_stream=args.input_stream, properties=properties
            )
        else:
            # create a new session
            a = ObserverAgent(name=args.name, properties=properties)
            session = a.start_session()

        # wait for session
        if session:
            session.wait()
