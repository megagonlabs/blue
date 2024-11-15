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
from message import Message, MessageType, ContentType, ControlCode


class Worker:
    def __init__(
        self,
        input_stream,
        input="DEFAULT",
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

        self.input = input

        self.session = session
        self.agent = agent

        self._initialize(properties=properties)

        self.input_stream = input_stream
        self.processor = processor
        if processor is not None:
            self.processor = lambda *args, **kwargs,: processor(*args, **kwargs, worker=self)

        self.properties = properties

        self.producers = {}
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
                logging.error("Unknown return type from processor function: " + str(result))
                return

    # TODO: this seems out of place...
    def _update_form_ids(self, form_element: dict, stream_id: str, form_id: str):
        if "elements" in form_element:
            for element in form_element["elements"]:
                self._update_form_ids(element, stream_id, form_id)
        elif pydash.includes(["Control", "Button"], form_element["type"]):
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
        # producer = self._start_producer(output=output)
        # producer.write_bos()
        return self.write(Message.BOS, output=output, id=id, tags=tags, scope=scope)

    def write_eos(self, output="DEFAULT", id=None, tags=None, scope="worker"):
        # producer = self._start_producer(output=output)
        # producer.write_eos()
        return self.write(Message.EOS, output=output, id=id, tags=tags, scope=scope)

    def write_data(self, data, output="DEFAULT", id=None, tags=None, scope="worker"):
        # producer = self._start_producer(output=output)
        # producer.write_data(data)
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
            raise Exception("Unknown data type: " + str(type(data)))

        return self.write(Message(MessageType.DATA, contents, content_type), output=output, id=id, tags=tags, scope=scope)

    def write_progress(self, progress_id=None, label=None, value=0):
        progress = {'progress_id': progress_id, 'label': label, 'value': min(max(0, value), 1)}
        stream = self.write_control(code=ControlCode.PROGRESS, args=progress, output='PROGRESS')
        return stream

    def write_control(self, code, args, output="DEFAULT", id=None, tags=None, scope="worker"):
        # producer = self._start_producer(output=output)
        # producer.write_control(code, args)
        return self.write(Message(MessageType.CONTROL, {"code": code, "args": args}, ContentType.JSON), output=output, id=id, tags=tags, scope=scope)

    def write(self, message, output="DEFAULT", id=None, tags=None, scope="worker"):

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
                    id = str(hex(uuid.uuid4().fields[0]))[2:]

                if form_id is None:
                    form_id = id
                    message.setArg("form_id", id)

                # start stream
                event_producer = Producer(
                    name="EVENT",
                    id=form_id,
                    prefix=prefix,
                    suffix="STREAM",
                    properties=self.properties,
                )
                event_producer.start()
                event_stream = event_producer.get_stream()

                # inject stream and form id into ui
                self._update_form_ids(message.getArg("uischema"), event_stream, form_id)

                # start a consumer to listen to a event stream, using self.processor
                event_consumer = Consumer(
                    event_stream,
                    name=self.name,
                    prefix=self.cid,
                    listener=lambda message: self.listener(message, input="EVENT"),
                    properties=self.properties,
                )
                event_consumer.start()

            else:
                form_id = message.getArg('form_id')

                if form_id is None:
                    raise Exception('missing form_id in UPDATE_FORM')

                # inject stream and form id into ui
                # self._update_form_ids(message.getArg("uischema"), event_stream, form_id)                    

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
        # logging.info('Starting agent worker {name}'.format(name=self.sid))

        # start consumer only first on initial given input_stream
        self._start_consumer()
        logging.info("Started agent worker {name}".format(name=self.sid))

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

    def _start_producer(self, output="DEFAULT", tags=None, prefix=None):
        if prefix is None:
            prefix = self.prefix

        # start, if not started
        pid = prefix + ":OUTPUT:" + output
        if pid in self.producers:
            return self.producers[pid]

        # create producer for output
        producer = Producer(
            name="OUTPUT",
            id=output,
            prefix=prefix,
            suffix="STREAM",
            properties=self.properties,
        )
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
            # add tags from properties
            if "tags" in self.properties:
                tags_by_param = self.properties["tags"]
                # include tags from properties by output param
                for param in tags_by_param:
                    output_name = output.split(":")[0]
                    # add params specific to outp
                    if output_name == param:
                        param_tags = tags_by_param[param]
                        all_tags = all_tags.union(set(param_tags))
            all_tags = list(all_tags)

            self.session.notify(self.agent, output_stream, all_tags)
        return producer

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

    def get_all_session_data(self):
        if self.session:
            return self.session.get_all_data()

        return None

    def get_session_data_len(self, key):
        if self.session:
            return self.session.get_data_len(key)

        return None

    ## session stream data
    def set_stream_data(self, key, value, stream=None):
        if self.session:
            self.session.set_stream_data(stream, key, value)

    def append_stream_data(self, key, value, stream=None):
        if self.session:
            self.session.append_stream_data(stream, key, value)

    def get_stream_data(self, key, stream=None):
        if self.session:
            return self.session.get_stream_data(stream, key)

        return None

    def get_all_stream_data(self, stream=None):
        if self.session:
            return self.session.get_all_stream_data(stream)

        return None

    def get_stream_data_len(self, key, stream=None):
        if self.session:
            return self.session.get_stream_data_len(stream, key)

        return None

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

    def get_all_data(self):
        if self.session:
            return self.session.get_all_agent_data(self.agent)
        return None

    def get_data_len(self, key):
        if self.session:
            return self.session.get_agent_data_len(self.agent, key)
        return None

    def stop(self):
        # send stop signal to consumer(s)
        if self.consumer:
            self.consumer.stop()

    def wait(self):
        # send wait to consumer(s)
        if self.consumer:
            self.consumer.wait()
