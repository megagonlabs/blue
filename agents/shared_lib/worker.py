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

###### Blue
from producer import Producer
from consumer import Consumer
from agent import Session

class Worker():
    def __init__(self, name, input_stream, processor=None, session=None, properties={}):

        self.name = name
        self.session = session

        self.input_stream = input_stream

        self.processor = processor
        if processor is not None:
            self.processor = lambda *args, **kwargs,: processor(*args, **kwargs, worker=self)

        self.properties = properties

        self.producer = None
        self.consumer = None

        self._initialize()
        self._start()


    ###### initialization
    def _initialize(self):
        self._initialize_properties()


    def _initialize_properties(self):
        if 'num_threads' not in self.properties:
            self.properties['num_threads'] = 1

        if 'host' not in self.properties:
            self.properties['host'] = 'localhost'

        if 'port' not in self.properties:
            self.properties['port'] = 6379

    def listener(self, id, data):
        tag = None
        value = None
        if 'tag' in data:
            tag = data['tag']
        if 'value' in data:
            value = data['value']

        result = None

        if self.processor is not None:
            result = self.processor(id, tag, value)

        # if data, write to stream
        if result is not None:
            self.write(result, eos=(tag=='EOS'))
        
        if tag == 'EOS':
            # done, stop listening to input stream
            self.consumer.stop()



    def write(self, data, type=None, eos=True, split=" "):
        # start producer on first write
        self._start_producer()

        # do basic type setting, if none given
        # print("type {type}".format(type=type))
        if type == None:
            if isinstance(data, int):
                type = 'int'
            elif isinstance(data, float):
                type = 'float'
            elif isinstance(data, str):
                type = 'str'
            else:
                data = str(data)
                type = 'str'

        # print("type {type}".format(type=type))
        # print("data {data}".format(data=data))

        self.producer.write(data=data, type=type, eos=eos, split=split)

    def _start(self):
        # logging.info('Starting agent worker {name}'.format(name=self.name))

        # start consumer only first 
        self._start_consumer()
        logging.info('Started agent worker {name}'.format(name=self.name))

    def _start_consumer(self):
         # start a consumer to listen to stream
        if self.input_stream:
            # create data namespace to share data on stream 
            if self.session:
                self.session._init_stream_agent_data_namespace(self.input_stream, self.name)

            self.consumer = Consumer(self.name, self.input_stream, listener=lambda id, data : self.listener(id,data))
            self.consumer.start()

    def _start_producer(self):
        # start, if not started
        if self.producer == None:
            producer = Producer(self.name)
            producer.start()
            self.producer = producer

            # notify session of new stream, if in a session
            if self.session:
                # get output stream info
                output_stream = self.producer.get_stream()
                # notify session
                self.session.notify(output_stream)

    ###### DATA RELATED 
    ## session data
    def set_session_data(self, key, value):
        if self.session:
            self.session.set_data(key, value)

    def append_session_data(self, key, value):
        if self.session:
            self.session.append_data(key, value)

    def get_session_data(self, key):
        if self.session:
            return self.session.get_data(key)
        
        return None

    def get_session_data_len(self, key):
        if self.session:
            return self.session.get_data_len(key)
        
        return None

    ## session stream data
    def set_stream_data(self, key, value):
        if self.session:
            self.session.set_stream_data(self.input_stream, key, value)

    def append_stream_data(self, key, value):
        if self.session:
            self.session.append_stream_data(self.input_stream, key, value)

    def get_stream_data(self, key):
        if self.session:
            return self.session.get_stream_data(self.input_stream, key)
        
        return None

    def get_stream_data_len(self, key):
        if self.session:
            return self.session.get_stream_data_len(self.input_stream, key)
        
        return None

    ## worker data
    def set_data(self, key, value):
        if self.session:
            self.session.set_stream_agent_data(self.input_stream, self.name, key, value)

    def append_data(self, key, value):
        if self.session:
            self.session.append_stream_agent_data(self.input_stream, self.name, key, value)

    def get_data(self, key):
        if self.session:
            return self.session.get_stream_agent_data(self.input_stream, self.name, key)

        return None

    def get_data_len(self, key):
        if self.session:
            return self.session.get_stream_agent_data(self.input_stream, self.name, key)

        return None

    def stop(self):
        # send stop signal to consumer
        self.consumer.stop()

    def wait(self):
        # send wait to consumer
        self.consumer.wait()



#######################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, default='processor')
    parser.add_argument('--input_stream', type=str, default='input')
    parser.add_argument('--threads', type=int, default=1)
   
    args = parser.parse_args()

    stream_data = []

    # sample func to process data
    def processor(id, event, value):
       
        if event == 'EOS':
            # print all data received from stream
            print(stream_data)

            # compute stream data
            l = len(stream_data)
            time.sleep(4)
            
            # output to stream
            return l
           
        elif event == 'DATA':
            # store data value
            stream_data.append(value)
        
        return None


    # create a worker
    w = Worker(args.name, args.input_stream, processor=processor)
    w.start()
  
   