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
from connection import PooledConnectionFactory
from tracker import PerformanceTracker, SystemPerformanceTracker, Metric, MetricGroup

def create_uuid():
    return str(hex(uuid.uuid4().fields[0]))[2:]

# system tracker
system_tracker = None

class AgentPerformanceTracker(PerformanceTracker):
    def __init__(self, agent, properties=None, callback=None):
        self.agent = agent
        super().__init__(prefix=agent.cid, properties=properties, inheritance="perf.platform.agent", callback=callback)

    def collect(self): 
        super().collect()

        ### agent group
        agent_group = MetricGroup(id="agent", label="Agent Info", visibility=False)
        self.data.add(agent_group)


        # agent info
        name_metric = Metric(id="name", label="Name", value=self.agent.name, visibility=False)
        agent_group.add(name_metric)
        cid_metric = Metric(id="id", label="ID", value=self.agent.cid, visibility=False)
        agent_group.add(cid_metric)
        session_metric = Metric(id="sessuib", label="Session", value=self.agent.session.cid, visibility=False)
        agent_group.add(session_metric)

        ### workers group
        workers_group = MetricGroup(id="workers", label="Workers Info")
        self.data.add(agent_group)

        num_workers_metric = Metric(id="num_workers", label="Num Workers", value=len(list(self.agent.workers.values())), visibility=True)
        workers_group.add(num_workers_metric)
        
        workers_list_group = MetricGroup(id="workers_list", label="Workers List", type="list")
        workers_group.add(workers_list_group)


        for worker_id in self.agent.workers:
            worker = self.agent.workers[worker_id]
            stream = None
            if worker.consumer:
                if worker.consumer.stream:
                    stream = worker.consumer.stream

            worker_group = MetricGroup(id=worker_id, label=worker.cid)
            workers_list_group.add(worker_group)

            worker_name_metric = Metric(id="name", label="Name", value=worker.name, type="text")
            worker_group.add(worker_name_metric)

            worker_cid_metric = Metric(id="cid", label="ID", value=worker.cid, type="text", visibility=False)
            worker_group.add(worker_cid_metric)

            worker_stream_metric =  Metric(id="strean", label="Stream", value=stream, type="text")
            worker_group.add(worker_stream_metric)
           

        return self.data.toDict()
    
class AgentFactoryPerformanceTracker(PerformanceTracker):
    def __init__(self, agent_factory, properties=None, callback=None):
        self.agent_factory = agent_factory
        super().__init__(prefix=agent_factory.cid, properties=properties, inheritance="perf.platform.agentfactory", callback=callback)

    def collect(self): 
        super().collect()

         ### db group
        db_group = MetricGroup(id="database", label="Database Info")
        self.data.add(db_group)

        ### db connections group
        db_connections_group = MetricGroup(id="database_connections", label="Connections Info")
        db_group.add(db_connections_group)

        connections_factory_id = Metric(id="connection_factory_id", label="Connections Factory ID", type="text", value=self.agent_factory.connection_factory.get_id())
        db_connections_group.add(connections_factory_id)

        # db connection info
        num_created_connections_metric = Metric(id="num_created_connections", label="Num Total Connections", type="series", value=self.agent_factory.connection_factory.count_created_connections())
        db_connections_group.add(num_created_connections_metric)
        num_in_use_connections_metric = Metric(id="num_in_use_connections", label="Num In Use Connections", type="series", value=self.agent_factory.connection_factory.count_in_use_connections())
        db_connections_group.add(num_in_use_connections_metric)
        num_available_connections_metric = Metric(id="num_available_connections", label="Num Available Connections", type="series", value=self.agent_factory.connection_factory.count_available_connections())
        db_connections_group.add(num_available_connections_metric)

        return self.data.toDict()

    
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
        self.workers = {}

        # event producers, by form_id
        self.event_producers = {}

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
        default_listeners["includes"] = []
        default_listeners["excludes"] = []

        ### default tags to tag output streams
        tags = {}
        self.properties["tags"] = tags

        # DEFAULT is the default output parameter
        default_tags = []
        tags["DEFAULT"] = default_tags

        # perf tracker
        self.properties["tracker.perf.platform.agent.autostart"] = False
        self.properties["tracker.perf.platform.agent.outputs"] = ["log.INFO"]

        # let consumer streams expire 
        self.properties["consumer.expiration"] = 3600 #60 minutes


    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    ###### database, data
    def _start_connection(self):
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()

    ###### worker
    # input_stream is data stream for input param, default 'DEFAULT'
    def create_worker(self, input_stream, input="DEFAULT", context=None, processor=None):
        # listen
        logging.info("Creating worker for stream {stream} for param {param}...".format(stream=input_stream, param=input))

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
            name=self.name + "-WORKER",
            prefix=p,
            agent=self,
            processor=processor,
            session=self.session,
            properties=self.properties,
            on_stop=lambda sid: self.on_worker_stop_handler(sid)
        )

        self.workers[worker.sid] = worker

        return worker

    def on_worker_stop_handler(self, worker_sid):
        if worker_sid in self.workers:
            del self.workers[worker_sid]

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
        # logging.info("instruction processor")
        # logging.info(message)
        # logging.info(input)
        # logging.info(properties)
        # logging.info(worker)

        if message.getCode() == ControlCode.EXECUTE_AGENT:
            agent = message.getArg("agent")
            if agent == self.name:
                context = message.getArg("context")
                input_streams = message.getArg("params")
                for input_param in input_streams:
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
            agent_cid = message.getArg("agent")

            # ignore streams from self
            if agent_cid == self.cid:
                return

            # agent define what to listen to using include/exclude expressions
            # logging.info("Checking listener tags...")
            matched_params = self._match_listen_to_tags(tags)
            # logging.info("Done.")

            # instructable
            # logging.info("instructable? " + str(self.properties['instructable']))
            if self.properties['instructable']:
                if 'INSTRUCTION' in set(tags):
                    # create a special worker to list to streams with instructions
                    instruction_worker = self.create_worker(stream, input="INSTRUCTION", processor=lambda *args, **kwargs: self._instruction_processor(*args, **kwargs))

            # skip
            if len(matched_params) == 0:
                # logging.info("Skipping stream {stream} with {tags}...".format(stream=stream, tags=tags))
                return

            for param in matched_params:
                tags = matched_params[param]

                # create worker
                worker = self.create_worker(stream, input=param, context=stream)

                # logging.info("Spawned worker for stream {stream}...".format(stream=stream))
        
        # session ended, stop agent
        elif message.isEOS():
            self.stop()

    def _match_listen_to_tags(self, tags):
        matched_params = {}

        # default listeners
        listeners_by_param = self.properties["listens"]
        # logging.info(json.dumps(listeners_by_param, indent=3))
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
                            # logging.info("Matched include rule: {rule} for param: {param}".format(rule=str(i), param=param))
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
                        matched_tags = matched_tags.union(m)
                        # logging.info("Matched include rule: {rule} for param: {param}".format(rule=str(i), param=param))

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
                        # logging.info("Matched exclude rule: {rule} for param: {param}".format(rule=str(x), param=param))
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
                        # logging.info("Matched exclude rule: {rule} for param: {param}".format(rule=str(x), param=param))
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

    ## data
    def set_data(self, key, value):
        self.session.set_agent_data(self, key, value)

    def get_data(self, key):
        return self.session.get_agent_data(self, key)

    def append_data(self, key, value):
        self.session.append_agent_data(self, key, value)

    def get_data_len(self, key):
        return self.session.get_agent_data_len(self, key)

    def perf_tracker_callback(self, data, tracker=None, properties=None):
        pass

    def _init_tracker(self):
        self._tracker = AgentPerformanceTracker(self, properties=self.properties, callback= lambda *args, **kwargs: self.perf_tracker_callback(*args, **kwargs) )

    def _start_tracker(self):
        # start tracker
        self._tracker.start()

    def _stop_tracker(self):
        self._tracker.stop()

    def _terminate_tracker(self):
        self._tracker.terminate()

    def _start(self):
        self._start_connection()

        # init tracker
        self._init_tracker()

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
        # stop tracker
        self._stop_tracker()

        # leave session
        self.leave_session()

        # send stop to each worker
        for worker_id in self.workers:
            worker = self.workers[worker_id]
            worker.stop()

        for worker_id in self.workers:
            del self.workers[worker_id]
        

    def wait(self):
        # send wait to each worker
        for worker_id in self.workers:
            worker = self.workers[worker_id]
            worker.wait()


class AgentFactory:
    def __init__(
        self,
        _class=Agent,
        _name="Agent",
        _registry="default",
        platform="default",
        properties={},
    ):
        self._class = _class
        self._name = _name
        self._registry = _registry

        self.platform = platform

        self.name = "AGENT_FACTORY"
        self.id = self._name 
        self.sid = self.name + ":" + self.id

        self.prefix = "PLATFORM:" + self.platform
        self.cid = self.prefix + ":" + self.sid

        self._initialize(properties=properties)

        self.platform_consumer = None

        # creation time
        self.started = int(time.time()) #math.floor(time.time_ns() / 1000000)

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

        # perf tracker
        self.properties["tracker.perf.platform.agentfactory.autostart"] = True
        self.properties["tracker.perf.platform.agentfactory.outputs"] = ["log.INFO", "pubsub"]

        # system perf tracker
        self.properties["tracker.perf.system.autostart"] = True
        self.properties["tracker.perf.system.outputs"] = ["log.INFO", "pubsub"]
       
        # no consumer idle tracking
        self.properties['tracker.idle.consumer.autostart'] = False

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

        # override agent factory idle tracker expiration
        # to never expire, as platform streams that agent
        # factories listen to are long running streams
        self.properties['consumer.expiration'] = None

    ###### database, data
    def _start_connection(self):
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()

    ###### factory functions
    def create(self, **kwargs):
        print(kwargs)
        klasse = self._class
        instanz = klasse(**kwargs)
        return instanz

    def perf_tracker_callback(self, data, tracker=None, properties=None):
        pass

    def _init_tracker(self):
        # agent factory perf tracker
        self._tracker = AgentFactoryPerformanceTracker(self, properties=self.properties, callback= lambda *args, **kwargs: self.perf_tracker_callback(*args, **kwargs) )

        # system tracker
        global system_tracker 
        system_tracker = SystemPerformanceTracker(properties=self.properties)

    def _start_tracker(self):
        # start tracker
        self._tracker.start()

    def _stop_tracker(self):
        self._tracker.stop()

    def _terminate_tracker(self):
        self._tracker.terminate()

    def _start(self):
        self._start_connection()

        # init tracker
        self._init_tracker()

        self._start_consumer()
        logging.info(
            "Started agent factory for agent: {name} in registry: {registry} on platform: {platform} ".format(
                name=self._name,
                registry=self._registry,
                platform=self.platform,
            )
        )

    def wait(self):
        self.platform_consumer.wait()

    def _start_consumer(self):
        # platform stream
        stream = "PLATFORM:" + self.platform + ":STREAM"
        self.platform_consumer = Consumer(
            stream,
            name=self._name + "_FACTORY",
            listener=lambda message: self.platform_listener(message),
            properties=self.properties,
        )
        self.platform_consumer.start()

    def _extract_epoch(self, id):
        e = id.split("-")[0]
        return int(int(e) / 1000)
    
    def platform_listener(self, message):
        # listen to platform stream

        # logging.info("Processing: " + str(message))
        id = message.getID()

        # only process newer instructions
        message_time = self._extract_epoch(id)

        # ignore past instructions
        if message_time < self.started:
            return

        # check if join session
        if message.getCode() == ControlCode.JOIN_SESSION:
            session = message.getArg("session")
            registry = message.getArg("registry")
            agent = message.getArg("agent")

            # check match in canonical name space, i.e.
            # <base_name> or <base_name>___<derivative__name>___<derivative__name>...
            ca = agent.split("_")
            base_name = ca[0]

            if self._name == base_name:
                name = agent

                # start with factory properties, merge properties from API call
                properties_from_api = message.getArg("properties")
                # properties_from_factory = self.properties
                agent_properties = {}
                # agent_properties = json_utils.merge_json(agent_properties, properties_from_factory)
                agent_properties = json_utils.merge_json(agent_properties, properties_from_api)
                input = None

                if "input" in agent_properties:
                    input = agent_properties["input"]
                    del agent_properties["input"]

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
            _class=Agent,
            _name=args.serve,
            _registry=args.registry,
            platform=platform,
            properties=properties,
        )
        af.wait()
