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

###### Backend, Databases
import redis


###### Blue
from producer import Producer
from consumer import Consumer
from session import Session
from worker import Worker

class Agent():
    def __init__(self, name, session=None, input_stream=None, processor=None, properties={}):

        self.name = name

        self._initialize(properties=properties)

        # override, if necessary
        if processor is not None:
            self.processor = lambda *args, **kwargs: processor(*args, **kwargs, properties=self.properties)
        else:
            self.processor = lambda *args, **kwargs: self.default_processor(*args, **kwargs, properties=self.properties)

        self.input_stream = input_stream
        
        self.set_session(session)

        self.aggregate_producer_id = None
        self.consumer = None

        self.workers = []

        self._start()

    ###### initialization
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)


    def _initialize_properties(self):
        self.properties = {}

        # db connectivity
        self.properties['host'] = 'localhost'
        self.properties['port'] = 6379

        # aggregator (have a single producer for all workers)
        self.properties['aggregator'] = False
        self.properties['aggregator.eos'] = 'FIRST'

        ### include/exclude list of rules to listen to agents/tags
        listeners = {}
        self.properties['listens'] = listeners
        listeners['includes'] = ['.*']
        listeners['excludes'] = [self.name]

        ### default tags to tag output streams
        tags = []
        self.properties['tags'] = tags


    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    ###### database, data
    def _start_connection(self):
        host = self.properties['host']
        port = self.properties['port']

        self.connection = redis.Redis(host=host, port=port, decode_responses=True)

    ###### worker
    def create_worker(self, input_stream, tags=None, id=None):
        if self.properties['aggregator']:
            # generate unique id for aggregate producer
            if self.aggregate_producer_id is None:
                self.aggregate_producer_id = self.name + ":" + str(hex(uuid.uuid4().fields[0]))[2:]
            # if id not set use aggregate_producer
            if id is None:
                id = self.aggregate_producer_id
        
        worker = Worker(self.name, input_stream, agent=self, id=id, processor=lambda *args, **kwargs: self.processor(*args, **kwargs, tags=tags), session=self.session, properties=self.properties)
      
        return worker

    ###### default processor, override
    def default_processor(self, stream, id, event, value, tags=None, properties=None, worker=None):
        logging.info('default processor: override')
        logging.info(stream)
        logging.info(event)
        logging.info(id)
        logging.info(value)
        logging.info(tags)
        logging.info(properties)
        logging.info(worker)

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



    def session_listener(self, id, record):   
        # listen to session stream
       
        # if session tag is USER
        tag = record['tag']
       
        if tag == 'ADD':
            data = json.loads(record['value'])
            input_stream = data['stream']
            tags = data['tags']

            # agent define what to listen to using include/exclude expressions
            matches = self._match_listen_to_tags(tags)
            if len(matches) == 0:
                logging.info("Not listening to {stream} with {tags}...".format(stream=input_stream, tags=tags))
                return 

            logging.info("Spawning worker for stream {stream} with matching tags {matches}...".format(stream=input_stream, matches=matches))
            session_stream = self.session.get_stream()

            # create and start worker
            # TODO; pass tag to worker, with parameters
            worker = self.create_worker(input_stream, tags=matches)
            self.workers.append(worker)
            
            logging.info("Spawned worker for stream {stream}...".format(stream=input_stream))

    def _match_listen_to_tags(self, tags):
        matches = []
        # process includes for each tag
        for tag in tags:

            includes = self.properties['listens']['includes']
            for i in includes:
                p = re.compile(i)
                if p.match(tag):
                    matches.append(tag)
        

        if len(matches) == 0:
            return matches

        # process excludes for each tag
        for tag in tags:

            excludes = self.properties['listens']['excludes']
            for x in excludes:
                p = re.compile(x)
                if p.match(tag):
                    logging.info("Matched exclude rule: {rule}".format(rule=x))
                    return []
       
        return matches

    def interact(self, data):
        if self.session is None:
            self.start_session()

        # create worker to emit data for session
        worker = self.create_worker(None)

        # write data, automatically notify session on BOS
        worker.write(data)

    def _start(self):
        self._start_connection()
        
        # logging.info('Starting agent {name}'.format(name=self.name))

        # if agent is associated with a session
        if self.session:
            self._start_session_consumer()
        # else if agent is dedicated to an input stream 
        elif self.input_stream:
            # create and start worker
            worker = self.create_worker(self.input_stream)
            self.workers.append(worker)

        logging.info('Started agent {name}'.format(name=self.name))


    def _start_session_consumer(self):
        # start a consumer to listen to session stream
        if self.session:
            session_stream = self.session.get_stream()

            if session_stream:
                self.consumer = Consumer(self.name, session_stream, listener=lambda id, data : self.session_listener(id,data), properties=self.properties)
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
    parser.add_argument('--properties', type=str)
    parser.add_argument('--loglevel', default="INFO", type=str)
 
    args = parser.parse_args()
   
    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())


    # set properties
    properties = {}
    p = args.properties
    if p:
        # decode json
        properties = json.loads(p)
    

    # sample func to process data from 
    # return a value other than None
    # to create a stream 
    def processor(stream, id, event, value):
        logging.into(stream)
        logging.info(id)
        logging.info(event)
        logging.info(value)
       
        return None


    # create an agent and then create a session, and add agents
    a = Agent(args.name, processor=processor, session=None, properties=properties)
    s = a.start_session()

    # optionally you can create an agent in a session directly
    b = Agent(args.name, processor=processor, session=s, properties=properties)

  
   