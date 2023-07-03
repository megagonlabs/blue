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
from utils import json_utils

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
class OpenAIAgent(Agent):
    def __init__(self, session=None, input_stream=None, processor=None, properties={}):
        super().__init__("OPENAI", session=session, input_stream=input_stream, processor=processor, properties=properties)

    def _initialize_properties(self):
        super()._initialize_properties()

        if 'api' not in self.properties:
            self.properties['api'] = 'Completion'
        if 'model' not in self.properties:
            self.properties['model'] = "text-davinci-003"
        if 'input_json' not in self.properties:
            self.properties['input_json'] = None 
        if 'input_context' not in self.properties:
            self.properties['input_context'] = None 
        if 'input_context_field' not in self.properties:
            self.properties['input_context_field'] = None 
        if 'input_field' not in self.properties:
            self.properties['input_field'] = 'prompt'
        if 'output_path' not in self.properties:
            self.properties['output_path'] = '$.choices[0].text'
        if 'stream' not in self.properties:
            self.properties['stream'] = False
        if 'max_tokens' not in self.properties:
            self.properties['max_tokens'] = 50

    def default_processor(self, id, event, data, properties=None, worker=None):
        properties = self.properties 
        print(properties)
        print(worker)

        if event == 'EOS':
            # print all data received from stream

            #### call service to compute
           
            message = {}
            # set all message attributes from properties
            for p in properties:
                message[p] = properties[p]

            # set input text to message
            input_data = " ".join(stream_data)
            input_object = input_data
            if properties['input_json']:
                input_object = json.loads(properties['input_json'])
                # set input text in object
                json_utils.json_query_set(input_object,properties['input_context_field'], input_data, context=properties['input_context'])

            message[properties['input_field']] = input_object

            # remove non-openai params
            del message['host']
            del message['port']
            del message['input_json']
            del message['input_context']
            del message['input_context_field']
            del message['input_field']
            del message['output_path']

            # serialize message, call service
            m = json.dumps(message)
            r = call_service(m)

            response = json.loads(r)

            output = json_utils.json_query(response, properties['output_path'], single=True)
           
            # output to stream
            return output
           
        elif event == 'DATA':
            # store data value
            stream_data.append(data)
        
        return None

        
def call_service(data):
    with connect("ws://localhost:8001") as websocket:
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

    stream_data = []

    # set properties
    properties = {}
    p = args.properties
    if p:
        # decode json
        properties = json.loads(p)
    

    if args.session:
        # join an existing session
        session = Session(args.session)
        a = OpenAIAgent(session=session, properties=properties)
    elif args.input_stream:
        # no session, work on a single input stream
        a = OpenAIAgent(input_stream=args.input_stream, properties=properties)
    else:
        # create a new session
        a = OpenAIAgent(properties=properties)
        a.start_session()


    # wait for session
    session.wait()