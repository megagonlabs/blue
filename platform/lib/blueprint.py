###### OS / Systems
import os
import sys

###### Add lib path
sys.path.append('./lib/')
sys.path.append('./lib/utils/')

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
from redis.commands.json.path import Path

###### Blue
from session import Session

class Platform():
    def __init__(self, name=None, properties={}):

        if name is None:
            name = "default"
        self.name = name

        self._initialize(properties=properties)

        self._start()


    ###### INITIALIZATION
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)


    def _initialize_properties(self):
        self.properties = {}

        if 'host' not in self.properties:
            self.properties['host'] = 'localhost'

        if 'port' not in self.properties:
            self.properties['port'] = 6379

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    ###### SESSION
    def get_sessions(self):
        session_keys = self.connection.keys(pattern='*SESSION:*:DATA')
        return [ { "id": ai[:-5], "name": ai[:-5], "description": "" } for ai in session_keys]

    def get_session(self, session_id):
        session_keys = self.connection.keys(pattern='*SESSION:*')
        if session_id in set(session_keys):
            return { "id": session_id, "name": session_id, "description": "" }
        else:
            return None

    def create_session(self):
        session = Session()
        session_id = session.name
        return { "id": session_id, "name": session_id, "description": "" }

    def delete_session(self, session_id):
        # delete session stream
        self.connection.delete(session_id)
        # delete session data
        self.connection.delete(session_id + ":DATA")
        # TODO: delete more


    ###### OPERATIONS
    def _start(self):
        # logging.info('Starting session {name}'.format(name=self.name))
        self._start_connection()

        logging.info('Started platform {name}'.format(name=self.name))

    def _start_connection(self):
        host = self.properties['host']
        port = self.properties['port']

        self.connection = redis.Redis(host=host, port=port, decode_responses=True)

    def stop(self):
        #TODO
        pass




#######################
### EXAMPLE
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--loglevel', default="INFO", type=str)
 
    args = parser.parse_args()
   
    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())

    # create platform
    platform = Platform()

    # list sessions
    sessions = platform.get_sessions()
    