###### OS / Systems
import os
import sys

######
import time
import argparse
import logging
import time
import uuid
import random
import asyncio
from asyncio import Queue

###### Parsers, Formats, Utils
import re
import csv
import json

import itertools
import pydash
from tqdm import tqdm

###### Backend, Databases
import redis

###### Threads
import threading
import concurrent.futures

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s", level=logging.ERROR, datefmt="%Y-%m-%d %H:%M:%S")

###### Blue
from message import Message, MessageType, ContentType, ControlCode


class Consumer:
    def __init__(self, stream, name="STREAM", id=None, sid=None, cid=None, prefix=None, suffix=None, listener=None, properties={}):

        self.stream = stream

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

        if listener is None:
            listener = lambda message: print("{message}".format(message=message))

        self.listener = listener

        self.threads = []

        # for pairing mode
        self.pairer_task = None
        self.left_param = None
        self.left_queue = None
        self.right_param = None
        self.right_queue = None

    ###### initialization
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)
        # properties {
        #     output {
        #         type: 'pair',
        #         left: <param>,
        #         right: <param>
        #     }
        # }
        output_type = pydash.objects.get(properties, 'output.type', None)
        if pydash.is_equal(output_type, 'pair'):
            self.pairer_task = asyncio.get_event_loop().create_task(self.pairer(self.left_queue, self.right_queue))
            self.left_param = properties["output"].get('left')
            self.left_queue = Queue()
            self.right_param = properties["output"].get('right')
            self.right_queue = Queue()

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

    # non-blocking, run until cancelled
    async def pairer(self, left_queue: Queue, right_queue: Queue):
        while True:
            # item {value, type}
            left_item: Message = await left_queue.get()
            right_item: Message = await right_queue.get()
            # always use right_item ID
            message = Message.fromJSON(
                {
                    'label': 'DATA',
                    'contents': {'args': {'params': {self.left_param: left_item, self.right_param: right_item}}},
                    'content_type': 'JSON',
                }
            )
            self.listener(message)
            left_queue.task_done()
            right_queue.task_done()

    ####### open connection, create group, start threads
    def start(self):

        # logging.info("Starting consumer {c} for stream {s}".format(c=self.sid,s=self.stream))
        self.stop_signal = False

        self._start_connection()

        self._start_group()

        self._start_threads()

        logging.info("Started consumer {c} for stream {s}".format(c=self.sid, s=self.stream))

    def stop(self):
        logging.info("Stopping consumer {c} for stream {s}".format(c=self.sid, s=self.stream))
        self.stop_signal = True

    def wait(self):
        for t in self.threads:
            t.join()

    def _start_connection(self):
        host = self.properties['db.host']
        port = self.properties['db.port']

        self.connection = redis.Redis(host=host, port=port, decode_responses=True)

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

    async def response_handler(self, message: Message):
        if self.pairer_task is not None:
            if message.isEOS():
                await asyncio.sleep(1)
                # wait until all items in the queue have been processed
                if self.left_queue is not None:
                    self.left_queue.join()
                if self.right_queue is not None:
                    self.right_queue.join()
                self.pairer_task.cancel()
            else:
                # pushing messages to pairing queue
                left_parameter = message.getParam(self.left_param)
                right_parameter = message.getParam(self.right_param)
                if left_parameter is not None:
                    await self.left_queue.put(left_parameter)
                if right_parameter is not None:
                    await self.right_queue.put(right_parameter)
        else:
            self.listener(message)

    async def _consume_stream(self, c) -> asyncio.coroutine:
        s = self.stream
        g = self.cid
        r = self.connection

        logging.info("[Thread {c}]: starting".format(c=c))
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
                    logging.info("[Thread {c}]: reclaiming... {s} {id}".format(c=c, s=s, id=id))

                    # listen
                    message = Message.fromJSON(json.dumps(m_json))
                    message.setID(id)
                    message.setStream(s)
                    await self.response_handler(message)
                    #

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

                logging.info("[Thread {c}]: listening... stream:{s} id:{id} message:{message}".format(c=c, s=s, id=id, message=m_json))

                # listen
                message = Message.fromJSON(json.dumps(m_json))
                message.setID(id)
                message.setStream(s)
                await self.response_handler(message)

                # occasionally throw exception (for testing failed threads)
                # if random.random() > 0.5:
                #    print("[Thread {c}]: throwing exception".format(c=c))
                #    raise Exception("exception")

                # ack
                r.xack(s, g, id)

        logging.info("[Thread {c}]: finished".format(c=c))

    def _start_threads(self):
        # start threads
        num_threads = self.properties['num_threads']

        for i in range(num_threads):
            t = threading.Thread(target=lambda: asyncio.run(self._consume_stream(self.cid + "-" + str(i))), daemon=True)
            t.start()
            self.threads.append(t)

    def _delete_stream(self):
        s = self.stream
        r = self.connection

        l = r.xread(streams={s: 0})
        for _, m in l:
            [r.xdel(s, i[0]) for i in m]


#######################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, default='consumer')
    parser.add_argument('--stream', type=str, default='stream')
    parser.add_argument('--threads', type=int, default=1)
    parser.add_argument('--loglevel', default="INFO", type=str)

    args = parser.parse_args()

    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())

    # create a listener
    def listener(id, message):
        print("hello {message}".format(message=message))

    c = Consumer(args.stream, name=args.name, listener=listener)
    c.start()
