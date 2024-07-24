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
import math

###### Parsers, Formats, Utils
import re
import csv
import json
from utils import json_utils


import itertools
from tqdm import tqdm

###### Backend, Databases
import redis


###### Blue
from producer import Producer
from consumer import Consumer
from session import Session
from worker import Worker
from message import Message, MessageType, ContentType, ControlCode


def create_uuid():
    return str(hex(uuid.uuid4().fields[0]))[2:]

class Agent:
    def __init__(
        self,
        name="AGENT",
        id=None,
        sid=None,
        cid=None,
        prefix=None,
        suffix=None,
        session=None,
        processor=None,
        properties={},
    ):

        self.name = name
        if id:
            self.id = id
        else:
            self.id = str(hex(uuid.uuid4().fields[0]))[2:]

        if sid:
            self.sid = sid
        else:
            self.sid = self.name + ":" + self.id

        self.prefix = prefix
        self.suffix = suffix
        self.cid = cid

        if self.cid == None:
            self.cid = self.sid

            if self.prefix:
                self.cid = self.prefix + ":" + self.cid
            if self.suffix:
                self.cid = self.cid + ":" + self.suffix

        self._initialize(properties=properties)

        # override, if necessary
        if processor is not None:
            self.processor = lambda *args, **kwargs: processor(*args, **kwargs, properties=self.properties)
        else:
            self.processor = lambda *args, **kwargs: self.default_processor(*args, **kwargs, properties=self.properties)

        self.session = None
        if session:
            self.join_session(session)

        # consumer for session stream
        self.session_consumer = None

        # workers of an agent in a session
        self.workers = []

        self._start()

    ###### initialization
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        self.properties = {}

        # db connectivity
        self.properties["db.host"] = "localhost"
        self.properties["db.port"] = 6379

        # instructable
        self.properties["instructable"] = True

        ### include/exclude list of rules to listen to agents/tags
        listeners = {}
        self.properties["listens"] = listeners
        

        # DEFAULT is the default input parameter
        default_listeners = {}
        listeners["DEFAULT"] = default_listeners
        default_listeners["includes"] = [".*"]
        default_listeners["excludes"] = []

        ### default tags to tag output streams
        tags = {}
        self.properties["tags"] = tags
        
        # DEFAULT is the default output parameter
        default_tags = []
        tags["DEFAULT"] = default_tags
        

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    ###### database, data
    def _start_connection(self):
        host = self.properties["db.host"]
        port = self.properties["db.port"]

        # db connection
        logging.info("Starting connection to: " + host + ":" + str(port))
        self.connection = redis.Redis(host=host, port=port, decode_responses=True)

    ###### worker
    # input_stream is data stream for input param, default 'DEFAULT' 
    def create_worker(self, input_stream, input="DEFAULT", context=None, processor=None):
        # listen 
        logging.info(
            "Listening stream {stream} for param {param}...".format(
                stream=input_stream, param=input
            )
        )

        if processor == None:
            processor = lambda *args, **kwargs: self.processor(*args, **kwargs)

        # set prefix if context provided
        if context:
            p = context + ":" + self.sid
        else:
            # default agent's cid is prefix
            p = self.cid

        worker = Worker(
            input_stream,
            input=input,
            prefix=p,
            agent=self,
            processor=processor,
            session=self.session,
            properties=self.properties,
        )

        self.workers.append(worker)

        return worker

    ###### default processor, override
    def default_processor(
        self,
        message,
        input=None,
        properties=None,
        worker=None,
    ):
        logging.info("default_processor: override")
        logging.info(message)
        logging.info(input)
        logging.info(properties)
        logging.info(worker)

    ###### default processor, do not override
    def _instruction_processor(
        self,
        message,
        input=None,
        properties=None,
        worker=None,
    ):
        logging.info("instruction processor")
        logging.info(message)
        logging.info(input)
        logging.info(properties)
        logging.info(worker)

        if message.getCode() == ControlCode.EXECUTE_AGENT:
            agent = message.getArg("agent")
            if agent == self.name:
                context = message.getArg("context")
                input_streams = message.getArg("input")
                for input_param in input_streams:
                    logging.info("l")
                    self.create_worker(input_streams[input_param], input=input_param, context=context)
            
        

    ###### session
    def join_session(self, session):
        if type(session) == str:
            session = Session(cid=session, properties=self.properties)

        self.session = session

        if self.session:
            self.session.add_agent(self)

    def leave_session(self):
        if self.session:
            self.session.remove_agent(self)

    def session_listener(self, message):
        # listen to session stream
        if message.getCode() == ControlCode.ADD_STREAM:
            
            stream = message.getArg("stream")
            tags = message.getArg("tags")
            
            # agent define what to listen to using include/exclude expressions
            logging.info("Checking listener tags...")
            matched_params = self._match_listen_to_tags(tags)
            logging.info("Done.")

            # instructable
            logging.info("instructable? " + str(self.properties['instructable']))
            if self.properties['instructable']:
                if 'INSTRUCTION' in set(tags):
                    # create a special worker to list to streams with instructions
                    instruction_worker = self.create_worker(stream, input="INSTRUCTION", processor=lambda *args, **kwargs: self._instruction_processor(*args, **kwargs))

            # skip
            if len(matched_params) == 0:
                logging.info("Skipping stream {stream} with {tags}...".format(stream=stream, tags=tags))
                return

            for param in matched_params:
                tags = matched_params[param]
                

                # create worker
                worker = self.create_worker(stream, input=param)

                logging.info("Spawned worker for stream {stream}...".format(stream=stream))

    def _match_listen_to_tags(self, tags):
        matched_params = {}

        # default listeners
        listeners_by_param = self.properties["listens"]
        logging.info(json.dumps(listeners_by_param, indent=3))
        for param in listeners_by_param:
            matched_tags = set()

            param_listeners = listeners_by_param[param]
            if 'includes' not in param_listeners:
                continue
            includes = param_listeners["includes"]
            excludes = []
            if 'excludes' in param_listeners:
                excludes = param_listeners["excludes"]

            for i in includes:
                p = None
                if type(i) == str:
                    p = re.compile(i)
                    for tag in tags:
                        if p.match(tag):
                            matched_tags.add(tag)
                            logging.info("Matched include rule: {rule} for param: {param}".format(rule=str(i),param=param))
                elif type(i) == list:
                    m = set()
                    a = True
                    for ii in i:
                        logging.info(ii)
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
                        matched_tags = matched_tags.union(m)
                        logging.info("Matched include rule: {rule} for param: {param}".format(rule=str(i),param=param))

            # no matches for param
            if len(matched_tags) == 0:
                continue

            # found matched_tags for param
            matched_params[param] = list(matched_tags)

            for x in excludes:
                p = None
                if type(x) == str:
                    p = re.compile(x)
                    if p.match(tag):
                        logging.info("Matched exclude rule: {rule} for param: {param}".format(rule=str(x),param=param))
                        # delete match
                        del matched_params[param] 
                        break
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
                        logging.info("Matched exclude rule: {rule} for param: {param}".format(rule=str(x),param=param))
                        # delete match
                        del matched_params[param] 
                        break

        return matched_params

    def interact(self, data, output="DEFAULT", unique=True, eos=True):
        if self.session is None:
            logging.error("No current session to interact with.")
            return

        # update output, if unique
        if unique:
            output = output + ":" + create_uuid()

        # create worker to emit data for session
        worker = self.create_worker(None)

        # write data, automatically notify session on BOS
        
        worker.write_data(data, output=output)

        if eos:
            worker.write_eos(output=output)

    def _start(self):
        self._start_connection()

        # if agent is associated with a session
        if self.session:
            self._start_session_consumer()

        logging.info("Started agent {name}".format(name=self.name))

    def _start_session_consumer(self):
        # start a consumer to listen to session stream
        if self.session:
            session_stream = self.session.get_stream()

            if session_stream:
                self.session_consumer = Consumer(
                    session_stream,
                    name=self.name,
                    listener=lambda message: self.session_listener(message),
                    properties=self.properties,
                )
                self.session_consumer.start()

    def stop(self):
        # leave session
        self.leave_session()

        # send stop to each worker
        for w in self.workers:
            w.stop()

    def wait(self):
        # send wait to each worker
        for w in self.workers:
            w.wait()


class AgentFactory:
    def __init__(
        self,
        agent_class=Agent,
        agent_name="Agent",
        agent_registry="default",
        platform="default",
        properties={},
    ):
        self.agent_class = agent_class
        self.agent_name = agent_name
        self.agent_registry = agent_registry

        self.platform = platform

        self._initialize(properties=properties)

        self.session_consumer = None

        # creation time
        self.ct = math.floor(time.time_ns() / 1000000)

        self._start()

    ###### initialization
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        self.properties = {}

        # db connectivity
        self.properties["db.host"] = "localhost"
        self.properties["db.port"] = 6379

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    ###### database, data
    def _start_connection(self):
        host = self.properties["db.host"]
        port = self.properties["db.port"]

        # db connection
        logging.info("Starting connection to: " + host + ":" + str(port))
        self.connection = redis.Redis(host=host, port=port, decode_responses=True)

    ###### factory functions
    def create(self, **kwargs):
        print(kwargs)
        klasse = self.agent_class
        instanz = klasse(**kwargs)
        return instanz

    def _start(self):
        self._start_connection()

        self._start_consumer()
        logging.info(
            "Started agent factory for agent: {name} in registry: {registry} on platform: {platform} ".format(
                name=self.agent_name,
                registry=self.agent_registry,
                platform=self.platform,
            )
        )

    def wait(self):
        self.session_consumer.wait()

    def _start_consumer(self):
        # platform stream
        stream = "PLATFORM:" + self.platform + ":STREAM"
        self.session_consumer = Consumer(
            stream,
            name=self.agent_name + "_FACTORY",
            listener=lambda message: self.platform_listener(message),
            properties=self.properties,
        )
        self.session_consumer.start()

    def platform_listener(self, message):
        # listen to platform stream

        logging.info("Processing: " + str(message))
        id = message.getID()

        # only process newer instructions
        mt = int(id.split("-")[0])

        # ignore past instructions
        if mt < self.ct:
            return

        # check if join session
        if message.getCode() == ControlCode.JOIN_SESSION:
            session = message.getArg("session")
            registry = message.getArg("registry")
            agent = message.getArg("agent")
            

            # start with factory properties, merge properties from API call
            properties_from_api = message.getArg("properties")
            properties_from_factory = self.properties
            agent_properties = {}
            agent_properties = json_utils.merge_json(agent_properties, properties_from_factory)
            agent_properties = json_utils.merge_json(agent_properties, properties_from_api)
            input = None

            if "input" in agent_properties:
                input = agent_properties["input"]
                del agent_properties["input"]

            # check match in canonical name space, i.e.
            # <agent_name> or <agent_name>.<derivative_agent_name>
            ca = agent.split("_")
            parent_agent_name = ca[0]
            child_agent_name = ca[0]

            # if derivative_agent_name 
            if len(ca) > 1:
                child_agent_name = ca[1]

            if self.agent_name == ca[0]:
                name = agent

                logging.info("Launching Agent: " + name + "...")
                logging.info("Agent Properties: " + json.dumps(agent_properties) + "...")

                prefix = session + ":" + "AGENT"
                a = self.create(
                    name=name,
                    prefix=prefix,
                    session=session,
                    properties=agent_properties,
                )

                logging.info("Joined session: " + session)
                if input:
                    a.interact(input)
                    logging.info("Interact: " + input)


#######################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str, default="AGENT")
    parser.add_argument("--input_stream", type=str, default="input")
    parser.add_argument("--properties", type=str)
    parser.add_argument("--loglevel", default="INFO", type=str)
    parser.add_argument("--serve", type=str, default="AGENT")
    parser.add_argument("--platform", type=str, default="default")
    parser.add_argument("--registry", type=str, default="default")

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

        af = AgentFactory(
            agent_class=Agent,
            agent_name=args.serve,
            agent_registry=args.registry,
            platform=platform,
            properties=properties,
        )
        af.wait()

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
