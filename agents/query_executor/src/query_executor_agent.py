###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/agent/")
sys.path.append('./lib/openai/')
sys.path.append("./lib/platform/")
sys.path.append("./lib/utils/")
sys.path.append('./lib/data_registry/')

######
import time
import argparse
import logging
import time
import uuid
import random
import pandas as pd

###### Parsers, Formats, Utils
import re
import csv
import json

import itertools
from tqdm import tqdm

###### Blue
from agent import Agent, AgentFactory
from data_registry import DataRegistry
from session import Session
from message import Message, MessageType, ContentType, ControlCode

# set log level
logging.getLogger().setLevel(logging.ERROR)
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s",
    level=logging.ERROR,
    datefmt="%Y-%m-%d %H:%M:%S",
)

#######################
class QueryExecutorAgent(Agent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "QUERYEXECUTOR"
        super().__init__(**kwargs)

    def _initialize(self, properties=None):
        super()._initialize(properties=properties)

        # create instance of data registry
        platform_id = self.properties["platform.name"]
        prefix = 'PLATFORM:' + platform_id
        self.registry = DataRegistry(id=self.properties['data_registry.name'], prefix=prefix,
                                     properties=self.properties)

    def _start(self):
        super()._start()


    def execute_sql_query(self, path, query):
        result = None
        question = None
        error = None
        try:
            # extract source, database, collection
            _, source, database, collection = path.split('/')
            # connect
            source_connection  = self.registry.connect_source(source)
            # execute query
            result = source_connection.execute_query(query, database=database, collection=collection)
        except Exception as e:
            error = str(e)

        return {
            'question': question,
            'source': path,
            'query': query,
            'result': result,
            'error': error
        }
    
    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):

        ##### Upon USER/Agent input text
        if input == "DEFAULT":
            if message.isEOS():
                # get all data received from user stream
                stream = message.getStream()

                # extract json
                input = " ".join(worker.get_data(stream))

                # logging.info("input: "  + input)
                
                if worker:
                    try:
                        data = json.loads(input)
                    except:
                        logging.error("Input is not JSON")
                        return

                    # extract path, query
                    path = data['source']
                    query = data['query']
                    result = self.execute_sql_query(path, query)
                    return [result, message.EOS]
                
            elif message.isBOS():
                stream = message.getStream()

                # init private stream data to empty array
                if worker:
                    worker.set_data(stream, [])
                pass
            elif message.isData():
                # store data value
                data = message.getData()
                stream = message.getStream()

                if message.getContentType() == ContentType.JSON:
                    # extract path, query
                    path = data['source']
                    query = data['query']
                    result = self.execute_sql_query(path, query)
                    return [result, message.EOS]
                else:
                    # append to private stream data
                    if worker:
                        worker.append_data(stream, data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="QUERYEXECUTOR", type=str)
    parser.add_argument('--session', type=str)
    parser.add_argument('--properties', type=str)
    parser.add_argument('--loglevel', default="INFO", type=str)
    parser.add_argument('--serve', type=str)
    parser.add_argument('--platform', type=str, default='default')
    parser.add_argument('--registry', type=str, default='default')

    args = parser.parse_args()

    for i in range(10):
        print('qwer' * 100 + str(i))

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

        af = AgentFactory(_class=QueryExecutorAgent, _name=args.serve, _registry=args.registry, platform=platform,
                          properties=properties)
        af.wait()
    else:
        a = None
        session = None

        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = QueryExecutorAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = QueryExecutorAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()