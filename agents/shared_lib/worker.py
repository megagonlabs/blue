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
    def __init__(self, name, input_stream, agent=None, id=None, processor=None, session=None, properties={}):

        self.name = name
        self.id = id

        self.session = session
        self.agent = agent

        self._initialize(properties=properties)

        self.input_streams = set()
        self.input_streams.add(input_stream)

        self.processor = processor
        if processor is not None:
            self.processor = lambda *args, **kwargs,: processor(*args, **kwargs, worker=self)

        self.properties = properties

        self.producer = None

        self.consumers = {}

        self._start()


    ###### initialization
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        self.properties = {}
        self.properties['num_threads'] = 1
        self.properties['host'] = 'localhost'
        self.properties['port'] = 6379

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]   

    def listener(self, id, data, stream):
        tag = None
        value = None
        if 'tag' in data:
            tag = data['tag']
        if 'value' in data:
            value = data['value']

        result = None

        if self.processor is not None:
            result = self.processor(stream, id, tag, value)

        # if data, write to stream
        if result is not None:
            result_data = result
            result_dtype = None
            result_tag = 'DATA'
            if type(result) == tuple:
                if len(result) == 2:
                    result_dtype = result[1]
                    result_data = result[0]
                elif len(result) == 3:
                    result_tag = result[2]
                    result_dtype = result[1]
                    result_data = result[0]


            if self.properties['aggregator.eos'] == 'FIRST':
                self.write(result_data, dtype=result_dtype, tag=result_tag, eos=(tag=='EOS'))
            elif self.properties['aggregator.eos'] == 'NEVER':
                self.write(result_data, dtype=result_dtype, tag=result_tag, eos=False)
            else:
                # TODO Implement 'ALL' option
                self.write(result_data, dtype=result_dtype, tag=result_tag, eos=False)
        
        if tag == 'EOS':
            # done, stop listening to input stream
            consumer = self.consumers[stream]
            print(consumer)
            consumer.stop()



    def write(self, data, dtype=None, tag='DATA', eos=True, split=" "):
        # start producer on first write
        self._start_producer()

        # do basic type setting, if none given
        # print("type {type}".format(type=type))
        if dtype == None:
            if isinstance(data, int):
                dtype = 'int'
            elif isinstance(data, float):
                dtype = 'float'
            elif isinstance(data, str):
                dtype = 'str'
            else:
                data = str(data)
                dtype = 'str'
        

        # print("type {type}".format(type=type))
        # print("data {data}".format(data=data))

        self.producer.write(data=data, dtype=dtype,  tag=tag, eos=eos, split=split)

    def _start(self):
        # logging.info('Starting agent worker {name}'.format(name=self.name))

        # start consumer only first on initial given input_stream
        self._start_consumers()
        logging.info('Started agent worker {name}'.format(name=self.name))

    def _start_consumers(self):
        for input_stream in self.input_streams:
            self._start_consumer_on_stream(input_stream)

    def _start_consumer_on_stream(self, input_stream):
         # start a consumer to listen to stream
        if input_stream:
            # create data namespace to share data on stream 
            if self.session:
                self.session._init_stream_agent_data_namespace(input_stream, self.name)

            consumer = Consumer(self.name, input_stream, listener=lambda id, data : self.listener(id,data,input_stream), properties=self.properties)

            self.consumers[input_stream] = consumer
            consumer.start()

    
    def _start_producer(self):
        # start, if not started
        if self.producer == None:
            suffix = None
            

            producer = Producer(self.name, sid=self.id, suffix=suffix, properties=self.properties)
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
    def _identify_stream(self, stream=None):
        if stream:
            return stream
        else:
            if len(self.input_streams) == 1:
                return list(self.input_streams)[0]
            else:
                return 'UNIDENTIFIED'

    def set_stream_data(self, key, value, stream=None):
        if self.session:
            stream = self._identify_stream(stream=stream)
            self.session.set_stream_data(stream, key, value)

    def append_stream_data(self, key, value, stream=None):
        if self.session:
            stream = self._identify_stream(stream=stream)
            self.session.append_stream_data(stream, key, value)

    def get_stream_data(self, key, stream=None):
        if self.session:
            stream = self._identify_stream(stream=stream)
            return self.session.get_stream_data(stream, key)
        
        return None

    def get_stream_data_len(self, key, stream=None):
        if self.session:
            stream = self._identify_stream(stream=stream)
            return self.session.get_stream_data_len(stream, key)
        
        return None

    ## worker data
    def set_data(self, key, value, stream=None):
        if self.session:
            stream = self._identify_stream(stream=stream)
            self.session.set_stream_agent_data(stream, self.name, key, value)

    def append_data(self, key, value, stream=None):
        if self.session:
            stream = self._identify_stream(stream=stream)
            self.session.append_stream_agent_data(stream, self.name, key, value)

    def get_data(self, key, stream=None):
        if self.session:
            stream = self._identify_stream(stream=stream)
            return self.session.get_stream_agent_data(stream, self.name, key)

        return None

    def get_data_len(self, key, stream=None):
        if self.session:
            stream = self._identify_stream(stream=stream)
            return self.session.get_stream_agent_data_len(stream, self.name, key)

        return None

    def stop(self):
        # send stop signal to consumer(s)
        for consumer in self.consumers.values():
            consumer.stop()

    def wait(self):
        # send wait to consumer(s)
        for consumer in self.consumers.values():
            consumer.wait()



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
  
   