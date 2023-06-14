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

###### Blue
from producer import Producer

class Session():
    def __init__(self, name=None, properties={}):

        # set a unique id per session
        if name is None:
            self.name = "SESSION" + ":" + str(uuid.uuid4())
        else:
            self.name = name

        self.properties = properties

        # producer to emit session events
        self.producer = None

        self._initialize()

        self.agents = []

        self._start()


    ###### initialization
    def _initialize(self):
        self._initialize_properties()


    def _initialize_properties(self):

        if 'host' not in self.properties:
            self.properties['host'] = 'localhost'

        if 'port' not in self.properties:
            self.properties['port'] = 6379

    def get_stream(self):
        return self.producer.get_stream()

    def add_agent(self, agent):
        self.agents.append(agent)

    def notify(self, worker_stream):
        # start producer on first write
        self._start_producer()

        data = worker_stream
        tag = "ADDS"
        self.producer.write(data=data, tag=tag, eos=False)

    def _start(self):
        # logging.info('Starting session {name}'.format(name=self.name))

        # start  producer to emit session events
        self._start_producer()

        logging.info('Started session {name}'.format(name=self.name))

    def _start_producer(self):
        # start, if not started
        if self.producer == None:
            producer = Producer("SESSION", sid=self.name)
            producer.start()
            self.producer = producer

    def stop(self):
        # stop agents
        for a in self.agents:
            a.stop()

        # put EOS to stream
        self.producer.write(tag="EOS")

    def wait(self):
        for a in self.agents:
            a.wait()

        while True:
            time.sleep(1)



#######################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, default='processor')
   
    args = parser.parse_args()

    from agent import Agent

    # create a user agent
    user_agent = Agent("USER")
    session = user_agent.start_session()

    # sample func to process data for counter
    stream_data = []

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

    # create a counter agent in the same session
    counter_agent = Agent("COUNTER", session=session, processor=processor)

    # user initiates an interaction
    user_agent.interact("this is a simple interaction")

    # wait for session
    session.wait()
    