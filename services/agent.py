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

class Agent():
    def __init__(self, name, input_stream, processor=None, properties={}):

        self.name = name
        self.input_stream = input_stream

        self.processor = processor

        self.properties = properties

        self.producer = None
        self.consumer = None

        self._initialize()


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

        # if data, write to streap
        if result is not None:
            self.write(result, eos=(tag=='EOS'))
        
        if tag == 'EOS':
            # done, stop listening to input stream
            self.consumer.stop()



    def write(self, data, type=None, eos=True, split=" "):
        self._start_producer()

        # do basic type setting, if none given
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

        self.producer.write(data, type=type, eos=eos, split=split)

    def start(self):
        print('Starting agent {name}'.format(name=self.name))
        # start consumer and producers
        self._start_producer()
        self._start_consumer()
        print('Started agent {name}'.format(name=self.name))

    def _start_consumer(self):
         # start a consumer to listen to stream
        if self.input_stream:
            self.consumer = Consumer(self.name, self.input_stream, listener=lambda id, data : self.listener(id,data))
            self.consumer.start()

    def _start_producer(self):
        # start, if not started
        if self.producer == None:
            producer = Producer(self.name)
            producer.start()
            self.producer = producer


#######################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, default='processor')
    parser.add_argument('--input_stream', type=str, default='input')
    parser.add_argument('--threads', type=int, default=1)
   
    args = parser.parse_args()

    stream_data = []

    # sample func to process data
    def processor(id, event, data):
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
            stream_data.append(data)
        
        return None


    # create an agent
    print(processor)
    a = Agent(args.name, args.input_stream, processor=processor)
    a.start()
  
   