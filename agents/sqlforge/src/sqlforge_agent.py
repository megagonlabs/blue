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


# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s",
    level=logging.ERROR,
    datefmt="%Y-%m-%d %H:%M:%S",
)


#######################
class SQLForgeAgent(Agent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "SQLFORGE"
        super().__init__(**kwargs)

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
            # compute stream data
            text_query = ""
            if worker:
                text_query = " ".join(worker.get_data("text_query"))

            logging.info("Translating text query: " + text_query)
            # TODO: Do SQL translation here
            sql_query = self.compute_sql_query(text_query)

            # output to stream
            return sql_query
        elif label == "BOS":
            # init stream to empty array
            if worker:
                worker.set_data("text_query", [])
            pass
        elif label == "DATA":
            # store data value
            logging.info(data)

            if worker:
                worker.append_data("text_query", data)

        return None

    def compute_sql_query(self, text_query):
        # TODO: Do SQL translation here
        return "SELECT * FROM CITY"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="SQLFORGE", type=str)
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
        
        af = AgentFactory(agent_class=SQLForgeAgent, agent_name=args.serve, agent_registry=args.registry, platform=platform, properties=properties)
        af.wait()
    else:
        a = None
        session = None

        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = SQLForgeAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = SQLForgeAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()
