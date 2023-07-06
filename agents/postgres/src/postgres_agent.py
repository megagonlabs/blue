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

###### Agent Specific
import sqlvalidator


# set log level
logging.getLogger().setLevel(logging.INFO)

class PostgresAgent(Agent):
    def __init__(self, session=None, input_stream=None, processor=None, properties={}):
        super().__init__("POSTGRES", session=session, input_stream=input_stream, processor=processor, properties=properties)

    def _initialize_properties(self):
        super()._initialize_properties()

        if 'postgres_host' not in self.properties:
            self.properties['postgres_host'] = 'localhost'
        if 'postgres_port' not in self.properties:
            self.properties['postgres_port'] = 5432
        if 'postgres_database' not in self.properties:
            self.properties['postgres_database'] = 'default'
        if 'input_json' not in self.properties:
            self.properties['input_json'] = None 
        if 'input_context' not in self.properties:
            self.properties['input_context'] = None 
        if 'input_context_field' not in self.properties:
            self.properties['input_context_field'] = None 
        if 'input_field' not in self.properties:
            self.properties['input_field'] = 'query'
        if 'input_format' not in self.properties:
            self.properties['input_format'] = 'select row_to_json(row) from ({input}) row;'
        if 'output_path' not in self.properties:
            self.properties['output_path'] = '$.results'
   
    def default_processor(self, id, event, value, properties=None, worker=None):
        properties = self.properties 

        if event == 'EOS':
            # get all data received from stream
            stream_data = ""
            if worker:
                stream_data = worker.get_data('stream')
                stream_data = stream_data[0] 

           
            #### call service to compute
           
            message = {}
            # set all message attributes from properties,
            # only with 'postgres_' prefix
            for p in properties:
                if p.find('postgres_') == 0:
                    message[p[len('postgres_'):]] = properties[p]

            # set input text to message
            input_data = " ".join(stream_data)

            #### validate input
            isValid = False

            try:
                sql_query = sqlvalidator.parse(input_data)
                isValid = sql_query.is_valid()
            except:
                logging.info('Error validating SQL query :{query}'.format(query=input_data))
                
            if not isValid:
                return 

            input_object = input_data

            if 'input_format' in properties and properties['input_format'] is not None:
                input_object = properties['input_format'].format(**properties, input=input_data)

            if 'input_json' in properties and properties['input_json'] is not None:
                input_object = json.loads(properties['input_json'])
                # set input text in object
                json_utils.json_query_set(input_object,properties['input_context_field'], input_data, context=properties['input_context'])

            message[properties['input_field']] = input_object


            # serialize message, call service
            m = json.dumps(message)
            r = self.call_service(m)

            response = json.loads(r)

            output_data = json_utils.json_query(response, properties['output_path'], single=True)
           
            # output to stream
            if 'output_format' in properties and properties['output_format'] is not None:
                output_data = properties['output_format'].format(**properties, output=output_data)
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

        
    def call_service(self, data):
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

    # set properties
    properties = {}
    p = args.properties


    if p:
        # decode json
        properties = json.loads(p)
    
    if args.session:
        # join an existing session
        session = Session(args.session)
        a = PostgresAgent(session=session, properties=properties)
    elif args.input_stream:
        # no session, work on a single input stream
        a = PostgresAgent(input_stream=args.input_stream, properties=properties)
    else:
        # create a new session
        a = PostgresAgent(properties=properties)
        a.start_session()

    # wait for session
    session.wait()