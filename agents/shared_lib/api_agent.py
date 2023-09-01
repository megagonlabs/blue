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

class APIAgent(Agent):
    def __init__(self, name, session=None, input_stream=None, processor=None, properties={}):
        super().__init__(name, session=session, input_stream=input_stream, processor=processor, properties=properties)

    def _initialize_properties(self, properties=None):
        super()._initialize_properties(properties=properties)

        self.properties['api.service'] = "ws://localhost:8001"
    
        self.properties['input_json'] = None
        self.properties['input_context'] = None 
        self.properties['input_context_field'] = None 
        self.properties['input_field'] = 'input'
        self.properties['output_path'] = 'output'

    def get_prefix(self):
        return self.name.lower() + '.'


    def get_properties(self, properties=None):
        merged_properties = {}

        # copy agent properties
        for p in self.properties:
            merged_properties[p] = self.properties[p]

        # override
        if properties is not None:
            for p in properties:
                merged_properties[p] = properties[p]

        return merged_properties

    def create_message(self, input_data, properties=None):
        message = {}

        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        # set all message attributes from properties,
        # and only those with api prefix 
        for p in properties:
            if p.find(self.get_prefix()) == 0:
                # do not pass forward service property
                property = p[len(self.get_prefix()):]
                if property == 'service':
                    continue
                message[property] = properties[p]

        # set input text to message
        input_object = input_data

        if 'input_template' in properties and properties['input_template'] is not None:
            input_object = properties['input_template'].format(**properties, input=input_data)

        if 'input_json' in properties and properties['input_json'] is not None:
            input_object = json.loads(properties['input_json'])
            # set input text in object
            json_utils.json_query_set(input_object,properties['input_context_field'], input_data, context=properties['input_context'])

        message[properties['input_field']] = input_object

        return message

    def create_output(self, response, properties=None):

        # get properties, overriding with properties provided
        properties = self.get_properties(properties=properties)

        output_data = json_utils.json_query(response, properties['output_path'], single=True)
           
        # apply output template
        if 'output_template' in properties and properties['output_template'] is not None:
            output_data = properties['output_template'].format(**properties, output=output_data)
        return output_data

    def validate_input(self, input_data):
        return True 

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
            if not self.validate_input(input_data):
                return 

            logging.info(input_data)
            message = self.create_message(input_data, properties=properties)

            # serialize message, call service
            m = json.dumps(message)
            r = self.call_service(m)

            response = json.loads(r)

            # create output from response
            output_data = self.create_output(response)
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
                worker.append_data('stream', value)
        
        return None

    def get_service_address(self):
        service_address = self.properties['api.service']
        if self.get_prefix() + "service" in self.properties:
            service_address = self.properties[self.get_prefix() + "service"]

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
        a = APIAgent(session=session, properties=properties)
    elif args.input_stream:
        # no session, work on a single input stream
        a = APIAgent(input_stream=args.input_stream, properties=properties)
    else:
        # create a new session
        a = APIAgent(properties=properties)
        a.start_session()

    # wait for session
    session.wait()