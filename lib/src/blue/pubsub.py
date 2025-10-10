###### Parsers, Utils
import time
import logging
import time
import json

from copy import deepcopy

###### Backend, Databases
import redis
from redis.commands.json.path import Path

###### Threads
import threading

###### Blue
from blue.stream import Message, MessageType, ContentType, Stream
from blue.connection import PooledConnectionFactory
from blue.tracker import IdleTracker
from blue.utils import uuid_utils, log_utils


###############
### Consumer
#
class Consumer:
    """Consumer class to read messages from a Redis stream using consumer groups."""

    def __init__(self, stream, name="STREAM", id=None, sid=None, cid=None, prefix=None, suffix=None, owner=None, listener=None, properties=None, on_stop=None):
        """Initialize the Consumer.

        Parameters:
            stream: Stream identifier to consume from.
            name: Name of the consumer. Defaults to "STREAM".
            id (str): Unique identifier for the consumer. If None, a UUID will be generated.
            sid (str): Short identifier for the consumer. If None, it will be generated from name and id.
            cid (str): Canonical identifier for the consumer. If None, it will be generated from sid, prefix, and suffix.
            prefix (str): Optional prefix for the cid.
            suffix (str): Optional suffix for the cid.
            owner: Owner of the consumer for metadata
            listener: Callback function to process each message.
            properties: Properties for the consumer. Defaults to None.
            on_stop (callable): Callback function to be called when the consumer stops.
        """
        self.stream_cid = stream
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

        self.owner = owner

        if properties is None:
            properties = {}
        self._initialize(properties=properties)

        self.stream = Stream(self.stream_cid, properties=self.properties)

        if listener is None:
            listener = lambda message: print("{message}".format(message=message))

        self.listener = listener

        self.on_stop = on_stop
        self.threads = []

        # last processed
        self.last_processed = None

        # for pairing mode
        # self.pairer_task = None
        # self.left_param = None
        # self.left_queue = None
        # self.right_param = None
        # self.right_queue = None

    ###### initialization
    def _initialize(self, properties=None):
        """Initialize the consumer with properties.

        Parameters:
            properties: Properties to configure the consumer.
        """
        self._initialize_properties()
        self._update_properties(properties=properties)

        self._initialize_logger()

    def _initialize_properties(self):
        """Initialize default properties for the consumer."""
        self.properties = {}
        self.properties['num_threads'] = 1
        self.properties['db.host'] = 'localhost'
        self.properties['db.port'] = 6379

    def _update_properties(self, properties=None):
        """Update consumer properties with provided values.

        Parameters:
            properties: Dictionary of properties to update.
        """
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def _initialize_logger(self):
        """Initialize the logger for the consumer. Sets consumer and stream in log data."""
        self.logger = log_utils.CustomLogger()
        # customize log
        self.logger.set_config_data(
            "stack",
            "%(call_stack)s",
        )
        self.logger.set_config_data("consumer", self.sid, -1)
        self.logger.set_config_data("stream", self.stream_cid, -1)

    ####### open connection, create group, start threads
    def _extract_epoch(self, id):
        """Extract epoch time from Redis stream ID."""
        e = id.split("-")[0]
        return int(int(e) / 1000)

    def _idle_tracker_callback(self, data, tracker=None, properties=None):
        """Callback function for idle tracking. Expires the consumer if idle beyond `consumer.expiration` based on `last_active`"""
        if properties is None:
            properties = self.properties

        expiration = None
        if "consumer.expiration" in properties:
            expiration = properties['consumer.expiration']

        # expire?
        if expiration != None and expiration > 0:
            last_active = tracker.getValue('last_active')
            current = tracker.getValue('metadata.current')

            if last_active and current:
                if last_active + expiration < current:
                    self.logger.info("Expired Consumer: " + self.cid)
                    self._stop()

    def _init_tracker(self):
        """Initialize the idle tracker for the consumer."""
        self._tracker = IdleTracker(self, properties=self.properties, callback=lambda *args, **kwargs,: self._idle_tracker_callback(*args, **kwargs))
        self._tracker.start()

    def _start_tracker(self):
        """Start the idle tracker for the consumer."""
        # start tracker
        self._tracker.start()

    def _stop_tracker(self):
        """Stop the idle tracker for the consumer."""
        self._tracker.stop()

    def _terminate_tracker(self):
        """Terminate the idle tracker for the consumer."""
        self._tracker.terminate()

    def start(self):
        """Start the consumer: open connection, create group, and start threads."""
        # self.logger.info("Starting consumer {c} for stream {s}".format(c=self.sid,s=self.stream_cid))
        self.stop_signal = False

        self._start_connection()

        self._start_group()

        self._start_threads()

        # init tracker
        self._init_tracker()

        # self.logger.info("Started consumer {c} for stream {s}".format(c=self.sid, s=self.stream_cid))

    def stop(self):
        """Stop the consumer and terminate the idle tracker."""
        self._terminate_tracker()

        self.stop_signal = True

    def _stop(self):
        """Internal method to stop the consumer and call the on_stop callback."""
        self._terminate_tracker()

        self.stop_signal = True

        if self.on_stop:
            self.on_stop(self.sid)

    def wait(self):
        """Wait for all consumer threads to finish."""
        for t in self.threads:
            t.join()

    def _start_connection(self):
        """Start the connection to the Redis server."""
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()

    def _start_group(self):
        """Create the consumer group if it doesn't exist."""
        s = self.stream_cid
        g = self.cid
        r = self.connection

        try:
            # self.logger.info("Creating group {g}...".format(g=g))
            r.xgroup_create(name=s, groupname=g, id=0)
        except:
            self.logger.info("Group {g} exists...".format(g=g))

        # self._print_group_info()

    def _print_group_info(self):
        s = self.stream_cid
        g = self.cid
        r = self.connection

        self.logger.info("Group info for stream {s}".format(s=s))
        res = r.xinfo_groups(name=s)
        for i in res:
            self.logger.info(f"{s} -> group name: {i['name']} with {i['consumers']} consumers and {i['last-delivered-id']}" + f" as last read id")

    def get_stream(self):
        """Get the stream ID for the consumer."""
        return self.stream_cid

    def get_group(self):
        """Get the consumer group ID."""
        return self.cid

    # async def response_handler(self, message: Message):
    #     if self.pairer_task is not None:
    #         if message.isEOS():
    #             await asyncio.sleep(1)
    #             # wait until all items in the queue have been processed
    #             if self.left_queue is not None:
    #                 self.left_queue.join()
    #             if self.right_queue is not None:
    #                 self.right_queue.join()
    #             self.pairer_task.cancel()
    #         else:
    #             # pushing messages to pairing queue
    #             left_parameter = message.getParam(self.left_param)
    #             right_parameter = message.getParam(self.right_param)
    #             if left_parameter is not None:
    #                 await self.left_queue.put(left_parameter)
    #             if right_parameter is not None:
    #                 await self.right_queue.put(right_parameter)
    #     else:
    #         self.listener(message)

    # async def _consume_stream(self, c):
    def _consume_stream(self, c):
        """Consume messages from the Redis stream using consumer group. Construct a `Message` object for each message and pass it to the listener callback."""
        s = self.stream_cid
        g = self.cid
        r = self.connection

        # self.logger.info("[Thread {c}]: starting".format(c=c))
        while True:

            if self.stop_signal:
                break

            # check any pending, if so claim
            m = r.xautoclaim(count=1, name=s, groupname=g, consumername=str(c), min_idle_time=10000, justid=False)

            if len(m) > 0:
                d = m
                id = d[0]
                m_json = d[1]

                # check special token (no data to claim)
                if id == "0-0":
                    pass
                else:
                    # self.logger.info("[Thread {c}]: reclaiming... {s} {id}".format(c=c, s=s, id=id))

                    # listen
                    message = Message.fromJSON(json.dumps(m_json))
                    message.setID(id)
                    message.setStream(s)
                    # await self.response_handler(message)
                    self.listener(message)

                    # last processed
                    self.last_processed = int(time.time())  # self._extract_epoch(id)

                    # update stream metadata
                    if self.owner:
                        metadata = {'message': id, 'time': self.last_processed}
                        self.stream.set_metadata('consumers.' + self.owner, metadata)

                    # ack
                    r.xack(s, g, id)
                    continue

            # otherwise read new
            m = r.xreadgroup(count=1, streams={s: '>'}, block=200, groupname=g, consumername=str(c))

            if len(m) > 0:
                e = m[0]
                s = e[0]
                d = e[1][0]
                id = d[0]
                m_json = d[1]

                # self.logger.info("[Thread {c}]: listening... stream:{s} id:{id} message:{message}".format(c=c, s=s, id=id, message=m_json))

                # listen
                message = Message.fromJSON(json.dumps(m_json))
                message.setID(id)
                message.setStream(s)
                # await self.response_handler(message)
                self.listener(message)

                # last processed
                self.last_processed = int(time.time())  # self._extract_epoch(id)

                # update stream metadata
                if self.owner:
                    metadata = {'message': id, 'time': self.last_processed}
                    self.stream.set_metadata('consumers.' + self.owner, metadata)

                # occasionally throw exception (for testing failed threads)
                # if random.random() > 0.5:
                #    print("[Thread {c}]: throwing exception".format(c=c))
                #    raise Exception("exception")

                # ack
                r.xack(s, g, id)

                # on EOS, stop
                if message.isEOS():
                    self._stop()

        # self.logger.info("[Thread {c}]: finished".format(c=c))

    def _start_threads(self):
        """Start consumer threads to read from the stream."""
        # start threads
        num_threads = self.properties['num_threads']

        for i in range(num_threads):
            # t = threading.Thread(target=lambda: asyncio.run(self._consume_stream(self.cid + "-" + str(i))), daemon=True)
            t = threading.Thread(target=lambda: self._consume_stream(self.cid + "-" + str(i)), daemon=True)
            t.name = "Thread-" + self.__class__.__name__ + "-" + self.sid
            t.start()
            self.threads.append(t)

    def _delete_stream(self):
        """Delete all messages from the stream."""
        s = self.stream_cid
        r = self.connection

        l = r.xread(streams={s: 0})
        for _, m in l:
            [r.xdel(s, i[0]) for i in m]


###############
### Producer
#
class Producer:
    """Producer class to write messages to a Redis stream."""

    def __init__(
        self,
        name="STREAM",
        id=None,
        sid=None,
        cid=None,
        prefix=None,
        suffix=None,
        owner=None,
        properties=None,
    ):
        """Initialize the Producer.

        Parameters:
            name: Name of the producer. Defaults to "STREAM".
            id: Unique identifier for the producer. If None, a UUID will be generated.
            sid: Short identifier for the producer. If None, it will be generated from name and id.
            cid: Canonical identifier for the producer. If None, it will be generated from sid, prefix, and suffix.
            prefix: Optional prefix for the cid.
            suffix: Optional suffix for the cid.
            owner: Owner of the producer for metadata
            properties: Properties for the producer. Defaults to None.
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

        self.owner = owner

        if properties is None:
            properties = {}
        self._initialize(properties=properties)

        self.stream = Stream(self.cid, properties=self.properties)

    ###### INITIALIZATION
    def _initialize(self, properties=None):
        """Initialize the producer with properties.

        Parameters:
            properties: Properties to configure the producer.
        """
        self._initialize_properties()
        self._update_properties(properties=properties)

        self._initialize_logger()

    def _initialize_properties(self):
        """Initialize default properties for the producer."""
        self.properties = {}

        # db connectivity
        self.properties["db.host"] = "localhost"
        self.properties["db.port"] = 6379

    def _update_properties(self, properties=None):
        """Update producer properties with provided values.

        Parameters:
            properties: Dictionary of properties to update.
        """
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def _initialize_logger(self):
        """Initialize the logger for the producer. Sets producer and stream in log data."""
        self.logger = log_utils.CustomLogger()
        # customize log
        self.logger.set_config_data(
            "stack",
            "%(call_stack)s",
        )
        self.logger.set_config_data("producer", self.sid, -1)

    ####### open connection, create group, start threads
    def start(self):
        """Start the producer: open connection and initialize the stream."""
        # self.logger.info("Starting producer {p}".format(p=self.sid))
        self._start_connection()

        self._start_stream()
        # self.logger.info("Started producer {p}".format(p=self.sid))

    def _start_connection(self):
        """Start the connection to the Redis server."""
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()

    def _start_stream(self):
        """Initialize the stream by adding a BOS (beginning of stream) message if the stream is empty."""
        # start stream by adding BOS
        s = self.cid
        r = self.connection
        # check if stream has BOS in the front
        data = r.xread(streams={s: 0}, count=1)

        empty_stream = len(data) == 0

        if empty_stream:
            # add BOS (begin of stream)
            self.write_bos()

        self._print_stream_info()

    def _print_stream_info(self):
        s = self.cid
        r = self.connection

    def get_stream(self):
        """Get the stream ID for the producer."""
        return self.cid

    # stream
    def write_bos(self):
        """Write a beginning of stream (BOS) message to the stream."""
        self.write(Message.BOS)

    def write_eos(self):
        """Write an end of stream (EOS) message to the stream."""
        self.write(Message.EOS)

    def write_data(self, data):
        """Write a data message to the stream.

        Parameters:
            data: Data to be written to the stream. Can be int, float, str, or dict.
        """
        # default to string
        content_type = ContentType.STR
        if type(data) == int:
            content_type = ContentType.INT
        elif type(data) == float:
            content_type = ContentType.FLOAT
        elif type(data) == str:
            content_type = ContentType.STR
        elif type(data) == dict:
            content_type = ContentType.JSON
        self.write(Message(MessageType.DATA, data, content_type))

    def write_control(self, code, args):
        """Write a control message to the stream.

        Parameters:
            code: Control code for the message.
            args: Arguments for the control message.
        """
        self.write(Message(MessageType.CONTROL, {"code": code, "args": args}, ContentType.JSON))

    def write(self, message):
        """Write a message to the stream.

        Parameters:
            message: Message object to be written to the stream.
        """
        self._write_message_to_stream(json.loads(message.toJSON()))

    def _write_message_to_stream(self, json_message):
        """Internal method to write a JSON message to the Redis stream.

        Parameters:
            json_message: JSON representation of the message to be written.
        """
        # self.logger.info("json_message: " + json_message)
        id = self.connection.xadd(self.cid, json_message)
        # self.logger.info("Streamed into {s} message {m}".format(s=self.cid, m=str(json_message)))

        # update stream metadata
        if self.owner:
            metadata = {'message': id, 'time': int(time.time())}
            self.stream.set_metadata('producers.' + self.owner, metadata)

    def read_all(self):
        """Read all messages from the stream.
        Returns:
            (list[Message]): List of Message objects read from the stream.
        """
        sl = self.connection.xlen(self.cid)
        m = self.connection.xread(streams={self.cid: "0"}, count=sl, block=200)
        messages = []
        e = m[0]
        s = e[0]
        d = e[1]
        for di in d:
            id = di[0]
            m_json = di[1]

            message = Message.fromJSON(json.dumps(m_json))
            message.setID(id)
            message.setStream(s)

            messages.append(message)

        return messages
