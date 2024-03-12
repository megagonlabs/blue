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
from rpc import RPCServer

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
        
        self.join_session(session)

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
        self.properties['db.host'] = 'localhost'
        self.properties['db.port'] = 6379

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
        host = self.properties['db.host']
        port = self.properties['db.port']

        # db connection
        logging.info("Starting connection to: " + host + ":" + str(port))
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
    def default_processor(self, stream, id, label, data, dtype=None, tags=None, properties=None, worker=None):
        logging.info('default processor: override')
        logging.info(stream)
        logging.info(tags)
        logging.info(id)
        logging.info(label)
        logging.info(data)
        logging.info(properties)
        logging.info(worker)

    ###### sesion
    def start_session(self):
        # create a new session
        session = Session(properties=self.properties)
        
        # set agent's session, start listening...
        self.join_session(session)

        # start consuming session stream
        self._start_session_consumer()
        return session


    def join_session(self, session):
        if type(session) == str:
            session = Session(name=session, properties=self.properties)

        self.session = session

        if self.session:
           self.session.add_agent(self)

    def leave_session(self):
        if self.session:
           self.session.remove_agent(self)



    def session_listener(self, id, message):   
        # listen to session stream
       
        label = message['label']
       
        if label == 'ADD':
            data = json.loads(message['data'])

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

    # def _match_listen_to_tags(self, tags):
    #     matches = []
    #     # process includes for each tag
    #     for tag in tags:

    #         includes = self.properties['listens']['includes']
    #         for i in includes:
    #             p = re.compile(i)
    #             if p.match(tag):
    #                 matches.append(tag)
        

    #     if len(matches) == 0:
    #         return matches

    #     # process excludes for each tag
    #     for tag in tags:

    #         excludes = self.properties['listens']['excludes']
    #         for x in excludes:
    #             p = re.compile(x)
    #             if p.match(tag):
    #                 logging.info("Matched exclude rule: {rule}".format(rule=x))
    #                 return []
       
    #     return matches

    def _match_listen_to_tags(self, tags):
        matches = set()

        includes = self.properties['listens']['includes']
        excludes = self.properties['listens']['excludes']

        for i in includes:
            p = None
            if type(i) == str:
                p = re.compile(i)
                for tag in tags:
                    if p.match(tag):
                        matches.add(tag)
                        logging.info("Matched include rule: {rule}".format(rule=str(i)))
            elif type(i) == list:
                m = set()
                a = True
                for ii in i:
                    p = re.compile(ii)
                    b = False
                    for tag in tags:
                        if p.match(tag):
                            m.add(tag)
                            b = True
                            break
                    if b:
                        continue
                    else:
                        a = False
                        break
                if a:
                    matches = matches.union(m)
                    logging.info("Matched include rule: {rule}".format(rule=str(i)))

        if len(matches) == 0:
            return list(matches)

        for x in excludes:
            p = None
            if type(x) == str:
                p = re.compile(x)
                if p.match(tag):
                    logging.info("Matched exclude rule: {rule}".format(rule=str(x)))
                    return []
            elif type(x) == list:
                a = True
                if len(x) == 0:
                    a = False
                for xi in x:
                    p = re.compile(xi)
                    b = False
                    for tag in tags:
                        if p.match(tag):
                            b = True
                            break
                    if b:
                        continue
                    else:
                        a = False
                        break
                if a:
                    logging.info("Matched exclude rule: {rule}".format(rule=str(x)))
                    return []

        return list(matches)

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
                self.consumer = Consumer(self.name, session_stream, listener=lambda id, message : self.session_listener(id, message), properties=self.properties)
                self.consumer.start()


    def stop(self):
        # leave session 
        self.leave_session

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
    parser.add_argument('--name', type=str, default='agent')
    parser.add_argument('--input_stream', type=str, default='input')
    parser.add_argument('--properties', type=str)
    parser.add_argument('--loglevel', default="INFO", type=str)
    parser.add_argument('--serve', default=False, action=argparse.BooleanOptionalAction)
 
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
        # launch agent with parameters, start session
        def launch(*args, **kwargs):
            logging.info("Launching UserAgent...")
            logging.info(kwargs)
            agent = Agent(*args, **kwargs)
            session = agent.start_session()
            logging.info("Started session: " + session.name)
            logging.info("Launched.")
            return session.name

        # launch agent with parameters, join session in keyword args (session=)
        def join(*args, **kwargs):
            logging.info("Launching UserAgent...")
            logging.info(kwargs)
            agent = Agent(*args, **kwargs)
            logging.info("Joined session: " + kwargs['session'])
            logging.info("Launched.")
            return kwargs['session']

        # run rpc server
        rpc = RPCServer(args.name, properties=properties)
        rpc.register(launch)
        rpc.register(join)
        rpc.run()
    else:
        # sample func to process data from 
        # return a value other than None
        # to create a stream 
        def processor(stream, id, label, data, dtype=None):
            logging.into(stream)
            logging.info(id)
            logging.info(label)
            logging.info(data)
        
            return None


        # create an agent and then create a session, and add agents
        a = Agent(args.name, processor=processor, session=None, properties=properties)
        s = a.start_session()

        # optionally you can create an agent in a session directly
        b = Agent(args.name, processor=processor, session=s, properties=properties)

  
   