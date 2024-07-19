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

###### Blue
from message import Message, MessageType, ContentType, ControlCode, MessageEncoder, MessageDecoder

# set log level
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [%(process)d:%(threadName)s:%(thread)d](%(filename)s:%(lineno)d) %(name)s -  %(message)s",
    level=logging.ERROR,
    datefmt="%Y-%m-%d %H:%M:%S",
)


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
        logging.info("Started producer {p}".format(p=self.sid))

    def _start_connection(self):
        host = self.properties["db.host"]
        port = self.properties["db.port"]

        logging.info("PRODUCER START....." + host)
        self.connection = redis.Redis(host=host, port=port, decode_responses=True)

    def _start_stream(self):
        # start stream by adding BOS
        s = self.cid
        r = self.connection
        # check if stream has BOS in the front
        data = r.xread(streams={s: 0}, count=1)
        empty_stream = data == None
        # has_bos = pydash.is_equal(
        #     pydash.objects.get(data, "0.1.0.1.label", None), "BOS"
        # )
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
            contents = json.dumps(data)
            content_type = ContentType.JSON
        self.write(Message(MessageType.DATA, contents, content_type))

    def write_control(self, code, args):
        self.write(Message(MessageType.CONTROL, {"code": code, args: args}, ContentType.JSON))

    def write(self, message):
        self._write_message_to_stream(message.toJSON())

    def _write_message_to_stream(self, json_message):
        self.connection.xadd(self.cid, json_message)
        logging.info("Streamed into {s} message {m}".format(s=self.sid, m=str(json_message)))

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

             
            message = json.loads(m_json, cls=MessageDecoder)
            message.setID(id)
            message.setStream(s)
            
            
            messages.append(message)

        return messages


#######################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str, default="USER")
    parser.add_argument("--text", type=str, default="hello world!")
    parser.add_argument("--loglevel", default="INFO", type=str)

    args = parser.parse_args()

    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())

    p = Producer(args.name)
    p.start()

    p.write(args.text, dtype="str")
