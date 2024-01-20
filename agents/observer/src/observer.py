###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/agent/")
sys.path.append("./lib/platform/")
sys.path.append("./lib/utils/")

import argparse
import csv
import itertools
import json
import logging
import random

###### Parsers, Formats, Utils
import re

######
import time
import uuid

###### Blue
from agent import Agent
from session import Session
from tqdm import tqdm
from websocket import create_connection

# set log level
logging.getLogger().setLevel(logging.INFO)


#######################
class ObserverAgent(Agent):
    def __init__(self, session=None, input_stream=None, processor=None, properties={}):
        super().__init__(
            "OBSERVER",
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
                                        "message": str_data,
                                        "stream": stream,
                                    }
                                )
                            )
                            time.sleep(1)
                            ws.close()
                        else:
                            logging.error(
                                "{} [{}]: {}".format(stream, ",".join(tags), str_data)
                            )

        elif label == "BOS":
            # init stream to empty array
            if worker:
                worker.set_data(stream, [])
            pass
        elif label == "DATA":
            # store data value
            # logging.error(value)
            if dtype == "json":
                logging.error("{} [{}]: {}".format(stream, ",".join(tags), value))
            else:
                if worker:
                    worker.append_data(stream, str(value))

        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", type=str)
    parser.add_argument("--input_stream", type=str)
    parser.add_argument("--properties", type=str)
    parser.add_argument("--loglevel", default="ERROR", type=str)

    args = parser.parse_args()

    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())

    session = None
    a = None

    # set properties
    properties = {}
    p = args.properties

    if p:
        # decode json
        properties = json.loads(p)

    if args.session:
        # join an existing session
        session = Session(args.session)
        a = ObserverAgent(session=session, properties=properties)
    elif args.input_stream:
        # no session, work on a single input stream
        a = ObserverAgent(input_stream=args.input_stream, properties=properties)
    else:
        # create a new session
        a = ObserverAgent(properties=properties)
        a.start_session()

    # wait for session
    session.wait()
