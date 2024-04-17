###### OS / Systems
import os
import sys
from xml.sax.handler import property_dom_node

import pydash

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/agent/")

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
from redis.commands.json.path import Path

###### Blue
from producer import Producer


class Session:
    def __init__(self, name=None, properties={}):

        # set a unique id per session
        if name is None:
            self.name = "SESSION" + ":" + str(hex(uuid.uuid4().fields[0]))[2:]
        else:
            self.name = name

        self.properties = properties

        # producer to emit session events
        self.producer = None

        self._initialize()

        self.agents = {}

        self._start()

    ###### INITIALIZATION
    def _initialize(self):
        self._initialize_properties()

    def _initialize_properties(self):

        if "db.host" not in self.properties:
            self.properties["db.host"] = "localhost"

        if "db.port" not in self.properties:
            self.properties["db.port"] = 6379

    def get_stream(self):
        return self.producer.get_stream()

    ###### AGENTS, NOTIFICATION
    def add_agent(self, agent):
        self._init_agent_data_namespace(agent)
        self.agents[agent.name] = agent

        # add join message
        data = {}
        data["agent"] = agent.name
        label = "JOIN"
        self.producer.write(data=data, dtype="json", label=label, eos=False)

    def remove_agent(self, agent):
        ### TODO: Purge agent memory, probably not..

        if agent.name in self.agents:
            del self.agents[agent.name]

        # add leave message
        data = {}
        data["agent"] = agent.name
        label = "LEAVE"
        self.producer.write(data=data, dtype="json", label=label, eos=False)

    def list_agents(self):
        ## read stream in producer, scan join/leave events
        agents = set()

        m = self.producer.read_all()
        for message in m:
            label = message["label"]
            if label == "JOIN":
                data = message["data"]
                data = json.loads(data)
                agent = data["agent"]
                agents.add(agent)
            if label == "LEAVE":
                data = message["data"]
                data = json.loads(data)
                agent = data["agent"]
                agents.remove(agent)
        return list(agents)

    def notify(self, worker_stream, tags):
        # # start producer on first write
        # self._start_producer()

        # create data namespace to share data on stream, success = True, if not existing
        success = self._init_stream_data_namespace(worker_stream)
        logging.info(
            "inited stream data namespace {} {}".format(worker_stream, success)
        )

        # add to stream to notify others, unless it exists
        if success:
            data = {}
            data["stream"] = worker_stream
            data["tags"] = tags
            label = "ADD"
            self.producer.write(data=data, dtype="json", label=label, eos=False)

    ###### MEMORY RELATED
    def __get_json_value(self, value):
        if value is None:
            return None
        if type(value) is list:
            if len(value) == 0:
                return None
            else:
                return value[0]
        else:
            return value

    ## session data
    def _init_data_namespace(self):
        # create namespaces for any session common data, and stream-specific data
        self.connection.json().set(
            self._get_data_namespace(),
            "$",
            {
                "memory": {"common": {}, "stream": {}, "agent": {}},
                "metadata": {},
            },
            nx=True,
        )

    def _get_data_namespace(self):
        return self.name + ":DATA"

    def set_data(self, key, value):
        self.connection.json().set(
            self._get_data_namespace(), "$.memory.common." + key, value
        )

    def get_data(self, key):
        value = self.connection.json().get(
            self._get_data_namespace(), Path("$.memory.common." + key)
        )
        return self.__get_json_value(value)

    def set_metadata(self, key, value):
        self.connection.json().set(
            self._get_data_namespace(), "$.metadata." + key, value
        )

    def get_metadata(self, key=""):
        value = self.connection.json().get(
            self._get_data_namespace(),
            Path("$.metadata" + ("" if pydash.is_empty(key) else ".") + key),
        )
        return self.__get_json_value(value)

    def append_data(self, key, value):
        self.connection.json().arrappend(
            self._get_data_namespace(), "$.memory.common." + key, value
        )

    def get_data_len(self, key):
        return self.connection.json().arrlen(
            self._get_data_namespace(), "$.memory.common." + key
        )

    ## session agent data (among agent workers)
    def _init_agent_data_namespace(self, agent):
        # create namespaces for stream-specific data
        return self.connection.json().set(
            self._get_data_namespace(),
            "$.memory.agent." + self._get_agent_data_namespace(agent),
            {},
            nx=True,
        )

    def _get_agent_data_namespace(self, agent):
        return agent.name

    def set_agent_data(self, agent, key, value):
        self.connection.json().set(
            self._get_data_namespace(),
            "$.memory.agent." + self._get_agent_data_namespace(agent) + "." + key,
            value,
        )

    def get_agent_data(self, agent, key):
        value = self.connection.json().get(
            self._get_data_namespace(),
            Path("$.memory.agent." + self._get_agent_data_namespace(agent) + "." + key),
        )
        return self.__get_json_value(value)

    def append_agent_data(self, agent, key, value):
        self.connection.json().arrappend(
            self._get_data_namespace(),
            "$.memory.agent." + self._get_agent_data_namespace(agent) + "." + key,
            value,
        )

    def get_agent_data_len(self, agent, key):
        return self.connection.json().arrlen(
            self._get_data_namespace(),
            Path("$.memory.agent." + self._get_agent_data_namespace(agent) + "." + key),
        )

    ## session stream data
    def _init_stream_data_namespace(self, stream):
        # create namespaces for stream-specific data
        return self.connection.json().set(
            self._get_data_namespace(),
            "$.memory.stream." + self._get_stream_data_namespace(stream),
            {"common": {}, "agent": {}},
            nx=True,
        )

    def _get_stream_data_namespace(self, stream):
        return stream

    def set_stream_data(self, stream, key, value):
        self.connection.json().set(
            self._get_data_namespace(),
            "$.memory.stream."
            + self._get_stream_data_namespace(stream)
            + ".common."
            + key,
            value,
        )

    def get_stream_data(self, stream, key):
        value = self.connection.json().get(
            self._get_data_namespace(),
            Path(
                "$.memory.stream."
                + self._get_stream_data_namespace(stream)
                + ".common."
                + key
            ),
        )
        return self.__get_json_value(value)

    def append_stream_data(self, stream, key, value):
        self.connection.json().arrappend(
            self._get_data_namespace(),
            "$.memory.stream."
            + self._get_stream_data_namespace(stream)
            + ".common."
            + key,
            value,
        )

    def get_stream_data_len(self, stream, key):
        return self.connection.json().arrlen(
            self._get_data_namespace(),
            Path(
                "$.memory.stream."
                + self._get_stream_data_namespace(stream)
                + ".common."
                + key
            ),
        )

    ## session stream worker data
    def _init_stream_agent_data_namespace(self, stream, agent):
        # create namespaces for stream-specific data
        return self.connection.json().set(
            self._get_data_namespace(),
            "$.memory.stream."
            + self._get_stream_data_namespace(stream)
            + ".agent."
            + self._get_stream_agent_data_namespace(agent),
            {},
            nx=True,
        )

    def _get_stream_agent_data_namespace(self, agent):
        return agent

    def set_stream_agent_data(self, stream, agent, key, value):
        self.connection.json().set(
            self._get_data_namespace(),
            "$.memory.stream."
            + self._get_stream_data_namespace(stream)
            + ".agent."
            + self._get_stream_agent_data_namespace(agent)
            + "."
            + key,
            value,
        )

    def get_stream_agent_data(self, stream, agent, key):
        value = self.connection.json().get(
            self._get_data_namespace(),
            Path(
                "$.memory.stream."
                + self._get_stream_data_namespace(stream)
                + ".agent."
                + self._get_stream_agent_data_namespace(agent)
                + "."
                + key
            ),
        )
        return self.__get_json_value(value)

    def append_stream_agent_data(self, stream, agent, key, value):
        self.connection.json().arrappend(
            self._get_data_namespace(),
            "$.memory.stream."
            + self._get_stream_data_namespace(stream)
            + ".agent."
            + self._get_stream_agent_data_namespace(agent)
            + "."
            + key,
            value,
        )

    def get_stream_agent_data_len(self, stream, agent, key):
        return self.connection.json().arrlen(
            self._get_data_namespace(),
            Path(
                "$.memory.stream."
                + self._get_stream_data_namespace(stream)
                + ".agent."
                + self._get_stream_agent_data_namespace(agent)
                + "."
                + key
            ),
        )

    ###### OPERATIONS
    def _start(self):
        # logging.info('Starting session {name}'.format(name=self.name))
        self._start_connection()

        # initialize session data
        self._init_data_namespace()

        # start  producer to emit session events
        self._start_producer()

        logging.info("Started session {name}".format(name=self.name))

    def _start_connection(self):
        host = self.properties["db.host"]
        port = self.properties["db.port"]

        self.connection = redis.Redis(host=host, port=port, decode_responses=True)

    def _start_producer(self):
        # start, if not started
        if self.producer == None:
            producer = Producer("SESSION", sid=self.name, properties=self.properties)
            producer.start()
            self.producer = producer

    def stop(self):
        # stop agents
        for agent_name in self.agents:
            self.agents[agent_name].stop()

        # put EOS to stream
        self.producer.write(label="EOS")

    def wait(self):
        for agent_name in self.agents:
            self.agents[agent_name].wait()

        while True:
            time.sleep(1)


#######################
### EXAMPLE
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--loglevel", default="INFO", type=str)

    args = parser.parse_args()

    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())

    # create session
    session = Session()

    # wait for session
    session.wait()
