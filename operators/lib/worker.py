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
import pydash

import itertools
from tqdm import tqdm

###### Blue
from producer import Producer
from consumer import Consumer
from message import Message, MessageType, ContentType, ControlCode


class Worker:
    def __init__(
        self,
        input_stream,
        name="WORKER",
        id=None,
        sid=None,
        cid=None,
        prefix=None,
        suffix=None,
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

        self.input = input

        self._initialize(properties=properties)

        self.input_stream = input_stream
        self.processor = processor
        if processor is not None:
            self.processor = lambda *args, **kwargs,: processor(*args, **kwargs, worker=self)

        self.properties = properties

        self.producer = None
        self.consumer = None

        self._start()

    ###### initialization
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        self.properties = {}
        self.properties["num_threads"] = 1
        self.properties["db.host"] = "localhost"
        self.properties["db.port"] = 6379

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def listener(self, message, input="DEFAULT"):
        
        r = None
        if self.processor is not None:
            # only data messages
            if message.isData(): 
                d = message.getData()           
                r = self.processor(d)

        if r is None:
            return
        
        results = []
        if type(r) == list:
            results = r
        else:
            results = [r]


        for result in results:
            if type(result) in [int, float, str, dict]:
                self.write_data(result)
            else:
                # error
                logging.error("Unknown return type from processor function: " + str(result))
                return

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
            contents = data
            content_type = ContentType.JSON

        self.write(Message(MessageType.DATA, contents, content_type))

    def write(self, message, output="DEFAULT", tags=None):
        # create producer, if not existing
        producer = self._start_producer()
        producer.write(message)

        # close consumer, if end of stream
        if message.isEOS():
            # done, stop listening to input stream
            if self.consumer:
                self.consumer.stop()

    def _start(self):
        # start consumer only first on initial given input_stream
        self._start_consumer()
        logging.info("Started operator worker {name}".format(name=self.sid))

    def _start_consumer(self):
        # start a consumer to listen to stream
        if self.input_stream is None:
            return
        
        consumer = Consumer(
            self.input_stream,
            name=self.name,
            prefix=self.cid,
            listener=lambda message: self.listener(message, input=self.input),
            properties=self.properties,
        )

        self.consumer = consumer
        consumer.start()

    def _start_producer(self):
        # create producer for output
        producer = Producer(name="OUT", prefix=self.prefix, suffix="STREAM", properties=self.properties)
        producer.start()
        self.producer = producer

        return producer


    def stop(self):
        # send stop signal to consumer(s)
        if self.consumer:
            self.consumer.stop()

    def wait(self):
        # send wait to consumer(s)
        if self.consumer:
            self.consumer.wait()

