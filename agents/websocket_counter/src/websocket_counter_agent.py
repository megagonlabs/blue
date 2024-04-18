###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/agent/')
sys.path.append('./lib/platform/')
sys.path.append('./lib/utils/')

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

###### Communication
import asyncio
from websockets.sync.client import connect


###### Blue
from agent import Agent
from session import Session
from rpc import RPCServer

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


#######################
class CounterAgent(Agent):
    def __init__(self, name="WEBSOCKET_COUNTER", session=None, input_stream=None, processor=None, properties={}):
        super().__init__(name, session=session, input_stream=input_stream, processor=processor, properties=properties)
        
        
    def _initialize_properties(self):
        super()._initialize_properties()

        self.properties['counter.service'] = "ws://localhost:8002"

    def default_processor(self, stream, id, label, data, dtype=None, tags=None, properties=None, worker=None):
        if label == 'EOS':
            # get all data received from stream
            stream_data = ""
            if worker:
                stream_data = worker.get_data('stream')

            #### call service to compute

            # create message, copying API specific properties
            input_data = " ".join(stream_data)
            
            logging.info(input_data)
            message = input_data

            # serialize message, call service
            m = json.dumps(message)
            r = self.call_service(m)

            response = json.loads(r)

            # create output from response
            output_data = int(response)
            logging.info(output_data)
            return output_data

        elif label == 'BOS':
            # init stream to empty array
            if worker:
                worker.set_data('stream',[])
            pass
        elif label == 'DATA':
            # store data value
            logging.info(data)
            
            if worker:
                worker.append_data('stream',data)
    
        return None

    def get_service_address(self):
        service_address = self.properties['counter.service']
        
        return service_address

    def call_service(self, data):
        with connect(self.get_service_address()) as websocket:
            logging.info("Sending to service: {data}".format(data=data))
            websocket.send(data)
            message = websocket.recv()
            logging.info("Received from service: {message}".format(message=message))
            return message

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default="WEBSOCKET_COUNTER", type=str)
    parser.add_argument('--session', type=str)
    parser.add_argument('--input_stream', type=str)
    parser.add_argument('--properties', type=str)
    parser.add_argument('--loglevel', default="INFO", type=str)
    parser.add_argument('--serve', default=False, action=argparse.BooleanOptionalAction)
 
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
            logging.info("Launching WebSocket_CounterAgent...")
            logging.info(kwargs)
            agent = CounterAgent(*args, **kwargs)
            session = agent.start_session()
            logging.info("Started session: " + session.name)
            logging.info("Launched.")
            return session.name

        # launch agent with parameters, join session in keyword args (session=)
        def join(*args, **kwargs):
            logging.info("Launching WebSocket_CounterAgent...")
            logging.info(kwargs)
            agent = CounterAgent(*args, **kwargs)
            logging.info("Joined session: " + kwargs['session'])
            logging.info("Launched.")
            return kwargs['session']

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
            a = CounterAgent(name=args.name, session=session, properties=properties)
        elif args.input_stream:
            # no session, work on a single input stream
            a = CounterAgent(name=args.name, input_stream=args.input_stream, properties=properties)
        else:
            # create a new session
            a = CounterAgent(name=args.name, properties=properties)
            session = a.start_session()

        # wait for session
        if session:
            session.wait()


