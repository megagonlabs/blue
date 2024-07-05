###### OS / Systems
import os
import sys

import pydash

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/utils/")

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
from producer import Producer
from session import Session


class Platform:
    def __init__(self, name="PLATFORM", id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):

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

        # platform stream
        self.producer = None

        self._start()

    ###### INITIALIZATION
    def _initialize(self, properties=None):
        self._initialize_properties()
        self._update_properties(properties=properties)

    def _initialize_properties(self):
        self.properties = {}

        # db connectivity
        self.properties['db.host'] = 'localhost'
        self.properties['db.port'] = 6379

    def _update_properties(self, properties=None):
        if properties is None:
            return

        # override
        for p in properties:
            self.properties[p] = properties[p]

    ###### SESSION
    def get_session_sids(self):
        keys = self.connection.keys(pattern=self.cid + ":SESSION:*:DATA")
        keys = "\n".join(keys)
        result = []

        # further apply re to match
        regex = r"SESSION:[^:]*:DATA"

        matches = re.finditer(regex, keys)
        session_sids = [match.group()[:-5] for match in matches]
        return session_sids

    def get_sessions(self):
        session_sids = self.get_session_sids()

        result = []
        for session_sid in session_sids:
            session = self.get_session(session_sid)
            metadata = session.get_metadata()
            result.append(
                {
                    "id": session_sid,
                    "name": pydash.objects.get(metadata, "name", session_sid),
                    "description": pydash.objects.get(metadata, "description", ""),
                    "created_date": pydash.objects.get(metadata, "created_date", None),
                }
            )
        return result

    def get_session(self, session_sid):
        session_sids = self.get_session_sids()

        if session_sid in set(session_sids):
            return Session(sid=session_sid, prefix=self.cid, properties=self.properties)
        else:
            return None

    def create_session(self):
        session = Session(prefix=self.cid, properties=self.properties)
        created_date = session.get_metadata('created_date')
        return {"id": session.sid, "name": session.sid, "description": "", 'created_date': created_date}

    def delete_session(self, session_sid):
        session_cid = self.cid + ":" + session_sid

        # delete session stream
        self.connection.delete(session_cid + ":STREAM")

        # delete session data, metadata
        self.connection.delete(session_cid + ":DATA")
        self.connection.delete(session_cid + ":METADATA")

        # TODO: delete more

        # TOOO: remove, stop all agents

    def _send_message(self, code, params):
        message = {'code': code, 'params': params}
        self.producer.write(data=message, dtype="json", label="INSTRUCTION")

    def join_session(self, session_sid, registry, agent, properties):

        session_cid = self.cid + ":" + session_sid
        code = "JOIN_SESSION"
        params = {'session': session_cid, 'registry': registry, 'agent': agent, 'properties': properties}

        self._send_message(code, params)

    ###### METADATA RELATED
    def __get_json_value(self, value):
        if value is None:
            return None
        if type(value) is list:
            if len(value) == 0:
                return None
            else:
                return value[0]
        else:
            return value

    def _init_metadata_namespace(self):
        # create namespaces for any session common data, and stream-specific data
        self.connection.json().set(
            self._get_metadata_namespace(),
            "$",
            {},
            nx=True,
        )

    def _get_metadata_namespace(self):
        return self.cid + ":METADATA"

    def set_metadata(self, key, value):
        self.connection.json().set(self._get_metadata_namespace(), "$." + key, value)

    def get_metadata(self, key=""):
        value = self.connection.json().get(
            self._get_metadata_namespace(),
            Path("$" + ("" if pydash.is_empty(key) else ".") + key),
        )
        return self.__get_json_value(value)

    ###### OPERATIONS
    def _start_producer(self):
        # start, if not started
        if self.producer == None:
            producer = Producer(sid="STREAM", prefix=self.cid, properties=self.properties)
            producer.start()
            self.producer = producer

    def _start(self):
        # logging.info('Starting session {name}'.format(name=self.sid))
        self._start_connection()

        # initialize platform metadata
        self._init_metadata_namespace()

        # start platform communication stream
        self._start_producer()

        logging.info('Started platform {name}'.format(name=self.sid))

    def _start_connection(self):
        host = self.properties["db.host"]
        port = self.properties["db.port"]

        self.connection = redis.Redis(host=host, port=port, decode_responses=True)

    def stop(self):
        # TODO
        pass


#######################
### EXAMPLE
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--loglevel", default="INFO", type=str)

    args = parser.parse_args()

    # set logging
    logging.getLogger().setLevel(args.loglevel.upper())

    # create platform
    platform = Platform()

    # list sessions
    sessions = platform.get_sessions()
