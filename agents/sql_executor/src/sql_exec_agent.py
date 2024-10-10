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
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s",
    level=logging.ERROR,
    datefmt="%Y-%m-%d %H:%M:%S",
)

#######################
class SQLExecutorAgent(Agent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "SQL_EXEC"
        super().__init__(**kwargs)

    def _initialize(self, properties=None):
        super()._initialize(properties=properties)
        platform_id = self.properties["platform.name"]
        prefix = 'PLATFORM:' + platform_id
        self.registry = DataRegistry(id=self.properties['data_registry.name'], prefix=prefix,
                                     properties=self.properties)
        # TODO: replace hardcoding source with None and employ data discovery
        self.source = '/employer_postgres/postgres/public'

    def _start(self):
        super()._start()


    def execute_sql_query(self, query):
        try:
            logging.info(self.source)
            _, source, db, collection = self.source.split('/')
            source_db = self.registry.connect_source(source)
            cursor = source_db._db_connect(db).cursor()
            # Note: collection refers to schema in postgres (the level between database and table)
            cursor.execute(f'SET search_path TO {collection}')
            cursor.execute(query)
            records = cursor.fetchall()
            logging.info(len(records))
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(records, columns=columns)
            result = df.to_dict('records')
        except Exception as e:
            error = str(e)
        return result
    
    def default_processor(self, message, input="DEFAULT", properties=None, worker=None):

        ##### Upon USER/Agent input text
        if input == "DEFAULT":
            if message.isEOS():
                # get all data received from user stream
                stream = message.getStream()

                logging.info(message.getData())
                query = " ".join(worker.get_data(stream))
                logging.info("query: "  + query)
                
                if worker:
                    result = self.execute_sql_query(query)
                    worker.write_data(result)
                    worker.write_eos()
                    return

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

                # append to private stream data
                if worker:
                    worker.append_data(stream, data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="SQL_EXEC", type=str)
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

        af = AgentFactory(_class=SQLExecutorAgent, _name=args.serve, _registry=args.registry, platform=platform,
                          properties=properties)
        af.wait()
    else:
        a = None
        session = None

        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = SQLExecutorAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = SQLExecutorAgent(name=args.name, session=session, properties=properties)

        # wait for session
        if session:
            session.wait()
