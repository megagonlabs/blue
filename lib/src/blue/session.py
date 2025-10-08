###### Parsers, Utils
import time
import argparse
import logging
import time
import pydash

###### Backend, Databases
from redis.commands.json.path import Path

###### Blue
from blue.core import Entity
from blue.stream import ControlCode
from blue.pubsub import Producer
from blue.connection import PooledConnectionFactory
from blue.utils import uuid_utils, log_utils


###############
### Session
#
class Session(Entity):
    """
    Session to provide context for managing agents and streams.
    Session data is shared among all agents in the session.
    """

    def __init__(self, id=None, sid=None, cid=None, prefix=None, suffix=None, properties=None):
        super().__init__(name="SESSION", id=id, sid=sid, cid=cid, prefix=prefix, suffix=suffix)

        self.connection = None

        # session stream
        self.producer = None

        self.agents = {}

        self._initialize(properties=properties)

        self._start()

    ###### INITIALIZATION
    def _initialize(self, properties=None):
        """Initialize session properties and logger.

        Parameters:
            properties: Dictionary of properties to configure the session. Defaults to None.
        """
        self._initialize_properties()
        self._update_properties(properties=properties)

        self._initialize_logger()

    def _initialize_properties(self):
        """Initialize default session properties."""
        self.properties = {}

        # db connectivity
        self.properties['db.host'] = 'localhost'
        self.properties['db.port'] = 6379

    def _update_properties(self, properties=None):
        """Update session properties with provided values.

        Parameters:
            properties: Dictionary of properties to update. Defaults to None.
        """
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def get_stream(self):
        """Get the session's stream identifier.

        Returns:
            The session's stream identifier.
        """
        return self.producer.get_stream()

    def _initialize_logger(self):
        """Initialize the session logger."""
        self.logger = log_utils.CustomLogger()
        # customize log
        self.logger.set_config_data(
            "stack",
            "%(call_stack)s",
        )
        self.logger.set_config_data("session", self.sid, -1)

    ###### AGENTS, NOTIFICATION
    def add_agent(self, agent):
        """
        Add an agent to the session and initialize its data namespace.
        Announces agent addition via control message to the session stream.

        Parameters:
            agent: Agent object to be added to the session.
        """
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
        """
        Remove an agent from the session and announce its removal via control message to the session stream.

        Parameters:
            agent: Agent object to be removed from the session.
        """
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
        """
        List all agents currently in the session.

        Returns:
            List of agents in the session.
        """
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
        """
        Notify the session about a new output stream created by an agent.
        Updates stream metadata and announces the new stream via control message to the session stream.

        Parameters:
            agent: Agent object that created the output stream.
            output_stream: Identifier of the output stream.
            tags: List of tags associated with the output stream.
        """
        self._update_stream_metadata(output_stream, agent, tags)

        # add to stream to notify others, unless it exists
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
        """Initialize the metadata namespace for the session."""
        # create namespaces for any session common data, and stream-specific data
        self.connection.json().set(
            self._get_metadata_namespace(),
            "$",
            {"members": {}, 'pinned': {}, 'debugger': {}},
            nx=True,
        )

        # add created_date
        self.set_metadata("created_date", int(time.time()), nx=True)

        # init budget
        self._init_budget()

    def _get_metadata_namespace(self):
        """Get the metadata namespace for the session."""
        return self.cid + ":METADATA"

    def set_metadata(self, key, value, nx=False):
        """
        Set metadata for the session.

        Parameters:
            key: Metadata key.
            value: Metadata value.
            nx: If True, set the value only if the key does not already exist. Defaults to False.
        """
        self.connection.json().set(self._get_metadata_namespace(), "$." + key, value, nx=nx)

    def get_metadata(self, key=""):
        """
        Get metadata for the session.

        Parameters:
            key: Metadata key. If empty, returns all metadata. Defaults to "".

        Returns:
            Metadata value or all metadata if key is empty.
        """
        value = self.connection.json().get(
            self._get_metadata_namespace(),
            Path("$" + ("" if pydash.is_empty(key) else ".") + key),
        )
        return self.__get_json_value(value)

    ## budget
    def _init_budget(self):
        """Initialize budget metadata for the session, such as cost, accuracy, and latency for allocation and usage tracking."""
        self.set_metadata('budget', {}, nx=True)
        self.set_metadata('budget.allocation', {}, nx=True)
        self.set_metadata('budget.use', {}, nx=True)
        self.set_budget_allocation(cost=-1, accuracy=-1, latency=-1, nx=True)

    def get_budget(self):
        """Get the overall budget metadata for the session.

        Returns:
            (dict): Dictionary containing overall budget metadata.
        """
        return self.get_metadata('budget')

    def set_budget_allocation(self, cost=None, accuracy=None, latency=None, nx=False):
        """
        Set budget allocation metadata for the session.

        Parameters:
            cost: Cost allocation value.
            accuracy: Accuracy allocation value.
            latency: Latency allocation value.
            nx (bool): If True, set the value only if the key does not already exist. Defaults to False.
        """
        if cost is not None:
            self.set_metadata('budget.allocation.cost', cost, nx)
        if accuracy is not None:
            self.set_metadata('budget.allocation.accuracy', accuracy, nx)
        if latency is not None:
            self.set_metadata('budget.allocation.latency', latency, nx)

    def get_budget_allocation(self):
        """Get the budget allocation metadata for the session.

        Returns:
            Dictionary containing budget allocation metadata.
        """
        return self.get_metadata(key='budget.allocation')

    def _set_budget_use(self, cost=None, accuracy=None, latency=None):
        """
        Set budget usage metadata for the session.

        Parameters:
            cost: Cost usage value.
            accuracy: Accuracy usage value.
            latency: Latency usage value.
        """
        if cost:
            self.set_metadata('budget.use.cost', cost)
        if accuracy:
            self.set_metadata('budget.use.accuracy', accuracy)
        if latency:
            self.set_metadata('budget.use.latency', latency)

    def update_budget_use(self, cost=None, accuracy=None, latency=None):
        """
        !!! warning "Not Implemented"

        Update budget usage metadata for the session by incrementing existing values.

        Parameters:
            cost: Cost usage value to increment.
            accuracy: Accuracy usage value to increment.
            latency: Latency usage value to increment.
        """
        # TODO
        pass

    def get_budget_use(self):
        """Get the budget usage metadata for the session.

        Returns:
            (dict): Dictionary containing budget usage metadata.
        """
        return self.get_metadata(key='budget.use')

    ## session data (shared by all agents)
    def _init_data_namespace(self):
        """Initialize session data namespace."""
        # create namespaces for any session common data, and stream-specific data
        self.connection.json().set(
            self._get_data_namespace(),
            "$",
            {},
            nx=True,
        )

    def _get_data_namespace(self):
        """Get the data namespace for the session.

        Returns:
            The data namespace for the session.
        """

        return self.cid + ":DATA"

    def set_data(self, key, value):
        """Set session data for a specific key.

        Parameters:
            key: Data key.
            value (Any): Data value.
        """
        self.connection.json().set(self._get_data_namespace(), "$." + key, value)

    def delete_data(self, key):
        """Delete session data for a specific key.

        Parameters:
            key (str): Data key to delete.
        """
        self.connection.json().delete(self._get_data_namespace(), "$." + key)

    def get_data(self, key):
        """Get session data for a specific key.

        Parameters:
            key (str): Data key.

        Returns:
            Data value for the specified key.
        """
        value = self.connection.json().get(self._get_data_namespace(), Path("$." + key))
        return self.__get_json_value(value)

    def get_all_data(self):
        """Get all session data.

        Returns:
            (dict): Dictionary containing all session data.
        """
        value = self.connection.json().get(self._get_data_namespace(), Path("$"))
        return self.__get_json_value(value)

    def append_data(self, key, value):
        """Append a value to a list in session data for a specific key.

        Parameters:
            key: Data key.
            value: Value to append to the list.
        """
        self.connection.json().arrappend(self._get_data_namespace(), "$." + key, value)

    def get_data_len(self, key):
        """Get the length of a list in session data for a specific key.

        Parameters:
            key: Data key.

        Returns:
            (int): Length of the list for the specified key.
        """
        return self.connection.json().arrlen(self._get_data_namespace(), "$." + key)

    ## session agent data (shared by all workers of an agent)
    def _get_agent_data_namespace(self, agent):
        """Get the data namespace for a specific agent in the session.

        Parameters:
            agent: Agent object.

        Returns:
            The data namespace for the specified agent.
        """
        return agent.cid + ":DATA"

    def _init_agent_data_namespace(self, agent):
        """Initialize data namespace for a specific agent in the session.

        Parameters:
            agent: Agent object.
        """
        # create namespaces for stream-specific data
        return self.connection.json().set(
            self._get_agent_data_namespace(agent),
            "$",
            {},
            nx=True,
        )

    def set_agent_data(self, agent, key, value):
        """Set data for a specific key in an agent's data namespace.

        Parameters:
            agent: Agent object.
            key: Data key.
            value: Data value.
        """
        self.connection.json().set(
            self._get_agent_data_namespace(agent),
            "$." + key,
            value,
        )

    def get_agent_data(self, agent, key):
        """Get data for a specific key in an agent's data namespace.

        Parameters:
            agent: Agent object.
            key: Data key.

        Returns:
            (Any): Data value for the specified key.
        """
        value = self.connection.json().get(
            self._get_agent_data_namespace(agent),
            Path("$." + key),
        )
        return self.__get_json_value(value)

    def get_all_agent_data(self, agent):
        """Get all data in an agent's data namespace.

        Parameters:
            agent: Agent object.

        Returns:
            (dict): Dictionary containing all data for the specified agent.
        """
        value = self.connection.json().get(
            self._get_agent_data_namespace(agent),
            Path("$"),
        )
        return self.__get_json_value(value)

    def append_agent_data(self, agent, key, value):
        """Append a value to a list in an agent's data namespace for a specific key.

        Parameters:
            agent: Agent object.
            key: Data key.
            value: Value to append to the list.
        """
        self.connection.json().arrappend(
            self._get_agent_data_namespace(agent),
            "$." + key,
            value,
        )

    def get_agent_data_len(self, agent, key):
        """Get the length of a list in an agent's data namespace for a specific key.

        Parameters:
            agent: Agent object.
            key: Data key.

        Returns:
            Length of the list for the specified key.
        """
        return self.connection.json().arrlen(
            self._get_agent_data_namespace(agent),
            Path("$." + key),
        )

    def _get_stream_metadata_namespace(self, stream):
        """
        Get the metadata namespace for a specific stream in the session.
        """
        return stream + ":METADATA"

    def _update_stream_metadata(self, stream, agent, tags):
        """
        Update metadata for a specific stream in the session with agent and tags information.

        Parameters:
            stream: Stream identifier.
            agent: Agent object that created the stream.
            tags: List of tags associated with the stream.
        """
        metadata_tags = {}
        for tag in tags:
            metadata_tags.update({tag: True})

        self.connection.json().set(self._get_stream_metadata_namespace(stream), "$." + 'created_by', agent.name)
        self.connection.json().set(self._get_stream_metadata_namespace(stream), "$." + 'id', agent.id)
        self.connection.json().set(self._get_stream_metadata_namespace(stream), "$." + 'tags', metadata_tags)

    ## session stream data
    def _get_stream_data_namespace(self, stream):
        """Get the data namespace for a specific stream in the session.

        Parameters:
            stream: Stream identifier.

        Returns:
            The data namespace for the specified stream.
        """
        return stream + ":DATA"

    def set_stream_data(self, stream, key, value):
        """Set data for a specific key in a stream's data namespace.

        Parameters:
            stream: Stream identifier.
            key: Data key.
            value: Data value to set.
        """
        self.connection.json().set(
            self._get_stream_data_namespace(stream),
            "$." + key,
            value,
        )

    def get_stream_data(self, stream, key):
        """Get data for a specific key in a stream's data namespace.

        Parameters:
            stream: Stream identifier.
            key: Data key.

        Returns:
            Data value for the specified key.
        """
        value = self.connection.json().get(
            self._get_stream_data_namespace(stream),
            Path("$." + key),
        )
        return self.__get_json_value(value)

    def get_all_stream_data(self, stream):
        """Get all data in a stream's data namespace.

        Parameters:
            stream: Stream identifier.

        Returns:
            All data in the stream's data namespace.
        """
        value = self.connection.json().get(
            self._get_stream_data_namespace(stream),
            Path("$"),
        )
        return self.__get_json_value(value)

    def append_stream_data(self, stream, key, value):
        """Append a value to a list in a stream's data namespace for a specific key.

        Parameters:
            stream: Stream identifier.
            key: Data key.
            value: Value to append to the list.
        """
        self.connection.json().arrappend(
            self._get_stream_data_namespace(stream),
            "$." + key,
            value,
        )

    def get_stream_data_len(self, stream, key):
        """Get the length of a list in a stream's data namespace for a specific key.

        Parameters:
            stream: Stream identifier.
            key: Data key.

        Returns:
            Length of the list for the specified key.
        """
        return self.connection.json().arrlen(
            self._get_stream_data_namespace(stream),
            Path("$." + key),
        )

    def to_dict(self):
        """Get a dictionary representation of the session, including its metadata.

        Returns:
            Dictionary containing session metadata and identifier.
        """
        return {**self.get_metadata(), "id": self.sid}

    def get_stream_debug_info(self):
        """Get debug information for all streams in the session.

        Returns:
            Dictionary containing debug information for all streams.
        """
        streams_metadata_ids = self.connection.keys("*" + self.sid + "*:STREAM:METADATA")
        debug_info = {}
        for streams_metadata_id in streams_metadata_ids:
            stream_id = streams_metadata_id[: -len(":METADATA")]
            stream_metadata = self.connection.json().get(streams_metadata_id)
            debug_info[stream_id] = stream_metadata

        return debug_info

    ###### OPERATIONS
    def _start(self):
        """Start the session by establishing a database connection, initializing metadata and data namespaces, and starting the session producer."""
        self._start_connection()

        # initialize session metadata
        self._init_metadata_namespace()

        # initialize session data
        self._init_data_namespace()

        # start  producer to emit session events
        self._start_producer()

    def _start_connection(self):
        """Establish a database connection using the provided properties."""
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()

    def _start_producer(self):
        """Start the session producer."""
        # start, if not started
        if self.producer == None:

            producer = Producer(sid="STREAM", prefix=self.cid, properties=self.properties, owner=self.sid)
            producer.start()
            self.producer = producer

    def stop(self):
        """Stop the session by stopping all agents and writing an end-of-stream message to the session stream."""
        # stop agents
        for agent_name in self.agents:
            self.agents[agent_name].stop()

        # put EOS to stream
        self.producer.write_eos()

    def wait(self):
        """Wait for all agents in the session to complete."""
        for agent_name in self.agents:
            self.agents[agent_name].wait()

        while True:
            time.sleep(1)
