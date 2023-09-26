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
from tqdm import tqdm

###### Backend, Databases
import redis

###### Threads
import threading
import concurrent.futures

# set log level
logging.getLogger().setLevel(logging.INFO)

class Producer():
    def __init__(self, name, suffix=None, sid=None, properties={}):

        self.name = name

        self._initialize(properties=properties)

        if sid is None:
            self.stream = self.name + ":" + str(hex(uuid.uuid4().fields[0]))[2:]
        else:
            self.stream = str(sid)

        if suffix:
            self.stream += "-" + str(suffix)

        self._initialize()

    ###### initialization
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        self.properties = {}
        self.properties['host'] = 'localhost'
        self.properties['port'] = 6379

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    ####### open connection, create group, start threads
    def start(self):
        # logging.info("Starting producer {p}".format(p=self.name))
        self._start_connection()

        self._start_stream()
        logging.info("Started producer {p}".format(p=self.name))


    def _start_connection(self):
        host = self.properties['host']
        port = self.properties['port']

        self.connection = redis.Redis(host=host, port=port, decode_responses=True)

    def _start_stream(self):
        # start strea by adding BOS 
        s = self.stream
        r = self.connection

        # add BOS (begin of stream)
        self.write(label="BOS")
       
        self._print_stream_info()

    def _print_stream_info(self):
        s = self.stream
        r = self.connection

    def get_stream(self):
        return self.stream

    # stream 
    def write(self, data=None, dtype="str", label="DATA", eos=False, split=None):
        # logging.info("producer write {label} {data} {dtype} {eos}".format(label=label,data=data,dtype=dtype,eos=eos))

        # do basic type casting, if none given
        # print("type {type}".format(type=type))
        if dtype == None:
            if isinstance(data, int):
                dtype = 'int'
            elif isinstance(data, float):
                dtype = 'float'
            elif isinstance(data, str):
                dtype = 'str'
            elif isinstance(data, dict) or isinstance(data, list):
                dtype = 'json'
            else:
                # convert everything else to string
                data = str(data)
                dtype = 'str'


        if dtype == 'json':
            data = json.dumps(data)

        if label == "DATA":

            if dtype == "str":
                # TODO: Overrride?
                if split is None:
                    split = " "

            if split is None:
                tokens = [data]
            else:
                tokens = data.split(split)

            for token in tokens:
                message = self._prepare_message(data=token, label=label, dtype=dtype)
                self._write_message_to_stream(message)
                
            # logging.info(eos)
            if eos:
                message = self._prepare_message(label="EOS")
                self._write_message_to_stream(message)

        elif label == "INSTRUCTION":
            message = self._prepare_message(data=data, label=label, dtype=dtype)
            self._write_message_to_stream(message)
        else:
            message = self._prepare_message(data=data, label=label, dtype=dtype)
            self._write_message_to_stream(message)

             
    def _prepare_message(self, label=None, data=None, dtype=None):
        if data is None:
            return {"label": label}
        else:
            return {"label": label, "data": data, "type": dtype}

    def _write_message_to_stream(self, message):
        # logging.info("Streaming into {s} message {m}".format(s=self.stream, m=str(message)))
        self.connection.xadd(self.stream, message)
        logging.info("Streamed into {s} message {m}".format(s=self.stream, m=str(message)))


#######################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, default='USER')
    parser.add_argument('--text', type=str, default='hello world!')
    parser.add_argument('--loglevel', default="INFO", type=str)
 
    args = parser.parse_args()
   
    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())


    p = Producer(args.name)
    p.start()

    p.write(args.text, dtype="str")



