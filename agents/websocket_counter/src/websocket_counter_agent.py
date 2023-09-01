###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/shared/')

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

# set log level
logging.getLogger().setLevel(logging.INFO)

#######################
class CounterAgent(Agent):
    def __init__(self, session=None, input_stream=None, processor=None, properties={}):
        super().__init__("COUNTER", session=session, input_stream=input_stream, processor=processor, properties=properties)
        
        
    def _initialize_properties(self):
        super()._initialize_properties()

        self.properties['counter.service'] = "ws://localhost:8002"

    def default_processor(self, stream, id, event, value, properties=None, worker=None):
        if event == 'EOS':
            # get all data received from stream
            stream_data = ""
            if worker:
                stream_data = worker.get_data('stream')
                stream_data = stream_data[0] 

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

        elif event == 'BOS':
            # init stream to empty array
            if worker:
                worker.set_data('stream',[])
            pass
        elif event == 'DATA':
            # store data value
            logging.info(value)
            
            if worker:
                worker.append_data('stream',value)
    
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
    parser.add_argument('--session', type=str)
    parser.add_argument('--input_stream', type=str)
    parser.add_argument('--properties', type=str)
 
    args = parser.parse_args()

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
        a = CounterAgent(session=session, properties=properties)
    elif args.input_stream:
        # no session, work on a single input stream
        a = CounterAgent(input_stream=args.input_stream, properties=properties)
    else:
        # create a new session
        a = CounterAgent(properties=properties)
        a.start_session()


    # wait for session
    session.wait()