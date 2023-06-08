###### OS / Systems
import os
import sys

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

# set log level
logging.getLogger().setLevel(logging.INFO)

#######################
class MyAgent(Agent):
    def __init__(self, name, stream, processor=None, properties={}):
        super().__init__(name, stream, processor=processor, properties=properties)

def call_service(data):
    with connect("ws://localhost:8001") as websocket:
        logging.info("Sending to service: {data}".format(data=data))
        websocket.send(data)
        message = websocket.recv()
        logging.info("Received from service: {message}".format(message=message))
        return int(message)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, default='AGENT')
    parser.add_argument('--input_stream', type=str, default='input')
 
    args = parser.parse_args()

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

    call_service("sample")
    a = MyAgent(args.name, args.input_stream, processor=processor)
    a.start()



