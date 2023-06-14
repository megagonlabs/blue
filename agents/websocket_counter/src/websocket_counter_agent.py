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

def call_service(data):
    with connect("ws://localhost:8001") as websocket:
        logging.info("Sending to service: {data}".format(data=data))
        websocket.send(data)
        message = websocket.recv()
        logging.info("Received from service: {message}".format(message=message))
        return int(message)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--session', type=str)
    parser.add_argument('--input_stream', type=str)
 
    args = parser.parse_args()


    session = None
    a = None


    stream_data = []



    # sample func to process data
    def processor(id, event, data):
        if event == 'EOS':
            # print all data received from stream
            print(stream_data)

            # call service to compute
            m = call_service(" ".join(stream_data))
           
            # output to stream
            return m
           
        elif event == 'DATA':
            # store data value
            stream_data.append(data)
        
        return None

    if args.session:
        # join an existing session
        session = Session(args.session)
        a = CounterAgent(session=session, processor=processor)
    elif args.input_stream:
        # no session, work on a single input stream
        a = CounterAgent(input_stream=args.input_stream, processor=processor)
    else:
        # create a new session
        a = CounterAgent(processor=processor)
        a.start_session()


    # wait for session
    session.wait()