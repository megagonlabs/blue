###### Parsers, Formats, Utils
import time
import argparse
import logging
import time
import re
import json
import pydash


###### Blue
from blue.stream import Message, MessageType, ContentType, ControlCode
from blue.connection import PooledConnectionFactory
from blue.pubsub import Consumer, Producer
from blue.session import Session
from blue.tracker import PerformanceTracker, SystemPerformanceTracker, Metric, MetricGroup
from blue.utils import json_utils, uuid_utils, log_utils
from blue.agents.plan import AgenticPlan
from blue.constant import Separator

# system tracker
system_tracker = None


###############
### AgentPerformanceTracker
#
class AgentPerformanceTracker(PerformanceTracker):
    """Performance tracker for agents.
    Tracks metadata and performance metrics for a specific agent, such as session information, number of workers, and per-worker metadata.
    """

    def __init__(self, agent, properties=None, callback=None):
        """Initialize the AgentPerformanceTracker.

        Parameters:
            agent: The agent to track.
            properties: Additional properties for the tracker. Defaults to None.
            callback: Callback function to be called on data collection. Defaults to None.
        """
        self.agent = agent
        super().__init__(prefix=agent.cid, properties=properties, inheritance="perf.platform.agent", callback=callback)

    def collect(self):
        """Collect metadata and performance metrics for the agent."""
        super().collect()

        ### agent group
        agent_group = MetricGroup(id="agent", label="Agent Info", visibility=False)
        self.data.add(agent_group)

        # agent info
        name_metric = Metric(id="name", label="Name", value=self.agent.name, visibility=False)
        agent_group.add(name_metric)
        cid_metric = Metric(id="id", label="ID", value=self.agent.cid, visibility=False)
        agent_group.add(cid_metric)
        session_metric = Metric(id="session", label="Session", value=self.agent.session.cid, visibility=False)
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

            worker_stream_metric = Metric(id="stream", label="Stream", value=stream, type="text")
            worker_group.add(worker_stream_metric)

        return self.data.toDict()


###############
### AgentFactoryPerformanceTracker
#
class AgentFactoryPerformanceTracker(PerformanceTracker):
    """
    Tracks metadata and performance metrics for a specific agent factory, such as number of database connections.
    """

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
        num_created_connections_metric = Metric(
            id="num_created_connections", label="Num Total Connections", type="series", value=self.agent_factory.connection_factory.count_created_connections()
        )
        db_connections_group.add(num_created_connections_metric)
        num_in_use_connections_metric = Metric(
            id="num_in_use_connections", label="Num In Use Connections", type="series", value=self.agent_factory.connection_factory.count_in_use_connections()
        )
        db_connections_group.add(num_in_use_connections_metric)
        num_available_connections_metric = Metric(
            id="num_available_connections", label="Num Available Connections", type="series", value=self.agent_factory.connection_factory.count_available_connections()
        )
        db_connections_group.add(num_available_connections_metric)

        return self.data.toDict()


###############
### Worker
#
class Worker:
    """
    Represents a worker of an agent to process data on an input stream and output the results to an output stream.
    """

    def __init__(
        self, input_stream, input="DEFAULT", name="WORKER", id=None, sid=None, cid=None, prefix=None, suffix=None, agent=None, processor=None, session=None, properties=None, on_stop=None
    ):
        """Initialize the Worker.

        Parameters:
            input_stream: The input stream to read data from.
            input: The input parameter name. Defaults to "DEFAULT".
            name: The worker name. Defaults to "WORKER".
            id: The worker ID. If not provided, a new UUID will be created.
            sid: The worker short ID.
            cid: The worker canonical ID.
            prefix: The prefix for canonical ID.
            suffix: The suffix for canonical ID.
            agent: The agent to which the worker belongs.
            processor: The function to process incoming messages, inherited from Agent.
            session: The session to which the worker belongs.
            properties: Properties of the worker.
            on_stop: The function to call when the worker stops.
        """
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

        self.input = input

        self.session = session
        self.agent = agent

        if properties is None:
            properties = {}
        self._initialize(properties=properties)

        self.input_stream = input_stream

        self.processor = processor
        if processor is not None:
            self.processor = lambda *args, **kwargs: processor(*args, **kwargs, worker=self, properties=self.properties)

        self.producers = {}
        self.consumer = None
        self.on_stop = on_stop

        self._start()

    ###### initialization
    def _initialize(self, properties=None):
        """
        Initialize the worker.

        Parameters:
            properties: Properties of the worker.
        """
        self._initialize_properties()
        self._update_properties(properties=properties)

        self._initialize_logger()

    def _initialize_properties(self):
        """Initialize the properties of the worker with default properties."""
        self.properties = {}
        self.properties["num_threads"] = 1
        self.properties["db.host"] = "localhost"
        self.properties["db.port"] = 6379

    def _update_properties(self, properties=None):
        """
        Update the properties of the worker.

        Parameters:
            properties: Properties of the worker.
        """
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def _initialize_logger(self):
        """
        Initialize the logger for the worker, add session, agent, and worker information.
        """

        self.logger = log_utils.CustomLogger()
        # customize log
        self.logger.set_config_data(
            "stack",
            "%(call_stack)s",
        )
        agent_sid = "<NOT_SET>"
        if self.agent:
            agent_sid = self.agent.sid
        self.logger.set_config_data("agent", agent_sid, -1)
        self.logger.set_config_data("worker", self.sid, -1)
        session_sid = "<NOT_SET>"
        if self.session:
            session_sid = self.session.sid
        self.logger.set_config_data("session", session_sid, -1)

    def listener(self, message, input="DEFAULT"):
        """
        Listen for messages and process them through processor function, writes results to output, unrolling result lists if needed.

        Parameters:
            message: The message to process.
            input: The input parameter.
        """
        r = None
        if self.processor is not None:
            r = self.processor(message, input=input)

        if r is None:
            return

        results = []
        if type(r) == list:
            results = r
        else:
            results = [r]

        for result in results:
            out_param = "DEFAULT"

            if type(result) in [int, float, str, dict]:
                self.write_data(result, output=out_param)
            elif type(result) == Message:
                self.write(result, output=out_param)

            else:
                # error
                self.logger.error("Unknown return type from processor function: " + str(result))
                return

    # TODO: this seems out of place...
    def _update_form_ids(self, form_element: dict, stream_id: str, form_id: str):
        if "elements" in form_element:
            for element in form_element["elements"]:
                self._update_form_ids(element, stream_id, form_id)
        elif pydash.includes(["Control", "Button", 'Tabs'], form_element["type"]):
            if form_element["type"] == "Control":
                if pydash.objects.has(form_element, "options.detail.type"):
                    self._update_form_ids(
                        pydash.objects.get(form_element, "options.detail", {}),
                        stream_id,
                        form_id,
                    )
            pydash.objects.set_(form_element, "props.streamId", stream_id)
            pydash.objects.set_(form_element, "props.formId", form_id)

    def write_bos(self, output="DEFAULT", id=None, tags=None, scope="worker"):
        """
        Write a Beginning of Stream (BOS) message to stream.

        Parameters:
            output: The output parameter.
            id: Optional ID to append to output parameter for output stream.
            tags: Stream tags.
            scope: Scope of the stream, agent or worker (default: worker).
        """
        # producer = self._start_producer(output=output)
        # producer.write_bos()
        return self.write(Message.BOS, output=output, id=id, tags=tags, scope=scope)

    def write_eos(self, output="DEFAULT", id=None, tags=None, scope="worker"):
        """
        Write a End of Stream (EOS) message to stream.

        Parameters:
            output: The output parameter.
            id: Optional ID to append to output parameter for output stream.
            tags: Stream tags.
            scope: Scope of the stream, agent or worker (default: worker).
        """
        # producer = self._start_producer(output=output)
        # producer.write_eos()
        return self.write(Message.EOS, output=output, id=id, tags=tags, scope=scope)

    def write_data(self, data, output="DEFAULT", id=None, tags=None, scope="worker"):
        """
        Write data to stream, handling different data types and unrolling lists.

        Parameters:
            output: The output parameter.
            id: Optional ID to append to output parameter for output stream.
            tags: Stream tags.
            scope: Scope of the stream, agent or worker (default: worker).
        """
        # producer = self._start_producer(output=output)
        # producer.write_data(data)
        if type(data) == list:
            for d in data:
                s = self.write_data(d, output=output, id=id, tags=tags, scope=scope)
            return s
        else:
            if type(data) == int:
                contents = data
                content_type = ContentType.INT
            elif type(data) == float:
                contents = data
                content_type = ContentType.FLOAT
            elif type(data) == str:
                contents = data
                content_type = ContentType.STR
            elif type(data) == dict:
                contents = data
                content_type = ContentType.JSON
            else:
                print(data)
                raise Exception("Unknown data type: " + str(type(data)))

            return self.write(Message(MessageType.DATA, contents, content_type), output=output, id=id, tags=tags, scope=scope)

    def write_progress(self, progress_id=None, label=None, value=0):
        """Write a progress message to stream.

        Parameters:
            progress_id: The progress ID.
            label: The progress label.
            value: The progress value between 0 and 1.
        """
        progress = {'progress_id': progress_id, 'label': label, 'value': min(max(0, value), 1)}
        stream = self.write_control(code=ControlCode.PROGRESS, args=progress, output='PROGRESS')
        return stream

    def write_control(self, code, args, output="DEFAULT", id=None, tags=None, scope="worker"):
        """
        Write a control message to stream.

        Parameters:
            code: The control code.
            args: The control arguments.
            output: The output parameter.
            id: Optional ID to append to output parameter for output stream.
            tags: Stream tags.
            scope: Scope of the stream, agent or worker (default: worker).
        """
        # producer = self._start_producer(output=output)
        # producer.write_control(code, args)
        return self.write(Message(MessageType.CONTROL, {"code": code, "args": args}, ContentType.JSON), output=output, id=id, tags=tags, scope=scope)

    def write(self, message, output="DEFAULT", id=None, tags=None, scope="worker"):
        """
        Write a message to stream. Additionally handles special control messages for forms.

        Parameters:
            message: The message to write.
            output: The output parameter.
            id: Optional ID to append to output parameter for output stream.
            tags: Stream tags.
            scope: Scope of the stream, agent or worker (default: worker).
        """
        # set prefix, based on scope
        if scope == "agent":
            prefix = self.agent.cid
        else:
            prefix = self.prefix

        # TODO: This doesn't belong here..
        if message.getCode() in [
            ControlCode.CREATE_FORM,
            ControlCode.UPDATE_FORM,
            ControlCode.CLOSE_FORM,
        ]:
            if message.getCode() == ControlCode.CREATE_FORM:
                form_id = message.getArg('form_id')

                # create a new form id
                if id == None:
                    id = uuid_utils.create_uuid()

                if form_id is None:
                    form_id = id
                    message.setArg("form_id", id)

                # start stream
                event_producer = Producer(name="EVENT", id=form_id, prefix=prefix, suffix="STREAM", properties=self.properties, owner=self.agent.sid)
                event_producer.start()
                event_stream = event_producer.get_stream()

                self.agent.event_producers[form_id] = event_producer

                # inject stream and form id into ui
                self._update_form_ids(message.getArg("uischema"), event_stream, form_id)

                # start a consumer to listen to a event stream, using self.processor
                event_consumer = Consumer(
                    event_stream, name=self.name, prefix=self.cid, listener=lambda message: self.listener(message, input="EVENT"), properties=self.properties, owner=self.agent.sid
                )
                event_consumer.start()
            elif message.getCode() == ControlCode.UPDATE_FORM:
                form_id = message.getArg('form_id')

                if form_id is None:
                    raise Exception('missing form_id in UPDATE_FORM')

                event_producer = None
                if form_id in self.agent.event_producers:
                    event_producer = self.agent.event_producers[form_id]

                if event_producer is None:
                    raise Exception("no matching event producer for form")
                id = form_id

                event_stream = event_producer.get_stream()

                # inject stream and form id into ui
                self._update_form_ids(message.getArg("uischema"), event_stream, form_id)

            else:
                form_id = message.getArg('form_id')

                if form_id is None:
                    raise Exception('missing form_id in CLOSE_FORM')

                event_producer = None
                if form_id in self.agent.event_producers:
                    event_producer = self.agent.event_producers[form_id]

                if event_producer is None:
                    raise Exception("no matching event producer for form")
                id = form_id

        # append output variable with id, if not None
        if id is not None:
            output = output + ":" + id

        # create producer, if not existing
        producer = self._start_producer(output=output, tags=tags, prefix=prefix)
        producer.write(message)

        # close consumer, if end of stream
        if message.isEOS():
            # done, stop listening to input stream
            if self.consumer:
                self.consumer.stop()

        # return stream
        stream = producer.get_stream()
        return stream

    def _start(self):
        """Start the worker by initializing the consumer for the input stream."""
        # self.logger.info('Starting agent worker {name}'.format(name=self.sid))

        # start consumer only first on initial given input_stream
        self._start_consumer()
        self.logger.info("Started agent worker {name} for stream {stream}".format(name=self.sid, stream="none" if self.input_stream is None else self.input_stream))

    def _start_consumer(self):
        """
        Start the consumer for the input stream.
        """
        # start a consumer to listen to stream

        # if no input stream do not create consumer
        if self.input_stream is None:
            return

        consumer = Consumer(
            self.input_stream,
            name=self.name,
            prefix=self.cid,
            listener=lambda message: self.listener(message, input=self.input),
            properties=self.properties,
            owner=self.agent.sid,
            on_stop=lambda sid: self.on_consumer_stop_handler(sid),
        )

        self.consumer = consumer
        consumer.start()

    def on_consumer_stop_handler(self, consumer_sid):
        """Stop worker when consumer stops, reaching end of stream."""
        self._stop()

    def _start_producer(self, output="DEFAULT", tags=None, prefix=None):
        """
        Start a producer for the output stream. Notifies the session of the new stream if in a session.

        Parameters:
            output: The output parameter.
            tags: Stream tags.
            prefix: Prefix for the output stream. If None, uses worker's prefix.
        """
        if prefix is None:
            prefix = self.prefix

        # start, if not started
        pid = prefix + ":OUTPUT:" + output
        if pid in self.producers:
            return self.producers[pid]

        # create producer for output
        producer = Producer(name="OUTPUT", id=output, prefix=prefix, suffix="STREAM", properties=self.properties, owner=self.agent.sid)
        producer.start()
        self.producers[pid] = producer

        # notify session of new stream, if in a session
        if self.session:
            # get output stream info
            output_stream = producer.get_stream()

            # notify session, get tags for output param
            all_tags = set()
            # add agents name as a tag
            all_tags.add(self.agent.name)
            # add additional tags from write
            if tags:
                all_tags = all_tags.union(set(tags))
            # add tags for specific output variable
            output_name = output.split(":")[0]
            output_tags = self.agent.get_output_tags(output_name)
            if output_tags:
                all_tags = all_tags.union(set(output_tags))
            all_tags = list(all_tags)

            self.session.notify(self.agent, output_stream, all_tags)
        return producer

    ###### DATA RELATED
    ## session data
    def set_session_data(self, key, value):
        """Set session data for key to value.

        Parameters:
            key: The data key.
            value: The data value.
        """
        if self.session:
            self.session.set_data(key, value)

    def append_session_data(self, key, value):
        """Append value to session data for key.

        Parameters:
            key: The data key.
            value: The data value to append.
        """
        if self.session:
            self.session.append_data(key, value)

    def get_session_data(self, key):
        """Get session data for key.

        Parameters:
            key: The data key.

        Returns:
            The data value for the key, or None if not found.
        """
        if self.session:
            return self.session.get_data(key)

        return None

    def get_all_session_data(self):
        """Get all session data.

        Returns:
            A dictionary of all session data, or None if not found.
        """
        if self.session:
            return self.session.get_all_data()

        return None

    def get_session_data_len(self, key):
        """Get length of session data for key.

        Parameters:
            key: The data key.
        """
        if self.session:
            return self.session.get_data_len(key)

        return None

    ## session stream data
    def set_stream_data(self, key, value, stream=None):
        """Set stream data for key to value.

        Parameters:
            key: The data key.
            value: The data value.
            stream: The stream ID.
        """
        if self.session:
            self.session.set_stream_data(stream, key, value)

    def append_stream_data(self, key, value, stream=None):
        """Append value to stream data for key.

        Parameters:
            key: The data key.
            value: The data value to append.
            stream: The stream ID.
        """
        if self.session:
            self.session.append_stream_data(stream, key, value)

    def get_stream_data(self, key, stream=None):
        """Get stream data for key.

        Parameters:
            key: The data key.
            stream: The stream ID.

        Returns:
            The data value for the key in the specified stream, or None if not found.
        """
        if self.session:
            return self.session.get_stream_data(stream, key)

        return None

    def get_all_stream_data(self, stream=None):
        """Get all stream data.

        Parameters:
            stream: The stream ID.
        """
        if self.session:
            return self.session.get_all_stream_data(stream)

        return None

    def get_stream_data_len(self, key, stream=None):
        """Get length of stream data for key. if list.

        Parameters:
            key: The data key.
            stream: The stream ID.

        Returns:
            The length of the data value for the key in the specified stream, or None if not found.
        """
        if self.session:
            return self.session.get_stream_data_len(stream, key)

        return None

    ## agent data
    def set_data(self, key, value):
        """Set agent data for key to value.

        Parameters:
            key: The data key.
            value: The data value.
        """
        if self.session:
            self.session.set_agent_data(self.agent, key, value)

    def append_data(self, key, value):
        """Append value to agent data for key.

        Parameters:
            key: The data key.
            value: The data value to append.
        """
        if self.session:
            self.session.append_agent_data(self.agent, key, value)

    def get_data(self, key):
        """Get agent data for key.

        Parameters:
            key: The data key.

        Returns:
            The data value for the key, or None if not found.
        """
        if self.session:
            return self.session.get_agent_data(self.agent, key)
        return None

    def get_all_data(self):
        """Get all agent data.

        Returns:
            A dictionary of all agent data, or None if not found.
        """
        if self.session:
            return self.session.get_all_agent_data(self.agent)
        return None

    def get_data_len(self, key):
        """Get length of agent data for key.

        Parameters:
            key: The data key.

        Returns:
            The length of the data value for the key, or None if not found.
        """
        if self.session:
            return self.session.get_agent_data_len(self.agent, key)
        return None

    def stop(self):
        """Stop the agent worker, including its consumer."""
        # send stop signal to consumer(s)
        if self.consumer:
            self.consumer.stop()

    def _stop(self):
        """Internal stop function, called when consumer stops, calls on_stop callback if provided."""
        if self.on_stop:
            self.on_stop(self.sid)

    def wait(self):
        """Wait for the agent worker to finish, including its consumer."""
        # send wait to consumer(s)
        if self.consumer:
            self.consumer.wait()


###############
### Agent
#
class Agent:
    """Represents an agent that can process data from input streams and output results to output streams.
    
    Properties:
    ----------
    | Name           | Type                 | Default | Description |
    |----------------|--------------------|----------|---------|
    | `db.host`       | `str`                  | `"localhost"` | The database host.
    | `db.port`       | `int`                  | `6379`    | The database port.
    | `instructable`  | `bool`                 | `True`    | Whether the agent is instructable.
    | `tracker.perf.platform.agent.autostart` | `bool` | `False` | Whether to autostart the performance tracker for the agent.
    | `tracker.perf.platform.agent.outputs`   | `list` | `["log.INFO"]` | The outputs for the performance tracker.
    | `consumer.expiration` | `int`              | `3600`    | The expiration time for consumer streams in seconds. Default is 3600 (60 minutes).

     Inputs:
    - DEFAULT: The default input parameter.

    Outputs:
    - DEFAULT: The default output parameter.

    """

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
        properties=None,
    ):
        """Initialize the Agent.

        Parameters:
            name: The agent name. Defaults to "AGENT".
            id: The agent ID. If not provided, a new UUID will be created.
            sid: The agent short ID.
            cid: The agent canonical ID.
            prefix: The prefix for canonical ID.
            suffix: The suffix for canonical ID.
            session: The session to which the agent belongs.
            processor: The function to process incoming messages.
            properties: Properties of the agent.
        """
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

        # input and outputs of an agent
        self.inputs = {}
        self.outputs = {}

        if properties is None:
            properties = {}
        self._initialize(properties=properties)

        # override, if necessary
        if processor is not None:
            self.processor = lambda *args, **kwargs: processor(*args, **kwargs)
        else:
            self.processor = lambda *args, **kwargs: self.default_processor(*args, **kwargs)

        self.session = None

        # consumer for session stream
        self.session_consumer = None

        # workers of an agent in a session
        self.workers = {}

        # event producers, by form_id
        self.event_producers = {}

        self._start()

        # lastly, join session
        if session:
            self.join_session(session)

    ###### initialization
    def _initialize(self, properties=None):
        """
        Initialize the agent's properties, inputs, and outputs.
        """
        self._initialize_properties()

        self._initialize_inputs()
        self._initialize_outputs()

        self._update_properties(properties=properties)

        # updates inputs/outputs if set in properties
        self._update_inputs(properties=properties)
        self._update_outputs(properties=properties)

        self._initialize_logger()

    ####### properties
    def _initialize_properties(self):
        """Initialize the properties of the agent with default properties."""
        self.properties = {}

        # db connectivity
        self.properties["db.host"] = "localhost"
        self.properties["db.port"] = 6379

        # instructable
        self.properties["instructable"] = True

        # perf tracker
        self.properties["tracker.perf.platform.agent.autostart"] = False
        self.properties["tracker.perf.platform.agent.outputs"] = ["log.INFO"]

        # let consumer streams expire
        self.properties["consumer.expiration"] = 3600  # 60 minutes

    def _update_properties(self, properties=None):
        """
        Update the agent's properties.

        Parameters:
            properties: Properties of the agent.
        """
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    ####### inputs / outputs
    def _initialize_inputs(self):
        """Initialize the agent's input parameters with a default input."""
        self.add_input("DEFAULT")

    def _initialize_outputs(self):
        """Initialize the agent's output parameters with a default output."""
        self.add_output("DEFAULT")

    def _update_inputs(self, properties=None):
        """
        Update the agent's input parameters from its properties.

        Parameters:
            properties: Properties of the agent.
        """
        # update from agent properties
        if 'inputs' in properties:
            inputs = properties['inputs']
            for input in inputs:
                i = inputs[input]
                d = i['description'] if 'description' in i else None
                p = i['properties'] if 'properties' in i else None
                self.update_input(input, description=d, properties=p)

    def _update_outputs(self, properties=None):
        """
        Update the agent's output parmeters from its properties.

        Parameters:
            properties: Properties of the agent.
        """
        # update from agent properties
        if 'outputs' in properties:
            outputs = properties['outputs']
            for output in outputs:
                o = outputs[output]
                d = o['description'] if 'description' in o else None
                p = o['properties'] if 'properties' in o else None
                self.update_output(output, description=d, properties=p)

    def update_input(self, name, description=None, properties=None):
        """
        Add/Update an input parameter of the agent, processing properties for includes/excludes.

        Parameters:
            name: The name of the input parameter.
            description: The description of the input parameter.
            properties: Properties of the input parameter.
        """
        # if name not in self.inputs:
        #     return

        includes = []
        excludes = []

        if properties is None:
            properties = {}
        if 'listens' in properties:
            listens = properties['listens']
            if 'includes' in listens:
                includes = listens['includes']
            if 'excludes' in listens:
                excludes = listens['excludes']
        self.add_input(name, description=description, includes=includes, excludes=excludes)

    def update_output(self, name, description=None, properties=None):
        """
        Add/Update an output parameter of the agent, processing properties for tags.

        Parameters:
            name: The name of the output parameter.
            description: The description of the output parameter.
            properties: Properties of the output parameter.
        """
        # if name not in self.outputs:
        #     return

        tags = []
        if properties is None:
            properties = {}

        if 'tags' in properties:
            tags = properties['tags']

        self.add_output(name, description=description, tags=tags)

    def add_input(self, name, description=None, includes=None, excludes=None):
        """
        Add an input parameter to the agent.

        Parameters:
            name: The name of the input parameter
            description: The description of the input parameter.
            includes: List of include tags for the input parameter.
            excludes: List of exclude tags for the input parameter.
        """
        if description is None:
            description = ""
        if includes is None:
            includes = []
        if excludes is None:
            excludes = []

        self.inputs[name] = {"name": name, "description": description, "listens": {"includes": includes, "excludes": excludes}}

    def add_output(self, name, description=None, tags=None):
        """
        Add an output parameter to the agent.

        Parameters:
            name: The name of the output parameter
            description: The description of the output parameter.
            tags: List of tags for the output parameter.
        """
        if description is None:
            description = ""
        if tags is None:
            tags = []

        self.outputs[name] = {"name": name, "description": description, "tags": tags}

    def get_input(self, name):
        """
        Get an input parameter of the agent.

        Parameters:
            name: The name of the input parameter
        """
        if name in self.inputs:
            return self.inputs[name]
        return None

    def get_output(self, name):
        """
        Get an output parameter of the agent.

        Parameters:
            name: The name of the output parameter
        """
        if name in self.outputs:
            return self.outputs[name]
        return None

    def has_input(self, name):
        """
        Check if the agent has an input parameter with specified name.

        Parameters:
            name: The name of the input parameter

        Returns:
            True if the input parameter exists, False otherwise.
        """
        return name in self.inputs

    def has_output(self, name):
        """
        Check if the agent has an output parameter with specified name.

        Parameters:
            name: The name of the output parameter

        Returns:
            True if the output parameter exists, False otherwise.
        """
        return name in self.outputs

    def set_input_description(self, name, description=None):
        """
        Set the description of an input parameter.

        Parameters:
            name: The name of the input parameter
            description: The new description for the input parameter
        """
        if description is None:
            description = ""
        if name in self.inputs:
            self.inputs[name]['description'] = description

    def get_input_description(self, name):
        """
        Get the description of an input parameter.

        Parameters:
            name: The name of the input parameter

        Returns:
            The description of the input parameter, or None if not found.
        """
        if name in self.inputs:
            return self.inputs[name]['description']
        return None

    def set_output_description(self, name, description=None):
        """
        Set the description of an output parameter.

        Parameters:
            name: The name of the output parameter
            description: The new description for the output parameter
        """
        if description is None:
            description = ""
        if name in self.outputs:
            self.outputs[name]['description'] = description

    def get_output_description(self, name):
        """
        Get the description of an output parameter.

        Parameters:
            name: The name of the output parameter

        Returns:
            The description of the output parameter, or None if not found.
        """
        if name in self.outputs:
            return self.outputs[name]['description']
        return None

    def add_input_include(self, name, include=None):
        """
        Add an include pattern to an input parameter.

        Parameters:
            name: The name of the input parameter
            include: The include pattern to add
        """
        if include is None:
            return

        if name in self.inputs:
            self.inputs[name]['listens']['includes'].append(include)

    def remove_input_include(self, name, include=None):
        """
        Remove an include pattern from an input parameter.

        Parameters:
            name: The name of the input parameter
            include: The include pattern to remove
        """
        if include is None:
            return

        if name in self.inputs:
            self.inputs[name]['listens']['includes'].remove(include)

    def input_includes(self, name, include):
        """
        Check if an include pattern exists for an input parameter.

        Parameters:
            name: The name of the input parameter
            include: The include pattern to check

        Returns:
            True if the include pattern exists, False otherwise.
        """
        if name in self.inputs:
            return include in self.inputs[name]['listens']['includes']
        return None

    def get_input_includes(self, name):
        """
        Get the include patterns for an input parameter.

        Parameters:
            name: The name of the input parameter

        Returns:
            A list of include patterns for the input parameter, or None if not found.
        """
        if name in self.inputs:
            return self.inputs[name]['listens']['includes']

    def add_input_exclude(self, name, exclude=None):
        """
        Add an exclude pattern to an input parameter.

        Parameters:
            name: The name of the input parameter
            exclude: The exclude pattern to add
        """
        if exclude is None:
            return

        if name in self.inputs:
            self.inputs[name]['listens']['excludes'].append(exclude)

    def remove_input_exclude(self, name, exclude=None):
        """
        Remove an exclude pattern from an input parameter.

        Parameters:
            name: The name of the input parameter
            exclude: The exclude pattern to remove
        """
        if exclude is None:
            return

        if name in self.inputs:
            self.inputs[name]['listens']['excludes'].remove(exclude)

    def input_excludes(self, name, exclude):
        """
        Check if an exclude pattern exists for an input parameter.

        Parameters:
            name: The name of the input parameter
            exclude: The exclude pattern to check

        Returns:
            True if the exclude pattern exists, False otherwise.
        """
        if name in self.inputs:
            return exclude in self.inputs[name]['listens']['excludes']
        return None

    def get_input_excludes(self, name):
        """
        Get the exclude patterns for an input parameter.

        Parameters:
            name: The name of the input parameter

        Returns:
            A list of exclude patterns for the input parameter, or None if not found.
        """
        if name in self.inputs:
            return self.inputs[name]['listens']['excludes']

    def add_output_tag(self, name, tag=None):
        """
        Add a tag to an output parameter.

        Parameters:
            name: The name of the output parameter
            tag: The tag to add
        """
        if tag is None:
            return

        if name in self.outputs:
            self.outputs[name]['tags'].append(tag)

    def remove_output_tag(self, name, tag=None):
        """
        Remove a tag from an output parameter.

        Parameters:
            name: The name of the output parameter
            tag: The tag to remove
        """
        if tag is None:
            return

        if name in self.outputs:
            self.outputs[name]['tags'].remove(tag)

    def has_output_tag(self, name, tag):
        """
        Check if a tag exists for an output parameter.

        Parameters:
            name: The name of the output parameter
            tag: The tag to check

        Returns:
            True if the tag exists, False otherwise.
        """
        if name in self.outputs:
            return tag in self.outputs[name]['tags']
        return None

    def get_output_tags(self, name):
        """
        Get the tags for an output parameter.

        Parameters:
            name: The name of the output parameter

        Returns:
            A list of tags for the output parameter, or None if not found.
        """
        if name in self.outputs:
            return self.outputs[name]['tags']
        return None

    ####### logger
    def _initialize_logger(self):
        """Initialize the logger for the agent."""
        self.logger = log_utils.CustomLogger()
        # customize log
        self.logger.set_config_data(
            "stack",
            "%(call_stack)s",
        )
        self.logger.set_config_data("agent", self.sid, -1)
        session_sid = "<NOT_SET>"
        self.logger.set_config_data("session", session_sid, -1)

    ###### database, data
    def _start_connection(self):
        """Start the database connection for the agent."""
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()

    ###### worker
    # input_stream is data stream for input param, default 'DEFAULT'
    def create_worker(self, input_stream, input="DEFAULT", context=None, processor=None, properties=None):
        """
        Create a worker for the agent to process data from the specified input stream for input parameter

        Parameters:
            input_stream: The input stream for the worker
            input: The name of the input parameter
            context: The context for the worker (determines prefix for worker)
            processor: The processor function for the worker
            properties: The properties for the worker

        Returns:
            The created worker.
        """
        # check if listening already
        if input_stream and input_stream in self.workers:
            return self.workers[input_stream]

        # listen
        if processor == None:
            processor = lambda *args, **kwargs: self.processor(*args, **kwargs)

        # set prefix if context provided
        if context:
            prefix = context + ":" + self.sid
        else:
            # default agent's cid is prefix
            prefix = self.cid

        # override agent properties, if provided
        if properties is None:
            properties = {}

        worker_properties = {}
        worker_properties = json_utils.merge_json(worker_properties, self.properties)
        worker_properties = json_utils.merge_json(worker_properties, properties)

        worker = Worker(
            input_stream,
            input=input,
            name=self.name + "-WORKER",
            prefix=prefix,
            agent=self,
            processor=processor,
            session=self.session,
            properties=worker_properties,
            on_stop=lambda sid: self.on_worker_stop_handler(sid),
        )

        self.workers[input_stream] = worker

        return worker

    def on_worker_stop_handler(self, worker_input_stream):
        """Remove worker from workers list when it stops."""
        if worker_input_stream in self.workers:
            del self.workers[worker_input_stream]

    ###### default processor, override
    def default_processor(
        self,
        message,
        input=None,
        properties=None,
        worker=None,
    ):
        pass

    ###### default processor, do not override
    def _instruction_processor(
        self,
        message,
        input=None,
        properties=None,
        worker=None,
    ):
        """Default instruction processor, listens to instruction streams and creates new workers based on instructions, if instructable and matching agent name."""

        # self.logger.info("instruction processor")
        # self.logger.info(message)
        # self.logger.info(input)
        # self.logger.info(properties)
        # self.logger.info(worker)

        if message.getCode() == ControlCode.EXECUTE_AGENT:
            agent = message.getArg("agent")
            if agent == self.name:

                context = message.getAgentContext()

                # get additional properties
                properties = message.getAgentProperties()

                input_params = message.getInputParams()
                for input_param in input_params:
                    self.create_worker(input_params[input_param], input=input_param, context=context, properties=properties)

    ###### session
    def join_session(self, session):
        """
        Join a session.

        Parameters:
            session: The session to join
        """
        if type(session) == str:
            session = Session(cid=session, properties=self.properties)

        self.session = session

        # update logger
        self.logger.del_config_data("session")
        self.logger.set_config_data("session", self.session.sid, -1)

        if self.session:
            self.session.add_agent(self)
            self._start_session_consumer()

    def leave_session(self):
        """
        Leave the current session.
        """
        if self.session:
            self.session.remove_agent(self)

    def session_listener(self, message):
        """Listener for session messages. Handles new streams in session and checks if stream should be processed by the agent. Also, checks for instructions if instructable."""
        # listen to session stream
        if message.getCode() == ControlCode.ADD_STREAM:

            stream = message.getArg("stream")
            tags = message.getArg("tags")
            agent_cid = message.getArg("agent")

            # ignore streams from self
            if agent_cid == self.cid:
                return

            # find matching inputs
            matched_inputs = self._match_inputs_to_stream_tags(tags)

            # instructable
            # self.logger.info("instructable? " + str(self.properties['instructable']))
            if self.properties['instructable']:
                if 'INSTRUCTION' in set(tags):
                    # create a special worker to list to streams with instructions
                    instruction_worker = self.create_worker(stream, input="INSTRUCTION", processor=lambda *args, **kwargs: self._instruction_processor(*args, **kwargs))

            # skip
            if len(matched_inputs) == 0:
                # self.logger.info("Skipping stream {stream} with {tags}...".format(stream=stream, tags=tags))
                return

            for input in matched_inputs:
                tags = matched_inputs[input]

                # create worker
                worker = self.create_worker(stream, input=input, context=stream)

                # self.logger.info("Spawned worker for stream {stream}...".format(stream=stream))

        # session ended, stop agent
        elif message.isEOS():
            self.stop()

    def _match_inputs_to_stream_tags(self, tags):
        """
        Checks if streams tags match any of the agent's input parameters' include/exclude patterns.

        Parameters:
            tags: The tags from the stream

        Returns:
            A dictionary mapping input parameters to their matched tags.
        """
        matched_inputs = {}

        # check listeners for each input
        for input in self.inputs:
            matched_tags = set()

            includes = self.get_input_includes(input)
            excludes = self.get_input_excludes(input)

            for i in includes:
                p = None
                if type(i) == str:
                    p = re.compile(i)
                    for tag in tags:
                        if p.match(tag):
                            matched_tags.add(tag)
                            # self.logger.info("Matched include rule: {rule} for param: {param}".format(rule=str(i), param=param))
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
                        # self.logger.info("Matched include rule: {rule} for param: {param}".format(rule=str(i), param=param))

            # no matches for param
            if len(matched_tags) == 0:
                continue

            # found matched_tags for input
            matched_inputs[input] = list(matched_tags)

            for x in excludes:
                p = None
                if type(x) == str:
                    p = re.compile(x)
                    if p.match(tag):
                        # self.logger.info("Matched exclude rule: {rule} for param: {param}".format(rule=str(x), param=param))
                        # delete match
                        del matched_inputs[input]
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
                        # self.logger.info("Matched exclude rule: {rule} for param: {param}".format(rule=str(x), param=param))
                        # delete match
                        del matched_inputs[input]
                        break

        return matched_inputs

    # interact
    def interact(self, data, output="DEFAULT", unique=True, eos=True):
        """
        Interact with the session by sending data to the specified output. Used for interacting with the session directly.
        If unique is True, a unique identifier will be appended to the output name.
        If eos is True, an end-of-stream signal will be sent after the data.
        """
        if self.session is None:
            self.logger.error("No current session to interact with.")
            return

        # update output, if unique
        if unique:
            output = output + ":" + uuid_utils.create_uuid()

        # create worker to emit data for session
        worker = self.create_worker(None)

        # write data, automatically notify session on BOS
        worker.write_data(data, output=output)

        if eos:
            worker.write_eos(output=output)

    # plan
    def submit_plan(self, plan):
        """
        Submit a plan for execution.

        Parameters:
            plan: The AgenticPlan to submit.
        """
        if self.session is None:
            self.logger.error("No current session to submit.")
            return

        if not isinstance(plan, AgenticPlan):
            self.logger.error("Incorrect plan type")
            return

        # create worker to submit plan for session
        worker = self.create_worker(None)

        # write plan, automatically notify session on BOS
        plan.submit(worker)

    ## data
    def set_data(self, key, value):
        """Set agent data for key to value.

        Parameters:
            key: The data key.
            value: The data value.
        """
        self.session.set_agent_data(self, key, value)

    def get_data(self, key):
        """Get agent data for key.

        Parameters:
            key: The data key.

        Returns:
            The data value.
        """
        return self.session.get_agent_data(self, key)

    def append_data(self, key, value):
        """Append value to agent data for key.

        Parameters:
            key: The data key.
            value: The data value.
        """
        self.session.append_agent_data(self, key, value)

    def get_data_len(self, key):
        """Get length of agent data for key. if list.

        Parameters:
            key: The data key.
        """
        return self.session.get_agent_data_len(self, key)

    def perf_tracker_callback(self, data, tracker=None, properties=None):
        """
        Callback for performance tracker.
        """
        pass

    def _init_tracker(self):
        """Initialize the performance tracker for the agent."""
        self._tracker = AgentPerformanceTracker(self, properties=self.properties, callback=lambda *args, **kwargs: self.perf_tracker_callback(*args, **kwargs))

    def _start_tracker(self):
        """Start the performance tracker."""
        # start tracker
        self._tracker.start()

    def _stop_tracker(self):
        """Stop the performance tracker."""
        self._tracker.stop()

    def _terminate_tracker(self):
        """Terminate the performance tracker."""
        self._tracker.terminate()

    def _start(self):
        """Start the agent."""
        self._start_connection()

        # init tracker
        self._init_tracker()

        self.logger.info("Started agent {name}".format(name=self.name))
        self.logger.info("Agent properties:")
        self.logger.info(json.dumps(self.properties))
        self.logger.info("Inputs:")
        self.logger.info(json.dumps(self.inputs))
        self.logger.info("Outputs:")
        self.logger.info(json.dumps(self.outputs))

    def _start_session_consumer(self):
        """Start the session consumer."""
        # start a consumer to listen to session stream
        if self.session:
            session_stream = self.session.get_stream()

            if session_stream:
                self.session_consumer = Consumer(session_stream, name=self.name, listener=lambda message: self.session_listener(message), properties=self.properties, owner=self.sid)
                self.session_consumer.start()

    def stop(self):
        """Stop the agent, its session consumer, and all its workers."""
        # stop tracker
        self._stop_tracker()

        # leave session
        self.leave_session()
        if self.session_consumer is not None and isinstance(self.session_consumer, Consumer):
            self.session_consumer.stop()

        # send stop to each worker
        for worker_input_stream in self.workers:
            worker = self.workers[worker_input_stream]
            worker.stop()

        for worker_input_stream in list(self.workers.keys()):
            del self.workers[worker_input_stream]

    def wait(self):
        """Wait for the agent, its session consumer, and all its workers to finish."""
        # send wait to each worker
        for worker_input_stream in self.workers:
            worker = self.workers[worker_input_stream]
            worker.wait()


###############
### AgentFactory
#
class AgentFactory:
    """Factory to create agents of a specified class, listening to platform streams for instructions to join sessions."""

    def __init__(
        self,
        _class=Agent,
        _name="Agent",
        _registry="default",
        platform="default",
        properties={},
    ):
        """Initialize the AgentFactory.

        Parameters:
            _class: The class of agents to create. Defaults to Agent.
            _name: The base name of the agents to create. Defaults to "Agent".
            _registry: The registry where the agents are registered. Defaults to "default".
            platform: The platform where the agents operate. Defaults to "default".
            properties: Properties of the agent factory.
        """
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
        self.started = int(time.time())  # math.floor(time.time_ns() / 1000000)

        self._start()

    ###### initialization
    def _initialize(self, properties=None):
        """
        Initialize the agent factory.

        Parameters:
            properties: Properties of the agent factory.
        """
        self._initialize_properties()
        self._update_properties(properties=properties)

        self._initialize_logger()

    def _initialize_properties(self):
        """Initialize the properties of the agent factory with default properties."""
        self.properties = {}

        # db connectivity
        self.properties["db.host"] = "localhost"
        self.properties["db.port"] = 6379

        # perf tracker
        self.properties["tracker.perf.platform.agentfactory.autostart"] = True
        self.properties["tracker.perf.platform.agentfactory.outputs"] = ["pubsub"]

        # system perf tracker
        self.properties["tracker.perf.system.autostart"] = True
        self.properties["tracker.perf.system.outputs"] = ["pubsub"]

        # no consumer idle tracking
        self.properties['tracker.idle.consumer.autostart'] = False

    def _update_properties(self, properties=None):
        """
        Update the properties of the agent factory.

        Parameters:
            properties: Properties of the agent factory.
        """
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

        # override agent factory idle tracker expiration
        # to never expire, as platform streams that agent
        # factories listen to are long running streams
        self.properties['consumer.expiration'] = None

    def _initialize_logger(self):
        """Initialize the logger for the agent factory."""
        self.logger = log_utils.CustomLogger()
        # customize log
        self.logger.set_config_data(
            "stack",
            "%(call_stack)s",
        )
        self.logger.set_config_data("agent_factory", self.sid, -1)

    ###### database, data
    def _start_connection(self):
        """Start the database connection for the agent factory."""
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()

    ###### factory functions
    def create(self, **kwargs):
        """Create a new agent of the specified class with the given parameters.

        Parameters:
            kwargs: Parameters to pass to the agent constructor.

        Returns:
            The created agent instance.
        """
        print(kwargs)
        klasse = self._class
        instanz = klasse(**kwargs)
        return instanz

    def perf_tracker_callback(self, data, tracker=None, properties=None):
        """Callback for performance tracker."""
        pass

    def _init_tracker(self):
        """Initialize the performance tracker for the agent factory."""
        # agent factory perf tracker
        self._tracker = AgentFactoryPerformanceTracker(self, properties=self.properties, callback=lambda *args, **kwargs: self.perf_tracker_callback(*args, **kwargs))

        # system tracker
        global system_tracker
        system_tracker = SystemPerformanceTracker(properties=self.properties)

    def _start_tracker(self):
        """Start the performance tracker for the agent factory."""
        # start tracker
        self._tracker.start()

    def _stop_tracker(self):
        """Stop the performance tracker for the agent factory."""
        self._tracker.stop()

    def _terminate_tracker(self):
        """Terminate the performance tracker for the agent factory."""
        self._tracker.terminate()

    def _start(self):
        """Start the agent factory."""
        self._start_connection()

        # init tracker
        self._init_tracker()

        self._start_consumer()
        self.logger.info(
            "Started agent factory for agent: {name} in registry: {registry} on platform: {platform} ".format(
                name=self._name,
                registry=self._registry,
                platform=self.platform,
            )
        )

    def wait(self):
        """Wait for the agent factory and its platform consumer to finish."""
        self.platform_consumer.wait()

    def _start_consumer(self):
        """Start the platform consumer to listen for join session instructions."""
        # platform stream
        stream = "PLATFORM:" + self.platform + ":STREAM"
        self.platform_consumer = Consumer(stream, name=self._name + "_FACTORY", listener=lambda message: self.platform_listener(message), properties=self.properties, owner=self.sid)
        self.platform_consumer.start()

    def _extract_epoch(self, id):
        """Extract epoch time from message ID."""
        e = id.split("-")[0]
        return int(int(e) / 1000)

    def platform_listener(self, message):
        """Listener for platform messages. Handles join session instructions to create and join new agents to sessions."""
        # listen to platform stream

        # self.logger.info("Processing: " + str(message))
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
            ca = agent.split(Separator.AGENT)
            base_name = ca[0]

            if self._name == base_name:
                name = agent

                # check if already joined
                s = Session(cid=session, properties=self.properties)
                sas = s.list_agents()
                sesion_agent_names = [sa['name'] for sa in sas]
                if name in sesion_agent_names:
                    return

                # get properties
                agent_properties = message.getArg("properties")

                # start with agent factory properties, merge
                properties = {}
                properties = json_utils.merge_json(properties, self.properties)
                properties = json_utils.merge_json(properties, agent_properties)

                input = None

                if "input" in agent_properties:
                    input = agent_properties["input"]
                    del agent_properties["input"]

                self.logger.info("Launching Agent: " + name + "...")
                self.logger.info("Agent Properties: " + json.dumps(properties) + "...")

                prefix = session + ":" + "AGENT"
                a = self.create(
                    name=name,
                    prefix=prefix,
                    session=session,
                    properties=properties,
                )

                self.logger.info("Joined session: " + session)
                if input:
                    a.interact(input)
                    self.logger.info("Interact: " + input)
