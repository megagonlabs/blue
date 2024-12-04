###### OS / Systems
from curses import noecho
import os
import sys


######
import time
import argparse
import logging
import time
import uuid
import random
import math

###### Parsers, Formats, Utils
import re
import csv
import json
from utils import json_utils


import itertools
from tqdm import tqdm

###### Backend, Databases
import redis


###### Blue
from worker import Worker
from consumer import Consumer
from message import Message, MessageType, ContentType, ControlCode
from connection import PooledConnectionFactory

def create_uuid():
    return str(hex(uuid.uuid4().fields[0]))[2:]

class Operator():
    def __init__(
        self,
        name="OPERATOR",
        id=None,
        sid=None,
        cid=None,
        prefix=None,
        suffix=None,
        pipeline=None,
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

        self._initialize(properties=properties)

        # override, if necessary
        if processor is not None:
            self.processor = lambda *args, **kwargs: processor(*args, **kwargs, properties=self.properties)
        else:
            self.processor = lambda *args, **kwargs: self.default_processor(*args, **kwargs, properties=self.properties)

        # pipeline
        self.pipeline = pipeline

        # consumer for instruction pipeline stream
        self.pipeline_consumer = None

        # workers of operator 
        self.workers = []

        self._start()

    ###### initialization
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        self.properties = {}

        # db connectivity
        self.properties["db.host"] = "localhost"
        self.properties["db.port"] = 6379

        # instructable
        self.properties["instructable"] = True
        

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    ###### database, data
    def _start_connection(self):
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()

    ###### worker
    # input_stream is data stream for operator
    def create_worker(self, input_stream, context=None, processor=None):
        # listen 
        logging.info(
            "Creating worker for stream {stream} ...".format(stream=input_stream)
        )

        if processor == None:
            processor = lambda *args, **kwargs: self.processor(*args, **kwargs)

        # set prefix if context provided
        if context:
            p = context + ":" + self.sid
        else:
            # default operator's cid is prefix
            p = self.cid

        worker = Worker(
            input_stream,
            prefix=p,
            processor=processor,
            properties=self.properties,
        )

        self.workers.append(worker)

        return worker

    ###### default processor, override
    def default_processor(
        self,
        data, #JSON
        properties=None,
    ):
        logging.info("default_processor: override")
        logging.info(data)
        logging.info(properties)

    ###### instruction pipeline listener, do not override
    def pipeline_listener(self, message):
        if message.getCode() == ControlCode.EXECUTE_OPERATOR:
            operator = message.getArg("operator")
            if operator == self.name:
                context = message.getArg("context")
                input_stream = message.getArg("input")
                self.create_worker(input_stream, context=context)


    def _start(self):
        self._start_connection()

        # if operator is associated with a pipeline
        if self.pipeline:
            self._start_pipeline_consumer()

        logging.info("Started operator {name}".format(name=self.name))

    def _start_pipeline_consumer(self):
        # start a consumer to listen to instruction pipeline
        if self.pipeline:
            self.pipeline_consumer = Consumer(
                self.pipeline,
                name=self.name,
                listener=lambda message: self.pipeline_listener(message),
                properties=self.properties,
            )
            self.pipeline_consumer.start()

    def stop(self):

        # send stop to each worker
        for w in self.workers:
            w.stop()

    def wait(self):
        # send wait to each worker
        for w in self.workers:
            w.wait()
        
    


class OperatorFactory():
    def __init__(
        self,
        _class=Operator,
        _name="Operator",
        _registry="default",
        platform="default",
        properties={},
    ):
        self._class = _class
        self._name = _name
        self._registry = _registry

        self.platform = platform

        self._initialize(properties=properties)

        self.platform = None

        # creation time
        self.ct = math.floor(time.time_ns() / 1000000)

        self._start()

    ###### initialization
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

    ###### database, data
    def _start_connection(self):
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()
        
    ###### factory functions
    def create(self, **kwargs):
        print(kwargs)
        klasse = self._class
        instanz = klasse(**kwargs)
        return instanz

    def _start(self):
        self._start_connection()

        self._start_consumer()
        logging.info(
            "Started operator factory for operator: {name} in registry: {registry} on platform: {platform} ".format(
                name=self._name,
                registry=self._registry,
                platform=self.platform,
            )
        )

    def wait(self):
        self.platform_consumer.wait()

    def _start_consumer(self):
        # platform stream
        stream = "PLATFORM:" + self.platform + ":STREAM"
        self.platform_consumer = Consumer(
            stream,
            name=self._name + "_FACTORY",
            listener=lambda message: self.platform_listener(message),
            properties=self.properties,
        )
        self.platform_consumer.start()

    def platform_listener(self, message):
        # listen to platform stream

        logging.info("Processing: " + str(message))
        id = message.getID()

        # only process newer instructions
        mt = int(id.split("-")[0])

        # ignore past instructions
        if mt < self.ct:
            return

        # check if join pipeline
        if message.getCode() == ControlCode.JOIN_PIPELINE:
            pipeline = message.getArg("pipeline")
            registry = message.getArg("registry")
            operator = message.getArg("operator")
            

            # start with factory properties
            properties_from_pipeline = message.getArg("properties")
            properties_from_factory = self.properties
            operator_properties = {}
            operator_properties = json_utils.merge_json(operator_properties, properties_from_factory)
            operator_properties = json_utils.merge_json(operator_properties, properties_from_pipeline)

            if self._name == operator:
                name = operator

                logging.info("Launching Operator: " + name + "...")
                logging.info("Operator Properties: " + json.dumps(operator_properties) + "...")

                prefix = pipeline + ":" + "OPERATOR"
                a = self.create(
                    name=name,
                    prefix=prefix,
                    pipeline=pipeline,
                    properties=operator_properties,
                )

                logging.info("Joined pipeline: " + pipeline)


#######################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str, default="OPERATOR")
    parser.add_argument("--properties", type=str)
    parser.add_argument("--loglevel", default="INFO", type=str)
    parser.add_argument("--serve", type=str, default="OPERATOR")
    parser.add_argument("--platform", type=str, default="default")
    parser.add_argument("--registry", type=str, default="default")

    args = parser.parse_args()

    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())

    # set properties
    properties = {}
    p = args.properties

    if p:
        # decode json
        properties = json.loads(p)

    if args.serve:
        platform = args.platform

        of = OperatorFactory(
            _class=Operator,
            _name=args.serve,
            _registry=args.registry,
            platform=platform,
            properties=properties,
        )
        of.wait()

