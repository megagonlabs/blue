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
from blue.stream import Message, MessageType, ContentType
from blue.connection import PooledConnectionFactory
from blue.tracker import IdleTracker
from blue.utils import uuid_utils

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")


###############
### Consumer
#
class Consumer:
    def __init__(self, stream, name="STREAM", id=None, sid=None, cid=None, prefix=None, suffix=None, listener=None, properties={}, on_stop=None):

        self.stream = stream

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

        self._initialize(properties=properties)

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
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        self.properties = {}
        self.properties['num_threads'] = 1
        self.properties['db.host'] = 'localhost'
        self.properties['db.port'] = 6379

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]



    ####### open connection, create group, start threads
    def _extract_epoch(self, id):
        e = id.split("-")[0]
        return int(int(e) / 1000)

    def _idle_tracker_callback(self, data, tracker=None, properties=None):
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
                    logging.info("Expired Consumer: " + self.cid)
                    self._stop() 

    def _init_tracker(self):
        self._tracker = IdleTracker(self, properties=self.properties, callback=lambda *args, **kwargs,: self._idle_tracker_callback(*args, **kwargs))
        self._tracker.start()

    def _start_tracker(self):
        # start tracker
        self._tracker.start()

    def _stop_tracker(self):
        self._tracker.stop()

    def _terminate_tracker(self):
        self._tracker.terminate()

    def start(self):

        # logging.info("Starting consumer {c} for stream {s}".format(c=self.sid,s=self.stream))
        self.stop_signal = False

        self._start_connection()

        self._start_group()

        self._start_threads()

        # init tracker
        self._init_tracker()

        # logging.info("Started consumer {c} for stream {s}".format(c=self.sid, s=self.stream))

    def stop(self):
        self._terminate_tracker()

        self.stop_signal = True 

    def _stop(self):
        self._terminate_tracker()

        self.stop_signal = True 

        if self.on_stop:
            self.on_stop(self.sid)

    def wait(self):
        for t in self.threads:
            t.join()

    def _start_connection(self):
       
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()


    def _start_group(self):
        # create group if it doesn't exists, print group info
        s = self.stream
        g = self.cid
        r = self.connection

        try:
            # logging.info("Creating group {g}...".format(g=g))
            r.xgroup_create(name=s, groupname=g, id=0)
        except:
            logging.info("Group {g} exists...".format(g=g))

        # self._print_group_info()

    def _print_group_info(self):
        s = self.stream
        g = self.cid
        r = self.connection

        logging.info("Group info for stream {s}".format(s=s))
        res = r.xinfo_groups(name=s)
        for i in res:
            logging.info(f"{s} -> group name: {i['name']} with {i['consumers']} consumers and {i['last-delivered-id']}" + f" as last read id")

    def get_stream(self):
        return self.stream

    def get_group(self):
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
        s = self.stream
        g = self.cid
        r = self.connection

        # logging.info("[Thread {c}]: starting".format(c=c))
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
                    # logging.info("[Thread {c}]: reclaiming... {s} {id}".format(c=c, s=s, id=id))

                    # listen
                    message = Message.fromJSON(json.dumps(m_json))
                    message.setID(id)
                    message.setStream(s)
                    # await self.response_handler(message)
                    self.listener(message)
                    # last processed
                    self.last_processed =  int(time.time()) # self._extract_epoch(id)

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

                # logging.info("[Thread {c}]: listening... stream:{s} id:{id} message:{message}".format(c=c, s=s, id=id, message=m_json))

                # listen
                message = Message.fromJSON(json.dumps(m_json))
                message.setID(id)
                message.setStream(s)
                # await self.response_handler(message)
                self.listener(message)
                # last processed
                self.last_processed = int(time.time())  # self._extract_epoch(id)

                # occasionally throw exception (for testing failed threads)
                # if random.random() > 0.5:
                #    print("[Thread {c}]: throwing exception".format(c=c))
                #    raise Exception("exception")

                # ack
                r.xack(s, g, id)

                # on EOS, stop
                if message.isEOS():
                    self._stop()

        # logging.info("[Thread {c}]: finished".format(c=c))

    def _start_threads(self):
        # start threads
        num_threads = self.properties['num_threads']

        for i in range(num_threads):
            # t = threading.Thread(target=lambda: asyncio.run(self._consume_stream(self.cid + "-" + str(i))), daemon=True)
            t = threading.Thread(target=lambda: self._consume_stream(self.cid + "-" + str(i)), daemon=True)
            t.name = "Thread-" + self.__class__.__name__ + "-" + self.sid
            t.start()
            self.threads.append(t)

    def _delete_stream(self):
        s = self.stream
        r = self.connection

        l = r.xread(streams={s: 0})
        for _, m in l:
            [r.xdel(s, i[0]) for i in m]



###############
### Producer
#
class Producer:
    def __init__(
        self,
        name="STREAM",
        id=None,
        sid=None,
        cid=None,
        prefix=None,
        suffix=None,
        properties={},
    ):

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

        self._initialize(properties=properties)

    ###### INITIALIZATION
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

    ####### open connection, create group, start threads
    def start(self):
        # logging.info("Starting producer {p}".format(p=self.sid))
        self._start_connection()

        self._start_stream()
        # logging.info("Started producer {p}".format(p=self.sid))

    def _start_connection(self):
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()


    def _start_stream(self):
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
        return self.cid

    # stream
    def write_bos(self):
        self.write(Message.BOS)

    def write_eos(self):
        self.write(Message.EOS)

    def write_data(self, data):
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
        self.write(Message(MessageType.CONTROL, {"code": code, "args": args}, ContentType.JSON))

    def write(self, message):
        self._write_message_to_stream(json.loads(message.toJSON()))

    def _write_message_to_stream(self, json_message):
        # logging.info("json_message: " + json_message)
        self.connection.xadd(self.cid, json_message)
        # logging.info("Streamed into {s} message {m}".format(s=self.cid, m=str(json_message)))

    def read_all(self):
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
