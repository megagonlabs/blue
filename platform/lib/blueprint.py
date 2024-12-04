###### OS / Systems
import sys

import pydash

###### Add lib path
sys.path.append("./lib/")
sys.path.append("./lib/utils/")

######
import argparse
import logging
import uuid

###### Parsers, Formats, Utils
import re

###### Backend, Databases
import redis
from redis.commands.json.path import Path

###### Blue
from producer import Producer
from session import Session
from message import Message, MessageType, ContentType, ControlCode
from connection import PooledConnectionFactory

class Platform:
    def __init__(self, name="PLATFORM", id=None, sid=None, cid=None, prefix=None, suffix=None, properties={}):
        self.connection = None
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
            if session is not None:
                result.append(session.to_dict())
        return result

    def get_session(self, session_sid):
        session_sids = self.get_session_sids()

        if session_sid in set(session_sids):
            return Session(sid=session_sid, prefix=self.cid, properties=self.properties)
        else:
            return None

    def create_session(self, created_by=None):
        session = Session(prefix=self.cid, properties=self.properties)
        if not pydash.is_empty(created_by):
            self.set_metadata(f'users.{created_by}.sessions.owner.{session.sid}', True)
        return session

    def delete_session(self, session_sid):
        session_cid = self.cid + ":" + session_sid

        # delete session stream
        self.connection.delete(session_cid + ":STREAM")

        # delete session data, metadata
        self.connection.delete(session_cid + ":DATA")
        self.connection.delete(session_cid + ":METADATA")

        # TODO: delete more

        # TODO: remove, stop all agents

    def _send_message(self, code, params):
        message = {'code': code, 'params': params}
        self.producer.write(data=message, dtype="json", label="INSTRUCTION")

    def join_session(self, session_sid, registry, agent, properties):

        session_cid = self.cid + ":" + session_sid

        args = {}
        args["session"] = session_cid
        args["registry"] = registry
        args["agent"] = agent
        args["properties"] = properties
        self.producer.write_control(ControlCode.JOIN_SESSION, args)

    ###### METADATA RELATED
    def create_update_user(self, user):
        uid = user['uid']
        default_user_role = self.get_metadata(f'settings.default_user_role')
        if pydash.is_empty(default_user_role):
            default_user_role = 'guest'
        # create user profile with guest role if does not exist
        self.set_metadata(
            f'users.{uid}',
            {
                'uid': user['uid'],
                'role': default_user_role,
                'email': user['email'],
                'name': user['name'],
                'picture': user['picture'],
                'settings': {},
                'sessions': {"pinned": {}, "owner": {}, "member": {}},
            },
            nx=True,
        )
        self.set_metadata(f'users.{uid}.email', user['email'])
        self.set_metadata(f'users.{uid}.name', user['name'])
        self.set_metadata(f'users.{uid}.picture', user['picture'])

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
            {'users': {}, "settings": {}},
            nx=True,
        )

    def _get_metadata_namespace(self):
        return self.cid + ":METADATA"

    def set_metadata(self, key, value, nx=False):
        self.connection.json().set(self._get_metadata_namespace(), "$." + key, value, nx=nx)

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
        self.connection_factory = PooledConnectionFactory(properties=self.properties)
        self.connection = self.connection_factory.get_connection()

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
