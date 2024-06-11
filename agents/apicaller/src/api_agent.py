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
from utils import json_utils

import itertools
from tqdm import tqdm

###### Communication
import asyncio
from websockets.sync.client import connect


###### Blue
from agent import Agent, AgentFactory
from session import Session


# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


class APIAgent(Agent):
    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "API"
        super().__init__(**kwargs)

    def _initialize_properties(self):
        super()._initialize_properties()

        self.properties['api.service'] = "ws://localhost:8001"
    
        self.properties['input_json'] = None
        self.properties['input_context'] = None 
        self.properties['input_context_field'] = None 
        self.properties['input_field'] = 'input'
        self.properties['output_path'] = 'output'

    def get_prefix(self):
        prefix = self.name.lower()
        if 'service.prefix' in self.properties:
            prefix = self.properties['service.prefix']
        return prefix + '.'


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

       
        if 'input_template' in properties and properties['input_template'] is not None:
            input_data = properties['input_template'].format(**properties, input=input_data)

        # set input text to message
        input_object = input_data

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

    def process_output(self, output_data):
        return output_data

    def default_processor(self, stream, id, label, data, dtype=None, tags=None, properties=None, worker=None):
        
        if label == 'EOS':
            # get all data received from stream
            stream_data = ""
            if worker:
                stream_data = worker.get_data('stream')

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

            # process output data
            output_data = self.process_output(output_data)

            output_dtype = None

            if type(output_data) == int:
                output_dtype = 'int'
            elif type(output_data) == str:
                output_dtype = 'str'
            elif type(output_data) == dict:
                output_dtype = 'json'

            return "DATA", output_data, output_dtype, True
            
        elif label == 'BOS':
            # init stream to empty array
            if worker:
                worker.set_data('stream',[])
            pass
        elif label == 'DATA':
            # store data value
            logging.info(data)
            
            if worker:
                worker.append_data('stream', data)
        
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
    parser.add_argument('--name', default="API", type=str)
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
        
        af = AgentFactory(agent_class=APIAgent, agent_name=args.serve, agent_registry=args.registry, platform=platform, properties=properties)
        af.wait()
    else:
        a = None
        session = None

        if args.session:
            # join an existing session
            session = Session(cid=args.session)
            a = APIAgent(name=args.name, session=session, properties=properties)
        else:
            # create a new session
            session = Session()
            a = APIAgent(name=args.name, session=session, properties=properties)
  
        # wait for session
        if session:
            session.wait()