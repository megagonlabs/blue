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
            self.processor = lambda *args, **kwargs: processor(
                *args, **kwargs, properties=self.properties
            )
        else:
            self.processor = lambda *args, **kwargs: self.default_processor(
                *args, **kwargs, properties=self.properties
            )

        if session:
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
        self.properties["db.host"] = "localhost"
        self.properties["db.port"] = 6379

        # aggregator (have a single producer for all workers)
        self.properties["aggregator"] = False
        self.properties["aggregator.eos"] = "FIRST"

        ### include/exclude list of rules to listen to agents/tags
        listeners = {}
        self.properties["listens"] = listeners
        listeners["includes"] = [".*"]
        listeners["excludes"] = [self.name]

        ### default tags to tag output streams
        tags = []
        self.properties["tags"] = tags

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
    def create_worker(self, input_stream, tags=None, id=None):
        # TODO: REVISE AS PART OF MI/MO
        # if self.properties['aggregator']:
        #     # generate unique id for aggregate producer
        #     if self.aggregate_producer_id is None:
        #         self.aggregate_producer_id = self.name + ":" + str(hex(uuid.uuid4().fields[0]))[2:]
        #     # if id not set use aggregate_producer
        #     if id is None:
        #         id = self.aggregate_producer_id

        worker = Worker(
            input_stream,
            prefix=self.cid,
            agent=self,
            processor=lambda *args, **kwargs: self.processor(
                *args, **kwargs, tags=tags
            ),
            session=self.session,
            properties=self.properties,
        )

        return worker

    ###### default processor, override
    def default_processor(
        self,
        stream,
        id,
        label,
        data,
        dtype=None,
        tags=None,
        properties=None,
        worker=None,
    ):
        logging.info("default processor: override")
        logging.info(stream)
        logging.info(tags)
        logging.info(id)
        logging.info(label)
        logging.info(data)
        logging.info(properties)
        logging.info(worker)

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

    def session_listener(self, id, message):
        # listen to session stream

        label = message["label"]

        if label == "ADD":
            data = json.loads(message["data"])

            input_stream = data["stream"]
            tags = data["tags"]

            # agent define what to listen to using include/exclude expressions
            logging.info("checking match.")
            matches = self._match_listen_to_tags(tags)
            logging.info("Done checking match.")
            if len(matches) == 0:
                logging.info(
                    "Not listening to {stream} with {tags}...".format(
                        stream=input_stream, tags=tags
                    )
                )
                return

            logging.info(
                "Spawning worker for stream {stream} with matching tags {matches}...".format(
                    stream=input_stream, matches=matches
                )
            )
            session_stream = self.session.get_stream()

            # create and start worker
            # TODO; pass tag to worker, with parameters
            worker = self.create_worker(input_stream, tags=matches)
            self.workers.append(worker)

            logging.info(
                "Spawned worker for stream {stream}...".format(stream=input_stream)
            )

    def _match_listen_to_tags(self, tags):
        matches = set()

        includes = self.properties["listens"]["includes"]
        excludes = self.properties["listens"]["excludes"]

        logging.info("includes")
        for i in includes:
            logging.info(i)
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
                    matches = matches.union(m)
                    logging.info("Matched include rule: {rule}".format(rule=str(i)))

        if len(matches) == 0:
            return list(matches)

        logging.info("excludes")
        for x in excludes:
            logging.info(x)
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
            logging.error("No current session to interact with.")
            return

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

        logging.info("Started agent {name}".format(name=self.name))

    def _start_session_consumer(self):
        # start a consumer to listen to session stream
        if self.session:
            session_stream = self.session.get_stream()

            if session_stream:
                self.consumer = Consumer(
                    session_stream,
                    name=self.name,
                    listener=lambda id, message: self.session_listener(id, message),
                    properties=self.properties,
                )
                self.consumer.start()

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

        self.consumer = None

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
        self.consumer.wait()

    def _start_consumer(self):
        # platform stream
        stream = "PLATFORM:" + self.platform + ":STREAM"
        self.consumer = Consumer(
            stream,
            name=self.agent_name + "FACTORY",
            listener=lambda id, message: self.platform_listener(id, message),
            properties=self.properties,
        )
        self.consumer.start()

    def platform_listener(self, id, message):
        # listen to platform stream

        logging.info("Processing: " + str(message))

        label = message["label"]

        # only process newer instructions
        mt = int(id.split("-")[0])
        if mt < self.ct:
            return

        if label == "INSTRUCTION":
            data = json.loads(message["data"])

            code = data["code"]
            params = data["params"]

            session = params["session"]
            registry = params["registry"]
            agent = params["agent"]

            # start with factory properties, merge properties from API call
            properties_from_api = params["properties"]
            properties_from_factory = self.properties
            agent_properties = {}
            agent_properties = json_utils.merge_json(
                agent_properties, properties_from_factory
            )
            agent_properties = json_utils.merge_json(
                agent_properties, properties_from_api
            )
            input = None

            if "input" in agent_properties:
                input = agent_properties["input"]
                del agent_properties["input"]

            if self.agent_name == agent:
                logging.info("Launching Agent: " + agent + "...")
                logging.info(
                    "Agent Properties: " + json.dumps(agent_properties) + "..."
                )

                name = agent
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
