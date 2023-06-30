###### OS / Systems
from curses import noecho
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


###### Threads
import threading
import concurrent.futures

###### Blue
from producer import Producer
from consumer import Consumer
from session import Session
from worker import Worker

class Agent():
    def __init__(self, name, session=None, input_stream=None, processor=None, properties={}):

        self.name = name
        
        self.properties = properties

        self._initialize()

        # override, if necessary
        if processor is not None:
            self.processor = lambda *args: processor(*args, properties=self.properties)

        self.input_stream = input_stream
        
        self.set_session(session)

        self.consumer = None

        self.workers = []

        self._start()

    ###### initialization
    def _initialize(self):
        self._initialize_properties()


    def _initialize_properties(self):
        pass

    ###### worker
    def create_worker(self, input_stream):
        worker = Worker(self.name, input_stream, processor=self.processor, session=self.session)
        return worker

    ###### sesion
    def start_session(self):
        # create a new session
        session = Session()
        
        # set agent's session, start listening...
        self.set_session(session)

        # start consuming session stream
        self._start_session_consumer()
        return session


    def set_session(self, session):
        self.session = session

        if self.session:
           self.session.add_agent(self)


    def session_listener(self, id, data):   
        # listen to session stream
       
        # if session tag is USER
        tag = data['tag']
        
        if tag == 'ADDS':
            input_stream = data['value']

            agent = input_stream.split(":")[0]
            
            # TODO: Agents need to define what to listen to
            # for now, just listen to anything that isn't coming self
            if agent != self.name:
            # if agent == 'USER':
                logging.info("Spawning worker for agent {name}...".format(name=self.name))
                session_stream = self.session.get_stream()

                # create and start worker
                worker = self.create_worker(input_stream)
                self.workers.append(worker)
                
                logging.info("Spawned worker for agent {name}...".format(name=self.name))

    def interact(self, data):
        if self.session is None:
            self.start_session()

        # create worker to emit data for session
        worker = self.create_worker(None)

        # write data, automatically notify session on BOS
        worker.write(data)

    def _start(self):
        # print('Starting agent {name}'.format(name=self.name))

        # if agent is associated with a session
        if self.session:
            self._start_session_consumer()
        # else if agent is dedicated to an input stream 
        elif self.input_stream:
            # create and start worker
            worker = self.create_worker(self.input_stream)
            self.workers.append(worker)

        print('Started agent {name}'.format(name=self.name))



    def _start_session_consumer(self):
        # start a consumer to listen to session stream
        if self.session:
            session_stream = self.session.get_stream()

            if session_stream:
                self.consumer = Consumer(self.name, session_stream, listener=lambda id, data : self.session_listener(id,data))
                self.consumer.start()


    def stop(self):
        # send stop to each worker
        for w in self.workers:
            w.stop()

    def wait(self):
        # send wait to each worker
        for w in self.workers:
            w.wait()



#######################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, default='processor')
    parser.add_argument('--input_stream', type=str, default='input')
    parser.add_argument('--threads', type=int, default=1)
   
    args = parser.parse_args()

    # sample func to process data from 
    # return a value other than None
    # to create a stream 
    def processor(id, event, value):
        print(id)
        print(event)
        print(value)
       
        return None

    # create an agent and then create a session, and add agents
    a = Agent(args.name, processor=processor, session=None)
    s = a.start_session()

    # optionally you can create an agent in a session directly
    b = Agent(args.name, processor=processor, session=s)

  
   