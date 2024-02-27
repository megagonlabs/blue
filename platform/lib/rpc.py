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

###### Communication, Threading
import rpyc
from rpyc.utils.server import ThreadedServer
    
import inspect
from threading import Thread


# set log level
logging.getLogger().setLevel(logging.INFO)

class RPCServer(rpyc.Service):
    def __init__(self, name, properties={}):
        self.name = name
        ALIASES = [self.name]

        self._initialize(properties=properties)
        
    ###### initialization
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)


    def _initialize_properties(self):
        self.properties = {}

        # db connectivity
        self.properties['rpc.port'] = 18861

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    def on_connect(self, connection):
        client_info = connection._config['endpoints'][1]
        client_host = client_info[0]
        client_port = client_info[1]
        logging.info("Connected: " + client_host + ":" + str(client_port))

    def on_disconnect(self, connection):
        client_info = connection._config['endpoints'][1]
        client_host = client_info[0]
        client_port = client_info[1]
        logging.info("Disconnected: " + client_host + ":" + str(client_port))

    def register(self, f):
        fstr = getattr(f, "__name__", str(f))
        exposed_f = lambda *args, **kwargs: f(*args[1:], **kwargs)
        setattr(RPCServer, 'exposed_' + fstr, exposed_f)

    def run(self):
        port = self.properties['rpc.port']
        logging.info("Starting RPC Server on port: " + str(port))
        t = ThreadedServer(self, port=port)
        t.start()


class RPCClient:
    def __init__(self, name, properties={}):
        self.name = name

        self._initialize(properties=properties)

    ###### initialization
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)


    def _initialize_properties(self):
        self.properties = {}

        self.properties['rpc.host'] = 'localhost'
        self.properties['rpc.port'] = 18861

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            print(p)
            self.properties[p] = properties[p]

    def executor(self):
        return self.connection.root

    def connect(self):
        try:
            logging.info("Connecting to " + self.properties['rpc.host'] + ":" + str(self.properties['rpc.port']) + "...")
            self.connection = rpyc.connect(self.properties['rpc.host'], self.properties['rpc.port'])
            logging.info("Connected.")
        except EOFError as e:
            logging.info(e)
            raise Exception('Client was not able to connect.')
    


