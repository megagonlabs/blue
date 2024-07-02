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
from agent import Session


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
        agent=None,
        processor=None,
        session=None,
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

        self.session = session
        self.agent = agent

        self._initialize(properties=properties)

        self.input_streams = set()
        self.input_streams.add(input_stream)

        self.processor = processor
        if processor is not None:
            self.processor = lambda *args, **kwargs,: processor(*args, **kwargs, worker=self)

        self.properties = properties

        self.producer = None

        self.consumers = {}

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

    def listener(self, id, message, stream):
        label = None
        data = None
        dtype = None

        if "label" in message:
            label = message["label"]
        if "data" in message:
            data = message["data"]
        if "type" in message:
            dtype = message["type"]

        result = None

        if dtype == "json":
            data = json.loads(data)

        if self.processor is not None:
            result = self.processor(stream, id, label, data, dtype=dtype)

        # logging.info(result)
        # if result, write to stream
        if result is not None:
            result_label = None
            result_data = None
            result_dtype = None
            result_eos = None

            # processor can return multiple values, and the order is mapped to the following:
            # DATA
            # DATA, DTYPE
            # LABEL, DATA, DTYPE
            # LABEL, DATA, DTYPE, EOS
            # where
            # LABEL is BOS, EOS, DATA, INSTRUCTION, ...
            # DTYPE is int, float, str, json, ...
            # EOS is True, False

            if type(result) == tuple:
                if len(result) == 2:
                    result_label = "DATA"
                    result_data = result[0]
                    result_dtype = result[1]
                elif len(result) == 3:
                    result_label = result[0]
                    result_data = result[1]
                    result_dtype = result[2]
                elif len(result) == 4:
                    result_label = result[0]
                    result_data = result[1]
                    result_dtype = result[2]
                    result_eos = result[3]
            else:
                result_label = "DATA"
                result_data = result
                result_dtype = None
                result_eos = False

            # result is interactive, create event message stream to track interactions
            if result_label == "INTERACTION":
                # start INTERACTION output stream early
                form_id = str(hex(uuid.uuid4().fields[0]))[2:]

                self._start_producer()
                event_stream = Producer(
                    name="EVENT_MESSAGE",
                    id=form_id,
                    prefix=self.producer.get_stream(),
                    properties=self.properties,
                )
                event_stream.start()

                # inject stream and form id into ui
                result_data["form_id"] = form_id
                interactive_result_type = pydash.objects.get(result_data, "type", None)
                if pydash.is_equal(interactive_result_type, "JSONFORM"):
                    self._stream_injection(result_data["content"], event_stream.get_stream(), form_id)

                # start a consumer to listen to a event stream, using self.processor
                event_consumer = Consumer(
                    event_stream.get_stream(),
                    name=self.name,
                    prefix=self.cid,
                    listener=lambda id, data: self.listener(id, data, event_stream.get_stream()),
                    properties=self.properties,
                )
                event_consumer.start()

            if self.properties["aggregator"]:
                if self.properties["aggregator.eos"] == "FIRST":
                    self.write(
                        result_data,
                        dtype=result_dtype,
                        label=result_label,
                        eos=(label == "EOS"),
                    )
                elif self.properties["aggregator.eos"] == "NEVER":
                    self.write(result_data, dtype=result_dtype, label=result_label, eos=False)
                else:
                    self.write(result_data, dtype=result_dtype, label=result_label, eos=False)
            else:
                # TODO Implement 'ALL' option
                self.write(result_data, dtype=result_dtype, label=result_label, eos=result_eos)

        if label == "EOS":
            # done, stop listening to input stream
            consumer = self.consumers[stream]
            consumer.stop()

    def _stream_injection(self, form_element: dict, stream: str, form_id: str):
        if "uischema" in form_element:
            self._stream_injection(form_element["uischema"], stream, form_id)
        else:
            if "elements" in form_element:
                for element in form_element["elements"]:
                    self._stream_injection(element, stream, form_id)
            elif pydash.includes(["Control", "Button"], form_element["type"]):
                if form_element["type"] is "Control":
                    if pydash.objects.has(form_element, 'options.detail.type'):
                        self._stream_injection(pydash.objects.get(form_element, 'options.detail', {}), stream, form_id)
                pydash.objects.set_(form_element, "props.streamId", stream)
                pydash.objects.set_(form_element, "props.formId", form_id)

    def write(self, data, dtype=None, label="DATA", eos=True, split=None):
        # start producer on first write
        self._start_producer()

        self.producer.write(data=data, dtype=dtype, label=label, eos=eos, split=split)

    def _start(self):
        # logging.info('Starting agent worker {name}'.format(name=self.sid))

        # start consumer only first on initial given input_stream
        self._start_consumers()
        logging.info("Started agent worker {name}".format(name=self.sid))

    def _start_consumers(self):
        for input_stream in self.input_streams:
            self._start_consumer_on_stream(input_stream)

    def _start_consumer_on_stream(self, input_stream):
        # start a consumer to listen to stream
        if input_stream:
            # create data namespace to share data on stream
            # if self.session:
            #     self.session._init_stream_agent_data_namespace(input_stream, self.agent)

            consumer = Consumer(
                input_stream,
                name=self.name,
                prefix=self.cid,
                listener=lambda id, data: self.listener(id, data, input_stream),
                properties=self.properties,
            )

            self.consumers[input_stream] = consumer
            consumer.start()

    def _start_producer(self):
        # start, if not started
        if self.producer == None:

            producer = Producer(prefix=self.prefix, properties=self.properties)
            producer.start()
            self.producer = producer

            # notify session of new stream, if in a session
            if self.session:
                # get output stream info
                output_stream = self.producer.get_stream()

                # notify session
                tags = set()
                tags.add(self.agent.name)
                if "tags" in self.properties:
                    tags = tags.union(set(self.properties["tags"]))
                tags = list(tags)

                self.session.notify(output_stream, tags)

    ###### DATA RELATED
    ## session data
    def set_session_data(self, key, value):
        if self.session:
            self.session.set_data(key, value)

    def append_session_data(self, key, value):
        if self.session:
            self.session.append_data(key, value)

    def get_session_data(self, key):
        if self.session:
            return self.session.get_data(key)

        return None

    def get_session_data_len(self, key):
        if self.session:
            return self.session.get_data_len(key)

        return None

    ## session stream data
    def _identify_stream(self, stream=None):
        if stream:
            return stream
        else:
            if len(self.input_streams) == 1:
                return list(self.input_streams)[0]
            else:
                return "UNIDENTIFIED"

    def set_stream_data(self, key, value, stream=None):
        if self.session:
            stream = self._identify_stream(stream=stream)
            self.session.set_stream_data(stream, key, value)

    def append_stream_data(self, key, value, stream=None):
        if self.session:
            stream = self._identify_stream(stream=stream)
            self.session.append_stream_data(stream, key, value)

    def get_stream_data(self, key, stream=None):
        if self.session:
            stream = self._identify_stream(stream=stream)
            return self.session.get_stream_data(stream, key)

        return None

    def get_stream_data_len(self, key, stream=None):
        if self.session:
            stream = self._identify_stream(stream=stream)
            return self.session.get_stream_data_len(stream, key)

        return None

    ## worker data
    # def set_data(self, key, value, stream=None):
    #     if self.session:
    #         stream = self._identify_stream(stream=stream)
    #         self.session.set_stream_agent_data(stream, self.agent, key, value)

    # def append_data(self, key, value, stream=None):
    #     if self.session:
    #         stream = self._identify_stream(stream=stream)
    #         self.session.append_stream_agent_data(stream, self.agent, key, value)

    # def get_data(self, key, stream=None):
    #     if self.session:
    #         stream = self._identify_stream(stream=stream)
    #         return self.session.get_stream_agent_data(stream, self.agent, key)

    #     return None

    # def get_data_len(self, key, stream=None):
    #     if self.session:
    #         stream = self._identify_stream(stream=stream)
    #         return self.session.get_stream_agent_data_len(stream, self.agent, key)

    #     return None

    ## agent data
    def set_data(self, key, value):
        if self.session:
            self.session.set_agent_data(self.agent, key, value)

    def append_data(self, key, value):
        if self.session:
            self.session.append_agent_data(self.agent, key, value)

    def get_data(self, key):
        if self.session:
            return self.session.get_agent_data(self.agent, key)
        return None

    def get_data_len(self, key):
        if self.session:
            return self.session.get_agent_data_len(self.agent, key)
        return None

    def stop(self):
        # send stop signal to consumer(s)
        for consumer in self.consumers.values():
            consumer.stop()

    def wait(self):
        # send wait to consumer(s)
        for consumer in self.consumers.values():
            consumer.wait()


#######################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str, default="processor")
    parser.add_argument("--input_stream", type=str, default="input")
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--loglevel", default="INFO", type=str)

    args = parser.parse_args()

    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())

    stream_data = []

    # sample func to process data
    def processor(id, label, data, dtype=None):

        if label == "EOS":
            # print all data received from stream
            print(stream_data)

            # compute stream data
            l = len(stream_data)
            time.sleep(4)

            # output to stream
            return l

        elif label == "DATA":
            # store data value
            stream_data.append(data)

        return None

    # create a worker
    w = Worker(args.name, args.input_stream, processor=processor)
    w.start()
