###### OS / Systems
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

###### Parsers, Formats, Utils
import json

###### Backend, Databases
import redis
from redis.commands.json.path import Path

###### Blue
from producer import Producer


class Session:
    def __init__(self, name="SESSION", id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):

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

        # session stream
        self.producer = None

        self.agents = {}

        self._initialize(properties=properties)

        self._start()

    ###### INITIALIZATION
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        self.properties = {}

        # db connectivity
        self.properties['db.host'] = 'localhost'
        self.properties['db.port'] = 6379

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def get_stream(self):
        return self.producer.get_stream()

    ###### AGENTS, NOTIFICATION
    def add_agent(self, agent):
        self._init_agent_data_namespace(agent)
        self.agents[agent.name] = agent

        # add join message
        label = "INSTRUCTION"
        data = {}
        data["code"] = "ADD_AGENT"
        data["params"] = {}
        data["params"]["name"] = agent.name
        data["params"]["sid"] = agent.sid

        self.producer.write(data=data, dtype="json", label=label, eos=False)

    def remove_agent(self, agent):
        ### TODO: Purge agent memory, probably not..

        if agent.name in self.agents:
            del self.agents[agent.name]

        # add leave message
        label = "INSTRUCTION"
        data = {}
        data["code"] = "REMOVE_AGENT"
        data["params"] = {}
        data["params"]["name"] = agent.name
        data["params"]["sid"] = agent.sid
        data["params"]["cid"] = agent.cid

        self.producer.write(data=data, dtype="json", label=label, eos=False)

    def list_agents(self):
        ## read stream in producer, scan join/leave events
        agents = {}

        m = self.producer.read_all()
        for message in m:
            label = message["label"]
            if label == "INSTRUCTION":
                data = json.loads(message["data"])
                code = data["code"]

                if code == "ADD_AGENT":
                    params = data["params"]
                    name = params.get('name', None)
                    sid = params.get('sid', None)
                    cid = params.get('cid', None)
                    agents[sid] = {"name": name, "sid": sid, "cid": cid}
                if code == "REMOVE_AGENT":
                    params = data["params"]
                    sid = params["sid"]
                    if sid in agents:
                        del agents[sid]

        return list(agents.values())

    def notify(self, worker_stream, tags):
        # # start producer on first write
        # self._start_producer()

        # create data namespace to share data on stream, success = True, if not existing
        success = self._init_stream_data_namespace(worker_stream)
        logging.info("inited stream data namespace {} {}".format(worker_stream, success))

        # add to stream to notify others, unless it exists
        if success:
            label = "INSTRUCTION"
            data = {}
            data["code"] = "ADD_STREAM"
            data["params"] = {}
            data["params"]["cid"] = worker_stream
            data["params"]["tags"] = tags

            self.producer.write(data=data, dtype="json", label=label, eos=False)

    ###### DATA/METADATA RELATED
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

    ## session metadata
    def _init_metadata_namespace(self):
        # create namespaces for any session common data, and stream-specific data
        self.connection.json().set(
            self._get_metadata_namespace(),
            "$",
            {"members": {}},
            nx=True,
        )

        # add created_date
        self.set_metadata("created_date", int(time.time()), nx=True)

    def _get_metadata_namespace(self):
        return self.cid + ":METADATA"

    def set_metadata(self, key, value, nx=False):
        self.connection.json().set(self._get_metadata_namespace(), "$." + key, value, nx=nx)

    def get_metadata(self, key=""):
        value = self.connection.json().get(
            self._get_metadata_namespace(),
            Path("$" + ("" if pydash.is_empty(key) else ".") + key),
        )
        return self.__get_json_value(value)

    ## session data (shared by all agents)
    def _init_data_namespace(self):
        # create namespaces for any session common data, and stream-specific data
        self.connection.json().set(
            self._get_data_namespace(),
            "$",
            {},
            nx=True,
        )

    def _get_data_namespace(self):
        return self.cid + ":DATA"

    def set_data(self, key, value):
        self.connection.json().set(self._get_data_namespace(), "$." + key, value)

    def get_data(self, key):
        value = self.connection.json().get(self._get_data_namespace(), Path("$." + key))
        return self.__get_json_value(value)

    def append_data(self, key, value):
        self.connection.json().arrappend(self._get_data_namespace(), "$." + key, value)

    def get_data_len(self, key):
        return self.connection.json().arrlen(self._get_data_namespace(), "$." + key)

    ## session agent data (shared by all workers of an agent)
    def _get_agent_data_namespace(self, agent):
        return agent.cid + ":DATA"

    def _init_agent_data_namespace(self, agent):
        # create namespaces for stream-specific data
        return self.connection.json().set(
            self._get_agent_data_namespace(agent),
            "$",
            {},
            nx=True,
        )

    def set_agent_data(self, agent, key, value):
        self.connection.json().set(
            self._get_agent_data_namespace(agent),
            "$." + key,
            value,
        )

    def get_agent_data(self, agent, key):
        value = self.connection.json().get(
            self._get_agent_data_namespace(agent),
            Path("$." + key),
        )
        return self.__get_json_value(value)

    def append_agent_data(self, agent, key, value):
        self.connection.json().arrappend(
            self._get_agent_data_namespace(agent),
            "$." + key,
            value,
        )

    def get_agent_data_len(self, agent, key):
        return self.connection.json().arrlen(
            self._get_agent_data_namespace(agent),
            Path("$." + key),
        )

    ## session stream data
    def _get_stream_data_namespace(self, stream):
        return stream + ":DATA"

    def _init_stream_data_namespace(self, stream):
        # create namespaces for stream-specific data
        return self.connection.json().set(
            self._get_stream_data_namespace(stream),
            "$",
            {},
            nx=True,
        )

    def set_stream_data(self, stream, key, value):
        self.connection.json().set(
            self._get_stream_data_namespace(stream),
            "$." + key,
            value,
        )

    def get_stream_data(self, stream, key):
        value = self.connection.json().get(
            self._get_stream_data_namespace(stream),
            Path("$." + key),
        )
        return self.__get_json_value(value)

    def append_stream_data(self, stream, key, value):
        self.connection.json().arrappend(
            self._get_stream_data_namespace(stream),
            "$." + key,
            value,
        )

    def get_stream_data_len(self, stream, key):
        return self.connection.json().arrlen(
            self._get_stream_data_namespace(stream),
            Path("$." + key),
        )

    def to_dict(self):
        metadata = self.get_metadata()
        return {
            "id": self.sid,
            "name": pydash.objects.get(metadata, "name", self.sid),
            "description": pydash.objects.get(metadata, "description", ""),
            "created_date": pydash.objects.get(metadata, "created_date", None),
            "created_by": pydash.objects.get(metadata, "created_by", None),
            "members": pydash.objects.get(metadata, "members", {}),
        }

    # ## session stream worker data
    # def _init_stream_agent_data_namespace(self, stream, agent):
    #     # create namespaces for stream-specific data
    #     return self.connection.json().set(
    #         self._get_data_namespace(),
    #         "$.stream." + self._get_stream_data_namespace(stream) + ".agent." + self._get_stream_agent_data_namespace(agent),
    #         {},
    #         nx=True,
    #     )

    # def _get_stream_agent_data_namespace(self, agent):
    #     return agent.sid

    # def set_stream_agent_data(self, stream, agent, key, value):
    #     self.connection.json().set(
    #         self._get_data_namespace(),
    #         "$.stream." + self._get_stream_data_namespace(stream) + ".agent." + self._get_stream_agent_data_namespace(agent) + "." + key,
    #         value,
    #     )

    # def get_stream_agent_data(self, stream, agent, key):
    #     value = self.connection.json().get(
    #         self._get_data_namespace(),
    #         Path("$.stream." + self._get_stream_data_namespace(stream) + ".agent." + self._get_stream_agent_data_namespace(agent) + "." + key),
    #     )
    #     return self.__get_json_value(value)

    # def append_stream_agent_data(self, stream, agent, key, value):
    #     self.connection.json().arrappend(
    #         self._get_data_namespace(),
    #         "$.stream." + self._get_stream_data_namespace(stream) + ".agent." + self._get_stream_agent_data_namespace(agent) + "." + key,
    #         value,
    #     )

    # def get_stream_agent_data_len(self, stream, agent, key):
    #     return self.connection.json().arrlen(
    #         self._get_data_namespace(),
    #         Path("$.stream." + self._get_stream_data_namespace(stream) + ".agent." + self._get_stream_agent_data_namespace(agent) + "." + key),
    #     )

    ###### OPERATIONS
    def _start(self):
        # logging.info('Starting session {name}'.format(name=self.name))
        self._start_connection()

        # initialize session metadata
        self._init_metadata_namespace()

        # initialize session data
        self._init_data_namespace()

        # start  producer to emit session events
        self._start_producer()

        logging.info("Started session {cid}".format(cid=self.cid))

    def _start_connection(self):
        host = self.properties["db.host"]
        port = self.properties["db.port"]

        self.connection = redis.Redis(host=host, port=port, decode_responses=True)

    def _start_producer(self):
        # start, if not started
        if self.producer == None:

            producer = Producer(sid="STREAM", prefix=self.cid, properties=self.properties)
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
