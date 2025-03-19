###### Parsers, Utils
import time
import argparse
import logging
import time
import pydash

###### Backend, Databases
from redis.commands.json.path import Path

###### Blue
from blue.stream import ControlCode
from blue.pubsub import Producer
from blue.connection import PooledConnectionFactory
from blue.utils import uuid_utils


###############
### Session
#
class Session:
    def __init__(self, name="SESSION", id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):
        self.connection = None
        self.name = name
        if id:
            self.id = id
        else:
            self.id = uuid_utils.create_uuid()

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
        args = {}
        args["agent"] = agent.name
        args["session"] = self.cid
        args["sid"] = agent.sid
        args["cid"] = agent.cid

        self.producer.write_control(ControlCode.ADD_AGENT, args)

    def remove_agent(self, agent):
        ### TODO: Purge agent memory, probably not..

        if agent.name in self.agents:
            del self.agents[agent.name]

        # add leave message
        args = {}
        args["agent"] = agent.name
        args["session"] = self.cid
        args["sid"] = agent.sid
        args["cid"] = agent.cid

        self.producer.write_control(ControlCode.REMOVE_AGENT, args)

    def list_agents(self):
        ## read stream in producer, scan join/leave events
        agents = {}

        m = self.producer.read_all()
        for message in m:
            if message.getCode() == ControlCode.ADD_AGENT:
                name = message.getArg('agent')
                sid = message.getArg('sid')
                cid = message.getArg('cid')
                agents[sid] = {"name": name, "sid": sid, "cid": cid}
            elif message.getCode() == ControlCode.REMOVE_AGENT:
                sid = message.getArg('sid')
                if sid in agents:
                    del agents[sid]

        return list(agents.values())

    def notify(self, agent, output_stream, tags):

        # create data namespace to share data on stream
        data_success = self._init_stream_data_namespace(output_stream)
        # logging.info("inited stream data namespace {} {}".format(output_stream, data_success))

        # create metadata namespace for stream, metadata_success = True, if not existing
        metadata_success = self._init_stream_metadata_namespace(output_stream, agent, tags)
        # logging.info("inited stream metadata namespace {} {}".format(output_stream, metadata_success))

        # add to stream to notify others, unless it exists
        if metadata_success:
            args = {}
            args["session"] = self.cid
            args["agent"] = agent.cid
            args["stream"] = output_stream
            args["tags"] = tags
            self.producer.write_control(ControlCode.ADD_STREAM, args)

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
            {"members": {}, 'pinned': {}},
            nx=True,
        )

        # add created_date
        self.set_metadata("created_date", int(time.time()), nx=True)

        # init budget
        self._init_budget()

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

    ## budget
    def _init_budget(self):
        self.set_metadata('budget', {}, nx=True)
        self.set_metadata('budget.allocation', {}, nx=True)
        self.set_metadata('budget.use', {}, nx=True)
        self.set_budget_allocation(cost=-1, accuracy=-1, latency=-1, nx=True)

    def get_budget(self):
        return self.get_metadata('budget')

    def set_budget_allocation(self, cost=None, accuracy=None, latency=None, nx=False):
        if cost is not None:
            self.set_metadata('budget.allocation.cost', cost, nx)
        if accuracy is not None:
            self.set_metadata('budget.allocation.accuracy', accuracy, nx)
        if latency is not None:
            self.set_metadata('budget.allocation.latency', latency, nx)

    def get_budget_allocation(self):
        return self.get_metadata(key='budget.allocation')

    def _set_budget_use(self, cost=None, accuracy=None, latency=None):
        if cost:
            self.set_metadata('budget.use.cost', cost)
        if accuracy:
            self.set_metadata('budget.use.accuracy', accuracy)
        if latency:
            self.set_metadata('budget.use.latency', latency)

    def update_budget_use(self, cost=None, accuracy=None, latency=None):
        # TODO
        pass

    def get_budget_use(self):
        return self.get_metadata(key='budget.use')

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

    def delete_data(self, key):
        self.connection.json().delete(self._get_data_namespace(), "$." + key)

    def get_data(self, key):
        value = self.connection.json().get(self._get_data_namespace(), Path("$." + key))
        return self.__get_json_value(value)

    def get_all_data(self):
        value = self.connection.json().get(self._get_data_namespace(), Path("$"))
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

    def get_all_agent_data(self, agent):
        value = self.connection.json().get(
            self._get_agent_data_namespace(agent),
            Path("$"),
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

    def _get_stream_metadata_namespace(self, stream):
        return stream + ":METADATA"

    def _init_stream_metadata_namespace(self, stream, agent, tags):
        # create metadata namespaces for stream
        metadata_tags = {}
        for tag in tags:
            metadata_tags.update({tag: True})
        metadata = {'created_by': agent.name, 'id': agent.id, 'tags': metadata_tags}
        return self.connection.json().set(self._get_stream_metadata_namespace(stream), "$", metadata, nx=True)

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

    def get_all_stream_data(self, stream):
        value = self.connection.json().get(
            self._get_stream_data_namespace(stream),
            Path("$"),
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
        return {**self.get_metadata(), "id": self.sid}

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

        # logging.info("Started session {cid}".format(cid=self.cid))

    def _start_connection(self):
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()

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
        self.producer.write_eos()

    def wait(self):
        for agent_name in self.agents:
            self.agents[agent_name].wait()

        while True:
            time.sleep(1)
