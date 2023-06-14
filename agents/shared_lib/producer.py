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
    def __init__(self, name, sid=None, properties={}):

        self.name = name

        if sid is None:
            self.stream = self.name + ":" + str(uuid.uuid4())
        else:
            self.stream = str(sid)

        self.properties = properties

        self._initialize()

    ###### initialization
    def _initialize(self):
        self._initialize_properties()

    def _initialize_properties(self):
        if 'host' not in self.properties:
            self.properties['host'] = 'localhost'

        if 'port' not in self.properties:
            self.properties['port'] = 6379


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
        self.write(tag="BOS")
       
        self._print_stream_info()

    def _print_stream_info(self):
        s = self.stream
        r = self.connection

    def get_stream(self):
        return self.stream

    # stream 
    def write(self, data=None, type="str", tag="DATA", eos=True, split=" "):
        # print("producer write {tag} {data} {type}".format(tag=tag,data=data,type=type))

        if tag == "DATA":
            # force str conversion
            if type is None:
                type = "str"
                data = str(data)

            if type == "str":
                if split is None:
                    tokens = [data]
                else:
                    tokens = data.split(split)

                    for token in tokens:
                        message = self._prepare_message(value=token, tag=tag, type="str")
                        self._write_message_to_stream(message)
                    
                    
            elif type == "int":
                message = self._prepare_message(value=data, tag=tag, type="int")
                self._write_message_to_stream(message)

            if eos:
                message = self._prepare_message(tag="EOS")
                self._write_message_to_stream(message)
        else:
            message = self._prepare_message(value=data, tag=tag)
            self._write_message_to_stream(message)

             
    def _prepare_message(self, tag=None, value=None, type=None):
        if tag == "DATA":
            return {"tag": tag, "value": value, "type": type}
        else:
            if value is None:
                return {"tag": tag}
            else:
                return {"tag": tag, "value": value}

    def _write_message_to_stream(self, message):
        # logging.info("Streaming into {s} message {m}".format(s=self.stream, m=str(message)))
        self.connection.xadd(self.stream, message)
        logging.info("Streamed into {s} message {m}".format(s=self.stream, m=str(message)))


#######################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, default='USER')
    parser.add_argument('--text', type=str, default='hello world!')
    args = parser.parse_args()

    p = Producer(args.name)
    p.start()

    p.stream(args.text, type="str")



